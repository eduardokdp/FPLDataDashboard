import requests
import streamlit as st
from typing import Dict, List, Tuple, Optional, Union, Any

def filter_players(
    players_df, 
    selected_teams, 
    selected_positions, 
    price_range, 
    form_range
):
    """
    Filter players dataframe based on selection criteria
    """
    filtered_df = players_df.copy()
    
    # Filter by team
    if selected_teams:
        filtered_df = filtered_df[filtered_df['team_name'].isin(selected_teams)]
    
    # Filter by position
    if selected_positions:
        filtered_df = filtered_df[filtered_df['position'].isin(selected_positions)]
    
    # Filter by price range
    min_price, max_price = price_range
    filtered_df = filtered_df[(filtered_df['price'] >= min_price) & (filtered_df['price'] <= max_price)]
    
    # Filter by form range
    min_form, max_form = form_range
    filtered_df = filtered_df[(filtered_df['form'] >= min_form) & (filtered_df['form'] <= max_form)]
    
    return filtered_df

def get_team_logo_url(team_code: int) -> Optional[str]:
    """
    Get the URL for a team's logo based on team code
    
    Args:
        team_code: The numeric code for the team
        
    Returns:
        URL string for the team logo or None if not available
    """
    return f"https://resources.premierleague.com/premierleague/badges/t{team_code}.svg"

def display_player_image(player_id: int) -> None:
    """
    Display a player's image based on player ID.
    Instead of downloading images, we'll use placeholder icons.
    
    Args:
        player_id: The player's ID
    """
    # Sample avatar icon from Font Awesome as a placeholder
    st.markdown(f"""
        <div style='text-align: center;'>
            <i class="fas fa-user-circle" style='font-size: 70px; color: #37003c;'></i>
        </div>
    """, unsafe_allow_html=True)

def map_position_id_to_name(position_id: int) -> str:
    """
    Map position ID to position name
    
    Args:
        position_id: The numeric position ID
        
    Returns:
        Position name as a string
    """
    position_map = {
        1: "Goalkeeper",
        2: "Defender",
        3: "Midfielder",
        4: "Forward"
    }
    return position_map.get(position_id, "Unknown")

def calculate_player_value(points: int, price: float) -> float:
    """
    Calculate player value (points per million)
    
    Args:
        points: Total points
        price: Player price in millions
        
    Returns:
        Value score (points per million)
    """
    if price <= 0:
        return 0
    return points / price

def format_fixture(fixture: Dict[str, Any], team_names: Dict[int, str]) -> str:
    """
    Format a fixture into a readable string
    
    Args:
        fixture: Fixture dictionary
        team_names: Mapping of team IDs to names
        
    Returns:
        Formatted fixture string
    """
    opponent_id = fixture['opponent']
    opponent_name = team_names.get(opponent_id, f"Team {opponent_id}")
    venue = "H" if fixture['is_home'] else "A"
    difficulty = fixture['difficulty']
    return f"{opponent_name} ({venue}) - FDR: {difficulty}"
