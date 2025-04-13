import streamlit as st
import pandas as pd
from datetime import datetime
import time

from mets_stats import get_latest_mets_game, get_zero_hit_players, get_strikeout_leaders
from utils import format_date, format_game_time, get_game_location

# Set page title and configuration
st.set_page_config(
    page_title="NY Mets 0-fer Club",
    page_icon="⚾",
    layout="wide"
)

# App header
st.title("⚾ NY Mets - The 0-fer Club")
st.markdown("Tracking players without hits in the latest NY Mets game")

# Add a refresh button
col1, col2 = st.columns([4, 1])
with col2:
    refresh = st.button("Refresh Data")

# Function to load data with caching
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_game_data():
    with st.spinner("Fetching latest Mets game data..."):
        try:
            game_data = get_latest_mets_game()
            
            if not game_data:
                return None, None, None, None
            
            zero_hit_players = get_zero_hit_players(game_data)
            strikeout_leaders = get_strikeout_leaders(game_data)
            
            # Game metadata
            game_date = format_date(game_data.get('game_date', ''))
            game_time = format_game_time(game_data.get('game_datetime', ''))
            location = get_game_location(game_data)
            opponent = game_data.get('opponent', 'Unknown')
            
            # Get game result
            mets_score = game_data.get('mets_score', 0)
            opponent_score = game_data.get('opponent_score', 0)
            result = f"Mets {mets_score} - {opponent} {opponent_score}"
            
            game_info = {
                'date': game_date,
                'time': game_time,
                'location': location,
                'result': result
            }
            
            return game_data, zero_hit_players, strikeout_leaders, game_info
            
        except Exception as e:
            st.error(f"Error fetching game data: {str(e)}")
            return None, None, None, None

# Force refresh if button is clicked
if refresh:
    st.cache_data.clear()

# Load data
game_data, zero_hit_players, strikeout_leaders, game_info = load_game_data()

# Display game information
if game_info:
    st.markdown("### Latest Game Info")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"**Date:** {game_info['date']}")
        st.markdown(f"**Time:** {game_info['time']}")
    with col2:
        st.markdown(f"**Location:** {game_info['location']}")
    with col3:
        st.markdown(f"**Result:** {game_info['result']}")
    
    st.markdown("---")

    # Display the 0-fer Club
    st.markdown("## The 0-fer Club")
    
    if zero_hit_players.empty:
        st.info("All Mets players got hits in this game! The 0-fer Club is empty.")
    else:
        # Format the table
        formatted_zeros = zero_hit_players.copy()
        
        # Display the table
        st.dataframe(
            formatted_zeros,
            use_container_width=True,
            column_config={
                "Player": st.column_config.TextColumn("Player"),
                "AB": st.column_config.NumberColumn("AB"),
                "Ks": st.column_config.NumberColumn("Ks")
            }
        )
    
    # Display strikeout leaders
    st.markdown("## Strikeout Leaders")
    
    if strikeout_leaders.empty:
        st.info("No Mets players struck out in this game!")
    else:
        # Display the table
        st.dataframe(
            strikeout_leaders,
            use_container_width=True,
            column_config={
                "Player": st.column_config.TextColumn("Player"),
                "Ks": st.column_config.NumberColumn("Ks")
            }
        )
    
    # Display last updated time
    st.markdown("---")
    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
else:
    st.error("No game data available. The Mets may not have played recently, or there was an error fetching the data.")
    st.markdown("Please try again later or click the Refresh button.")
