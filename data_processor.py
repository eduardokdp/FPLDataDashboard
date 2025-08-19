import pandas as pd
import numpy as np
from fpl_api import get_positions_data, get_upcoming_fixtures, get_next_gameweek

def get_positions_dict():
    """
    Create a dictionary mapping position IDs to position names
    """
    positions_data = get_positions_data()
    return {pos['id']: pos['singular_name'] for pos in positions_data}

def get_team_name_mapping(teams_data):
    """
    Create mapping of team IDs to team names
    """
    return {team['id']: team['name'] for team in teams_data}

def get_team_code_mapping(teams_data):
    """
    Create mapping of team IDs to team codes (used for images)
    """
    return {team['id']: team['code'] for team in teams_data}

def process_player_data(players_data, teams_data, fixtures_data):
    """
    Process raw player data to add additional useful information
    """
    positions_dict = get_positions_dict()
    team_names = get_team_name_mapping(teams_data)
    team_codes = get_team_code_mapping(teams_data)
    
    next_gameweek = get_next_gameweek()
    
    processed_players = []
    
    for player in players_data:
        if player['status'] in ['u', 'n', 'i'] or player['minutes'] == 0:
            continue
            
        price = player['now_cost'] / 10
        
        position = positions_dict.get(player['element_type'], 'Unknown')
        
        team_id = player['team']
        team_name = team_names.get(team_id, 'Unknown')
        team_code = team_codes.get(team_id, 0)
        
        upcoming_fixtures = get_upcoming_fixtures(team_id, next_n=3)
        
        if upcoming_fixtures:
            avg_difficulty = sum(f['difficulty'] for f in upcoming_fixtures) / len(upcoming_fixtures)
        else:
            avg_difficulty = 3  
        
        processed_player = {
            'id': player['id'],
            'code': player['code'],
            'name': player['web_name'],
            'full_name': f"{player['first_name']} {player['second_name']}",
            'team_id': team_id,
            'team_name': team_name,
            'team_code': team_code,
            'position_id': player['element_type'],
            'position': position,
            'price': price,
            'form': float(player['form'] or 0),
            'points_per_game': float(player['points_per_game'] or 0),
            'total_points': player['total_points'],
            'minutes': player['minutes'],
            'goals_scored': player['goals_scored'],
            'assists': player['assists'],
            'clean_sheets': player['clean_sheets'],
            'goals_conceded': player['goals_conceded'],
            'own_goals': player['own_goals'],
            'penalties_saved': player['penalties_saved'],
            'penalties_missed': player['penalties_missed'],
            'yellow_cards': player['yellow_cards'],
            'red_cards': player['red_cards'],
            'saves': player['saves'],
            'bonus': player['bonus'],
            'bps': player['bps'],
            'influence': float(player['influence'] or 0),
            'creativity': float(player['creativity'] or 0),
            'threat': float(player['threat'] or 0),
            'ict_index': float(player['ict_index'] or 0),
            'upcoming_fixtures': upcoming_fixtures,
            'avg_fixture_difficulty': avg_difficulty,
            'selected_by_percent': float(player['selected_by_percent'] or 0),
        }
        
        processed_players.append(processed_player)
    
    return processed_players

def prepare_features_for_prediction(processed_data):
    """
    Prepare features for the prediction model
    """
    features = []
    
    for player in processed_data:
        player_features = [
            player['price'],
            player['form'],
            player['points_per_game'],
            player['minutes'],
            player['goals_scored'],
            player['assists'],
            player['clean_sheets'],
            player['goals_conceded'],
            player['yellow_cards'],
            player['red_cards'],
            player['influence'],
            player['creativity'],
            player['threat'],
            player['ict_index'],
            player['avg_fixture_difficulty'],
            1 if player['position'] == 'Goalkeeper' else 0,
            1 if player['position'] == 'Defender' else 0,
            1 if player['position'] == 'Midfielder' else 0,
            1 if player['position'] == 'Forward' else 0,
        ]
        features.append(player_features)
    
    return np.array(features)
