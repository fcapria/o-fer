import requests
import json
from datetime import datetime, timedelta
import time

# Base URL for MLB Stats API
MLB_API_URL = "https://statsapi.mlb.com/api"

def get_schedule(team=None, date=None):
    """
    Get MLB games schedule for a team on a specific date.
    
    Args:
        team (int): Team ID (e.g., 121 for NY Mets)
        date (str): Date in format 'YYYY-MM-DD'
        
    Returns:
        list: List of games
    """
    endpoint = f"{MLB_API_URL}/v1/schedule"
    params = {
        'sportId': 1,  # MLB
        'hydrate': 'team',
    }
    
    if team:
        params['teamId'] = team
    
    if date:
        params['date'] = date
    
    try:
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract games from the response
        games = []
        if 'dates' in data and data['dates']:
            for date_data in data['dates']:
                if 'games' in date_data:
                    for game in date_data['games']:
                        game_info = {
                            'game_id': game['gamePk'],
                            'game_date': date,
                            'game_datetime': game.get('gameDate', ''),
                            'status': game.get('status', {}).get('detailedState', ''),
                            'home_name': game.get('teams', {}).get('home', {}).get('team', {}).get('name', ''),
                            'away_name': game.get('teams', {}).get('away', {}).get('team', {}).get('name', ''),
                            'home_score': game.get('teams', {}).get('home', {}).get('score', 0),
                            'away_score': game.get('teams', {}).get('away', {}).get('score', 0),
                            'venue_name': game.get('venue', {}).get('name', '')
                        }
                        games.append(game_info)
        
        return games
    
    except Exception as e:
        print(f"Error fetching schedule: {str(e)}")
        return []

def boxscore_data(game_id):
    """
    Get detailed boxscore data for a specific game.
    
    Args:
        game_id (int): MLB Game ID
        
    Returns:
        dict: Boxscore data including player stats
    """
    endpoint = f"{MLB_API_URL}/v1/game/{game_id}/boxscore"
    
    try:
        response = requests.get(endpoint)
        response.raise_for_status()
        
        data = response.json()
        
        # Process and transform the boxscore data
        boxscore = {
            'teamInfo': {
                'home': {
                    'battingOrder': []
                },
                'away': {
                    'battingOrder': []
                }
            },
            'playerInfo': {}
        }
        
        # Home team batting order
        if 'teams' in data and 'home' in data['teams']:
            home_team = data['teams']['home']
            if 'batters' in home_team:
                boxscore['teamInfo']['home']['battingOrder'] = home_team['batters']
        
        # Away team batting order
        if 'teams' in data and 'away' in data['teams']:
            away_team = data['teams']['away']
            if 'batters' in away_team:
                boxscore['teamInfo']['away']['battingOrder'] = away_team['batters']
        
        # Player info and stats
        if 'teams' in data:
            for team_side in ['home', 'away']:
                if team_side in data['teams']:
                    team = data['teams'][team_side]
                    if 'players' in team:
                        for player_id, player_data in team['players'].items():
                            player_id_num = player_id.replace('ID', '')
                            
                            player_info = {
                                'name': player_data.get('person', {}).get('fullName', ''),
                                'stats': {
                                    'batting': {}
                                }
                            }
                            
                            # Get batting stats
                            if 'stats' in player_data and 'batting' in player_data['stats']:
                                batting_stats = player_data['stats']['batting']
                                player_info['stats']['batting'] = {
                                    'atBats': batting_stats.get('atBats', 0),
                                    'hits': batting_stats.get('hits', 0),
                                    'strikeOuts': batting_stats.get('strikeOuts', 0)
                                }
                            
                            boxscore['playerInfo'][player_id_num] = player_info
        
        return boxscore
    
    except Exception as e:
        print(f"Error fetching boxscore data: {str(e)}")
        return {
            'teamInfo': {'home': {'battingOrder': []}, 'away': {'battingOrder': []}},
            'playerInfo': {}
        }