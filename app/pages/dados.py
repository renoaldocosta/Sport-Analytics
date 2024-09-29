# app/pages/dados.py

import streamlit as st
from statsbombpy import sb # Importa a biblioteca que será utilizada para carregar os dados
import pandas as pd
from mplsoccer import Pitch,Sbopen

parser = Sbopen()

def match_data(match_id):
    return parser.event(match_id=match_id)[0]

def get_match_label(matches, match_id):
    row = matches[matches['match_id'] == match_id].iloc[0]
    return f"{row['match_date']} - {row['home_team']} x {row['away_team']}"


def plot_passes(match_id, player_name):
    
    player_filter = (match_id.type_name == 'Pass') & (match_id.player_name == player_name)
    df_pass = match_id.loc[player_filter, ['x', 'y', 'end_x', 'end_y']]
    pitch = Pitch(pitch_color='#aabb97', line_color='white',
              stripe_color='#c2d59d', stripe=False)  # optional stripes
    
    fig, ax = pitch.grid(grid_height=0.9, title_height=0.06, axis=False, endnote_height=0.04, 
                         title_space=0, endnote_space=0)
    pitch.arrows(df_pass.x, df_pass.y, df_pass.end_x, df_pass.end_y, color='white', ax=ax['pitch'])
    
    pitch.kdeplot(df_pass.x, df_pass.y, ax=ax['pitch'], alpha=0.5, shade=True, cmap='coolwarm')
    
    return fig
    


def run():
    st.title("Conhecendo os Dados")
    competitions = sb.competitions()
    competitions_names = competitions['competition_name'].unique()
    competition = st.selectbox('Selecione a competição', competitions_names)
    competition_id = competitions[competitions['competition_name'] == competition]['competition_id'].values[0]
    
    seasons = competitions[competitions['competition_name'] == competition]['season_name'].unique()
    season_name = st.selectbox('Selecione a temporada', seasons)
    season_id = competitions[(competitions['competition_name'] == competition) & (competitions['season_name'] == season_name)]['season_id'].values[0]
    
    matches = sb.matches(competition_id=competition_id, season_id=season_id)
    
    
    
    game = st.selectbox('Selecione o jogo', matches['match_id'], format_func=lambda idx: get_match_label(matches, idx))
    with st.container():
        st.markdown(f"<p style='text-align: center; color: black'>Match Details</p>", unsafe_allow_html=True)
        date = matches[matches['match_id'] == game]['match_date'].values[0]
        st.markdown(f"<h2 style='text-align: center; color: red'>{date}</h2>", unsafe_allow_html=True)
        referee = matches[matches['match_id'] == game]['referee'].values[0]
        st.markdown(f"<h3 style='text-align: center; color: blue'>{referee}</h3>", unsafe_allow_html=True)
    
    with st.container():
        left_column, right_column = st.columns(2)
        with left_column:
            st.markdown(f"<p style='text-align: center; color: black'>Home Team</p>", unsafe_allow_html=True)
            home_team = matches[matches['match_id'] == game]['home_team'].values[0]
            st.subheader(home_team)
            home_score = matches[matches['match_id'] == game]['home_score'].values[0]
            col = st.columns([1.7, 1, 1])
            col[1].metric('Gols', home_score)
            
        with right_column:
            st.markdown(f"<p style='text-align: center; color: black'>Away Team</p>", unsafe_allow_html=True)
            away_team = matches[matches['match_id'] == game]['away_team'].values[0]
            st.subheader(away_team)
            away_score = matches[matches['match_id'] == game]['away_score'].values[0]
            col = st.columns([1.7, 1, 1])
            col[1].metric('Gols', away_score)
    
    dribbles = sb.events(match_id=game, split=True, flatten_attrs=False)['dribbles'] # Pré-carregar os dados de eventos para acelerar a exibição
    st.dataframe(dribbles)
    st.dataframe(competitions[competitions['competition_name'] == competition])
    
    
    st.write('\n\n\n\n')
    
    st.subheader("Messi vs Mbappé (2022)" )
    st.write("This section will be avaiable soon.")
    
    competitions = sb.competitions()
    competitions_names = "FIFA World Cup"
    fifa_world_cup22 = sb.matches(competition_id=43, season_id=106)
    final_match_id = fifa_world_cup22[(fifa_world_cup22['home_team'] == "Argentina") & (fifa_world_cup22['away_team'] == "France")].match_id.values[0]
    final_data = match_data(final_match_id)
    
    line_ups = sb.lineups(match_id=final_match_id)
    st.write(line_ups)
    
    # Kylian Mbappé Lottin - 3009
    # Lionel Andrés Messi Cuccittini - 5503
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("Kylian Mbappé Lottin")
        #st.image("https://media.api-sports.io/football/players/3009.png", width=100)
        # busca todos jogadores: https://media.api-sports.io/football/players/
        fig_1 = plot_passes(final_data, "Kylian Mbappé Lottin")
        st.pyplot(fig_1)
    with col2:
        st.write("Lionel Andrés Messi Cuccittini")
        #st.image("https://media.api-sports.io/football/players/5503.png", width=100)
        fig_2 = plot_passes(final_data, "Lionel Andrés Messi Cuccittini")
        st.pyplot(fig_2)
        