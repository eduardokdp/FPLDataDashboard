import requests
import pandas as pd
import time
import json
import streamlit as st

# Base URLs for FPL API
BASE_URL = "https://fantasy.premierleague.com/api/"
BOOTSTRAP_URL = f"{BASE_URL}bootstrap-static/"
FIXTURES_URL = f"{BASE_URL}fixtures/"
PLAYER_HISTORY_URL = f"{BASE_URL}element-summary/"

@st.cache_data(ttl=3600) 
def get_bootstrap_data():
    """
    Get the main FPL bootstrap data including players, teams, and game rules
    """
    try:
        response = requests.get(BOOTSTRAP_URL)
        response.raise_for_status()  
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching bootstrap data: {str(e)}")
        return None

@st.cache_data(ttl=3600)
def get_players_data():
    """
    Get all player data from the FPL API
    """
    bootstrap_data = get_bootstrap_data()
    if bootstrap_data:
        return bootstrap_data.get('elements', [])
    return []

@st.cache_data(ttl=3600)
def get_teams_data():
    """
    Get all teams data from the FPL API
    """
    bootstrap_data = get_bootstrap_data()
    if bootstrap_data:
        return bootstrap_data.get('teams', [])
    return []

@st.cache_data(ttl=3600)
def get_positions_data():
    """
    Get position/element_type data from the FPL API
    """
    bootstrap_data = get_bootstrap_data()
    if bootstrap_data:
        return bootstrap_data.get('element_types', [])
    return []

@st.cache_data(ttl=3600)
def get_fixtures_data():
    """
    Get fixture data for the season
    """
    try:
        response = requests.get(FIXTURES_URL)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching fixtures data: {str(e)}")
        return []

@st.cache_data(ttl=3600)
def get_player_history(player_id):
    """
    Get detailed history data for a specific player
    """
    try:
        url = f"{PLAYER_HISTORY_URL}{player_id}/"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.warning(f"Error fetching player history for player {player_id}: {str(e)}")
        return None

@st.cache_data(ttl=3600)
def get_current_gameweek():
    """
    Determine the current gameweek from the API data
    """
    bootstrap_data = get_bootstrap_data()
    if not bootstrap_data:
        return 1
    
    events = bootstrap_data.get('events', [])
    for event in events:
        if event.get('is_current', False):
            return event.get('id')
    
    for event in events:
        if event.get('is_next', False):
            return event.get('id') - 1
    
    return 1

@st.cache_data(ttl=3600)
def get_next_gameweek():
    """
    Determine the next gameweek from the API data
    """
    bootstrap_data = get_bootstrap_data()
    if not bootstrap_data:
        return 1
    
    events = bootstrap_data.get('events', [])
    for event in events:
        if event.get('is_next', False):
            return event.get('id')
    
    current_gw = get_current_gameweek()
    return min(current_gw + 1, 38)  

@st.cache_data(ttl=3600)
def get_team_difficulty_mapping():
    """
    Create a mapping of team ID to their FDR (Fixture Difficulty Rating)
    """
    teams_data = get_teams_data()
    return {team['id']: team['strength'] for team in teams_data}

@st.cache_data(ttl=3600)
def get_upcoming_fixtures(team_id, next_n=3):
    """
    Get upcoming fixtures for a specific team
    """
    current_gw = get_current_gameweek()
    next_gw = get_next_gameweek()
    
    fixtures = get_fixtures_data()
    team_fixtures = []
    
    for fixture in fixtures:
        gameweek = fixture.get('event')
        if not gameweek or gameweek < next_gw:
            continue
        
        if fixture.get('team_h') == team_id:
            team_fixtures.append({
                'gameweek': gameweek,
                'is_home': True,
                'opponent': fixture.get('team_a'),
                'difficulty': fixture.get('team_h_difficulty')
            })
        elif fixture.get('team_a') == team_id:
            team_fixtures.append({
                'gameweek': gameweek,
                'is_home': False,
                'opponent': fixture.get('team_h'),
                'difficulty': fixture.get('team_a_difficulty')
            })
    
    team_fixtures.sort(key=lambda x: x['gameweek'])
    return team_fixtures[:next_n]
