import pandas as pd
import mlb_api as statsapi
import time
from datetime import datetime, timedelta

def get_latest_mets_game():
    """
    Fetch the latest completed NY Mets game data.
    
    Returns:
        dict: Game data including batting stats
    """
    try:
        # Mets team ID is 121
        mets_id = 121
        
        # Get current date
        today = datetime.now()
        
        # Look for games in the past 7 days
        for i in range(7):
            date = (today - timedelta(days=i)).strftime('%Y-%m-%d')
            schedule = statsapi.get_schedule(team=mets_id, date=date)
            
            # Filter for completed games
            completed_games = [game for game in schedule if game['status'] == 'Final']
            
            if completed_games:
                # Get the latest completed game
                latest_game = completed_games[0]
                game_id = latest_game['game_id']
                
                # Get detailed game data
                game_data = statsapi.boxscore_data(game_id)
                
                # Determine home/away for Mets
                is_home = latest_game['home_name'] == 'New York Mets'
                team_data_key = 'home' if is_home else 'away'
                opponent_data_key = 'away' if is_home else 'home'
                
                # Get batting data
                batting_data = game_data['teamInfo'][team_data_key]['battingOrder']
                player_stats = game_data['playerInfo']
                
                # Create a list to store player batting stats
                players = []
                
                # Process batting stats for all players
                for player_id in batting_data:
                    if str(player_id) in player_stats:
                        player = player_stats[str(player_id)]
                        
                        # Get batting stats if available
                        if 'batting' in player['stats']:
                            batting_stats = player['stats']['batting']
                            
                            player_data = {
                                'name': player['name'],
                                'ab': int(batting_stats.get('atBats', 0)),
                                'hits': int(batting_stats.get('hits', 0)),
                                'strikeouts': int(batting_stats.get('strikeOuts', 0))
                            }
                            players.append(player_data)
                
                # Get scores
                mets_score = latest_game['home_score'] if is_home else latest_game['away_score']
                opponent_score = latest_game['away_score'] if is_home else latest_game['home_score']
                
                # Extract opponent name
                opponent = latest_game['away_name'] if is_home else latest_game['home_name']
                
                # Create final result
                result = {
                    'game_id': game_id,
                    'game_date': latest_game['game_date'],
                    'game_datetime': latest_game['game_datetime'],
                    'venue': latest_game['venue_name'],
                    'is_home': is_home,
                    'mets_score': mets_score,
                    'opponent_score': opponent_score,
                    'opponent': opponent,
                    'players': players
                }
                
                return result
                
        # If no completed games found
        return None
    
    except Exception as e:
        print(f"Error fetching Mets game data: {str(e)}")
        return None

def get_zero_hit_players(game_data):
    """
    Get players who didn't get any hits in the game but had at least one at-bat.
    
    Args:
        game_data (dict): Game data from get_latest_mets_game
        
    Returns:
        DataFrame: Players with columns [Player, AB, Ks]
    """
    if not game_data or 'players' not in game_data:
        return pd.DataFrame(columns=['Player', 'AB', 'Ks'])
    
    zero_hit_players = []
    
    for player in game_data['players']:
        if player['ab'] > 0 and player['hits'] == 0:
            zero_hit_players.append({
                'Player': player['name'],
                'AB': player['ab'],
                'Ks': player['strikeouts']
            })
    
    # Convert to DataFrame and sort by AB (descending) then Ks (descending)
    df = pd.DataFrame(zero_hit_players)
    if not df.empty:
        df = df.sort_values(by=['AB', 'Ks'], ascending=[False, False])
    
    return df

def get_strikeout_leaders(game_data):
    """
    Get players ordered by most strikeouts in the game.
    
    Args:
        game_data (dict): Game data from get_latest_mets_game
        
    Returns:
        DataFrame: Players with columns [Player, Ks]
    """
    if not game_data or 'players' not in game_data:
        return pd.DataFrame(columns=['Player', 'Ks'])
    
    strikeout_players = []
    
    for player in game_data['players']:
        if player['strikeouts'] > 0:
            strikeout_players.append({
                'Player': player['name'],
                'Ks': player['strikeouts']
            })
    
    # Convert to DataFrame and sort by Ks (descending)
    df = pd.DataFrame(strikeout_players)
    if not df.empty:
        df = df.sort_values(by='Ks', ascending=False)
    
    return df
