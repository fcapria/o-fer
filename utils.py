from datetime import datetime

def format_date(date_str):
    """
    Format the game date string to a more readable format.
    
    Args:
        date_str (str): Date string in 'YYYY-MM-DD' format
        
    Returns:
        str: Formatted date string like 'Monday, January 1, 2023'
    """
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.strftime('%A, %B %d, %Y')
    except ValueError:
        return date_str

def format_game_time(datetime_str):
    """
    Format the game datetime string to extract just the time.
    
    Args:
        datetime_str (str): Datetime string
        
    Returns:
        str: Formatted time string
    """
    try:
        # MLB API datetime format is like "2023-08-01T19:10:00Z"
        datetime_obj = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%SZ')
        # Convert to Eastern Time (MLB games are typically listed in ET)
        # Note: This is a simple approximation - proper timezone conversion would require pytz
        et_hour = (datetime_obj.hour - 5) % 24  # Simple UTC to ET conversion
        return datetime_obj.strftime(f'{et_hour}:%M PM ET')
    except ValueError:
        return datetime_str

def get_game_location(game_data):
    """
    Get the formatted location of the game.
    
    Args:
        game_data (dict): Game data dictionary
        
    Returns:
        str: Formatted location
    """
    venue = game_data.get('venue', 'Unknown Venue')
    
    if game_data.get('is_home', False):
        return f"{venue} (Home)"
    else:
        return f"{venue} (Away)"
