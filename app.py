import streamlit as st
import pandas as pd

from fpl_api import get_players_data, get_teams_data, get_fixtures_data, get_next_gameweek
from data_processor import process_player_data, get_positions_dict
from visualization import plot_player_history, plot_form_vs_price, plot_team_strength_comparison
from utils import filter_players, get_team_logo_url, get_player_image_url

st.set_page_config(
    page_title="FPL Info Dashboard",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Fantasy Premier League Info Dashboard")
st.markdown("Track player performance stats and make informed FPL decisions.")

with st.spinner("Loading FPL data..."):
    try:
        players_data = get_players_data()
        teams_data = get_teams_data()
        fixtures_data = get_fixtures_data()
        next_gameweek = get_next_gameweek()
        
        positions_dict = get_positions_dict()
        processed_data = process_player_data(players_data, teams_data, fixtures_data)
        
        players_df = pd.DataFrame(processed_data)
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.stop()

st.sidebar.header("Filter Players")

all_teams = sorted(players_df['team_name'].unique())
team_options = all_teams
selected_team_option = st.sidebar.selectbox("Select Team", team_options, index=0)

selected_teams = all_teams if selected_team_option == "All Teams" else [selected_team_option]

all_positions = sorted(players_df['position'].unique())
position_options = ["All Positions"] + all_positions
selected_position_option = st.sidebar.selectbox("Select Position", position_options, index=0)

selected_positions = all_positions if selected_position_option == "All Positions" else [selected_position_option]


plot_option = st.sidebar.selectbox(
    "Select plot to display:",
    ("Price vs Form", "Team Strength Comparison")
)

min_price = float(players_df['price'].min())
max_price = float(players_df['price'].max())
price_range = st.sidebar.slider("Price Range (£M)", min_price, max_price, (min_price, max_price), 0.1)

min_form = float(players_df['form'].min())
max_form = float(players_df['form'].max())
form_range = st.sidebar.slider("Form Range", min_form, max_form, (min_form, max_form), 0.1)

filtered_df = filter_players(
    players_df, 
    selected_teams, 
    selected_positions, 
    price_range, 
    form_range
)

sort_by = st.sidebar.selectbox(
    "Sort players by",
    ["Price", "Form", "Total Points", "Minutes", "Goals", "Assists"],
    index=0
)

sort_dict = {
    "Form": "form",
    "Price": "price",
    "Total Points": "total_points",
    "Minutes": "minutes",
    "Goals": "goals_scored",
    "Assists": "assists"
}

ascending = st.sidebar.checkbox("Ascending order", value=False)


filtered_df = filtered_df.sort_values(by=sort_dict[sort_by], ascending=ascending)

search_term = st.sidebar.text_input("Search player by name")
if search_term:
    filtered_df = filtered_df[filtered_df['name'].str.contains(search_term, case=False)]

team_header = f" - {selected_team_option}" if selected_team_option != "All Teams" else ""
position_header = f" - {selected_position_option}" if selected_position_option != "All Positions" else ""
st.header(f"Player Stats for Gameweek {next_gameweek}{team_header}{position_header}")

st.subheader(f"Showing {len(filtered_df)} players")

if plot_option == "Price vs Form":
    form_price_fig = plot_form_vs_price(filtered_df)
    st.plotly_chart(form_price_fig, use_container_width=True)

elif plot_option == "Team Strength Comparison":
    teams_data = get_teams_data() 
    team_strength_fig = plot_team_strength_comparison(teams_data)
    st.plotly_chart(team_strength_fig, use_container_width=True)


cols_per_row = 3
num_players = len(filtered_df)
num_rows = (num_players + cols_per_row - 1) // cols_per_row 

# Wrap the whole player section in a single expander
with st.expander("Show Player Cards"):
    cols_per_row = 4
    num_players = len(filtered_df)
    num_rows = (num_players + cols_per_row - 1) // cols_per_row 

    for row in range(num_rows):
        cols = st.columns(cols_per_row)
        for col_idx in range(cols_per_row):
            player_idx = row * cols_per_row + col_idx
            if player_idx < num_players:
                player = filtered_df.iloc[player_idx]
                with cols[col_idx]:
                    with st.container():
                        st.markdown(f"""
                        <div style='
                            border: 1px solid #e1e1e1;
                            border-radius: 5px;
                            padding: 10px;
                            margin-bottom: 10px;
                            background-color: white;
                        '>
                            <div style='text-align: center;'>
                                <h3>{player['name']}</h3>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        col1, col2 = st.columns([1, 2])

                        with col1:
                            player_img = get_player_image_url(player['code'])
                            st.image(player_img, width=50)

                        with col2:
                            st.markdown(f"**Team:** {player['team_name']}")
                            st.markdown(f"**Position:** {player['position']}")
                            st.markdown(f"**Price:** £{player['price']}M")

                            form_value = float(player['form'])
                            form_color = (
                                "green" if form_value > 6.0 else
                                "orange" if form_value > 4.0 else
                                "red"
                            )
                            st.markdown(f"**Form:** <span style='color:{form_color};'>{player['form']}</span>", unsafe_allow_html=True)

                            total_points = player['total_points']
                            points_color = (
                                "green" if total_points > 150 else
                                "orange" if total_points > 100 else
                                "gray"
                            )
                            st.markdown(f"**Total Points:** <span style='color:{points_color};'>{total_points}</span>", unsafe_allow_html=True)

                            if player['goals_scored'] > 0 or player['assists'] > 0:
                                st.markdown(f"**G/A:** {player['goals_scored']}/{player['assists']}")

expander = st.container()
if player['goals_scored'] > 0 or player['assists'] > 0:
    st.markdown(f"**G/A:** {player['goals_scored']}/{player['assists']}")





st.markdown("---")
st.markdown("Data sourced from the official Fantasy Premier League API.")
st.info("Player statistics are based on official FPL data. Use this information to make better informed FPL decisions.")
