import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import streamlit as st
from fpl_api import get_player_history

def plot_player_history(player_id):
    """
    Plot a player's historical performance
    
    Args:
        player_id: Player's FPL ID
        
    Returns:
        Plotly figure object
    """
    history_data = get_player_history(player_id)
    
    if not history_data or 'history' not in history_data or not history_data['history']:
        fig = go.Figure()
        fig.update_layout(
            title="No historical data available",
            xaxis_title="Gameweek",
            yaxis_title="Points"
        )
        return fig
    
    history_df = pd.DataFrame(history_data['history'])
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=history_df['round'],
        y=history_df['total_points'],
        mode='lines+markers',
        name='Points',
        line=dict(color='#37003c', width=3),
        marker=dict(size=8, color='#37003c')
    ))
    
    fig.add_trace(go.Scatter(
        x=history_df['round'],
        y=history_df['minutes'],
        mode='lines',
        name='Minutes',
        line=dict(color='#00ff87', width=2, dash='dash'),
        yaxis='y2'
    ))
    
    fig.update_layout(
        title="Player Performance by Gameweek",
        xaxis_title="Gameweek",
        yaxis=dict(
            title="Points",
            title_font=dict(color='#37003c'),
            tickfont=dict(color='#37003c')
        ),
        yaxis2=dict(
            title="Minutes",
            title_font=dict(color='#00ff87'),
            tickfont=dict(color='#00ff87'),
            anchor="x",
            overlaying="y",
            side="right",
            range=[0, 90]
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        height=300,
        margin=dict(l=20, r=20, t=40, b=20),
        hovermode="x"
    )
    
    fig.update_layout(
        xaxis=dict(
            rangeslider=dict(visible=True),
            type="linear"
        )
    )
    
    return fig

def plot_form_vs_price(players_df):
    """
    Create a scatter plot of player form vs price, with total points as size
    
    Args:
        players_df: DataFrame of player data
        
    Returns:
        Plotly figure object
    """
    df = players_df.copy()
    
    position_colors = {
        'Goalkeeper': '#FFC107',
        'Defender': '#2196F3',
        'Midfielder': '#4CAF50',
        'Forward': '#F44336'
    }
    
    fig = px.scatter(
        df,
        x='price',
        y='total_points',
        size='total_points',
        color='position',
        hover_name='name',
        size_max=40,
        color_discrete_map=position_colors,
        labels={
            'price': 'Price (£M)',
            'form': 'Form',
            'total_points': 'Total Points',
            'position': 'Position'
        },
        title='Player Total Points vs Price'
    )
    
    fig.update_traces(
        textposition='top center',
        textfont=dict(size=10),
        marker=dict(opacity=0.8)
    )
    
    fig.update_layout(
        xaxis=dict(title='Price (£M)', gridcolor='rgba(0,0,0,0.1)'),
        yaxis=dict(title='Total Points', gridcolor='rgba(0,0,0,0.1)'),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        plot_bgcolor='rgba(0,0,0,0.02)',
        hovermode='closest',
        height=500
    )
    
    return fig

def plot_team_strength_comparison(teams_data):
    """
    Create a bar chart comparing team strengths
    
    Args:
        teams_data: List of team data from FPL API
        
    Returns:
        Plotly figure object
    """
    teams_df = pd.DataFrame(teams_data)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=teams_df['name'],
        y=teams_df['strength_attack_home'],
        name='Attack (Home)',
        marker_color='#0074d4'
    ))
    
    fig.add_trace(go.Bar(
        x=teams_df['name'],
        y=teams_df['strength_attack_away'],
        name='Attack (Away)',
        marker_color='#0027d4'
    ))
    
    fig.add_trace(go.Bar(
        x=teams_df['name'],
        y=teams_df['strength_defence_home'],
        name='Defense (Home)',
        marker_color='#0074d4',
        opacity=0.6
    ))
    
    fig.add_trace(go.Bar(
        x=teams_df['name'],
        y=teams_df['strength_defence_away'],
        name='Defense (Away)',
        marker_color='#0027d4',
        opacity=0.6
    ))
    
    fig.update_layout(
        title='Team Strength Comparison',
        xaxis_title='Team',
        yaxis_title='Strength Rating',
        barmode='group',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        height=500
    )
    
    return fig