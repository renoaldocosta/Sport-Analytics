import streamlit as st
from statsbombpy import sb
import pandas as pd
from datetime import datetime
from app.Scripts.text_functions import mkd_text_divider, mkd_text, mkd_paragraph
import flagpy as fp


def year_filter(df):
    st.write("")
    season_name = st.selectbox('Selecione a copa do mundo:', df['season_name'])
    season_id = df[df['season_name'] == season_name].season_id.values[0]
    df = df[df['season_id'] == season_id]
    
    return df, season_id

def get_match_label(matches, match_id):
    row = matches[matches['match_id'] == match_id].iloc[0]
    return f"{row['match_date']} - {row['home_team']} x {row['away_team']}"

def match_filter(df, season_id, competition_id):
    df_matches = sb.matches(competition_id=competition_id[0], season_id=season_id)
    
    match_id = st.selectbox('Selecione o jogo:', df_matches['match_id'], format_func=lambda idx: get_match_label(df_matches, idx))
    df_matches = df_matches[df_matches['match_id'] == match_id]
    return df_matches, match_id


def filter_season(df):
    with st.sidebar:
        st.subheader("Filtros")
        df, season_id = year_filter(df)
    return df , season_id 

def filter_match(df, season_id, competition_id):
    with st.sidebar:
        df_matches, match_id = match_filter(df, season_id, competition_id)
    return df_matches, match_id


def load_data():
    competitions = sb.competitions()
    df = competitions[competitions['competition_name'] == 'FIFA World Cup']
    competition_id = df['competition_id'].unique()
    return df, competition_id

def country_mapping(country):# United States
    if country.strip() == 'England':
        country = 'The United Kingdom'
    if country == 'United States':
        country = 'The United States'
    # The Netherlands
    if country == 'Netherlands':
        country = 'The Netherlands'
    return country

def country_manual_mapping(country):
    if country == 'Wales':
        home_flag = r'./app/data/Images/flags/wales.png'
        return home_flag

def get_home_team_score_flag(df_match, match_id):
    home_team = df_match[df_match['match_id'] == match_id]['home_team'].values[0]
    home_score = df_match[df_match['match_id'] == match_id]['home_score'].values[0]
    df_flags = fp.get_flag_df()
    try:
        country_corrected= country_mapping(home_team)
        home_flag = df_flags.loc[country_corrected, 'flag']
        return home_team, home_score, home_flag
    except:
        try:
            home_flag = country_manual_mapping(home_team)
            return home_team, home_score, home_flag
        except:
            return home_team, home_score, r'./app/data/Images/not_founded.png'

    
def get_away_team_score_flag(df_match, match_id):
    away_team = df_match[df_match['match_id'] == match_id]['away_team'].values[0]
    away_score = df_match[df_match['match_id'] == match_id]['away_score'].values[0]
    df_flags = fp.get_flag_df()
    try:
        country_corrected = country_mapping(away_team)
        away_flag = df_flags.loc[country_corrected, 'flag']
        return away_team, away_score, away_flag
    except:
        try:
            away_flag = country_manual_mapping(away_flag)
            return away_team, away_score, away_flag
        except:
            return away_team, away_score, r'./app/data/Images/not_founded.png'
def run():
    #st.title("Jogo da Copa do Mundo")
    df, competition_id = load_data()
    
    df, season_id = filter_season(df)
    df_match, match_id = filter_match(df, season_id, competition_id)
    
#    st.dataframe(df['country_name'].unique())
    
    
    match = df_match[df_match['match_id'] == match_id].iloc[0]
    # converte data para o formato dd/mm/yyyy
    match_date  = pd.to_datetime(match['match_date'])
    match_date = match_date.strftime('%d/%m/%Y')
    
    hora = pd.to_datetime(match['kick_off'])
    hora = hora.strftime('%H:%M')
    
    # for index, row in df_flags.iterrows():
    #     st.image(row['flag'], caption=row.name)
    #st.dataframe(df_match['home_team'].unique())
    away_team, away_score, away_flag = get_away_team_score_flag(df_match, match_id)
    home_team, home_score, home_flag = get_home_team_score_flag(df_match, match_id)
    
    
    
    referee = df_match[df_match['match_id'] == match_id]['referee'].values[0]
    
    with st.container():
        st.title(f"{match['home_team']} x {match['away_team']}")
        st.subheader(f"{match_date} - {hora}")
        
        # exibe o nome do árbitro
        st.markdown(f"<h5 style= 'color: blue'>Árbitro: {referee}</h5>", unsafe_allow_html=True)
    
        col_flags = st.columns([1,1,2,1,1])
        with col_flags[1]:
            st.image(home_flag, use_column_width=True)
        with col_flags[3]:
            st.image(away_flag, use_column_width=True)
        
        # exibe o placar
        col1, col2 = st.columns(2)
        with col1:
            
            st.markdown(f"<h3 style='color: green'>{home_team} (Casa)</h3>", unsafe_allow_html=True)
            st.markdown(f"<h1 style='color: green'>{home_score}</h1>", unsafe_allow_html=True)
        with col2:
            
            st.markdown(f"<h3 style='color: red'>{away_team} (Visitante)</h3>", unsafe_allow_html=True)
            st.markdown(f"<h1 style='color: red'>{away_score}</h1>", unsafe_allow_html=True)   
    
    st.divider()
    st.header("Informações e Detalhes")
    tab1, tab2, tab3 = st.tabs(["Escalação", "Detalhes da Partida", "Estatísticas"])
    # ========================== Escalação ==========================
    mkd_text("", level='subheader')
    home_lineup = sb.lineups(match_id=match_id)[home_team].sort_values('jersey_number')
    away_lineup = sb.lineups(match_id=match_id)[away_team].sort_values('jersey_number')
    with tab1:
    
        with st.expander("👥 Jogadores",expanded=True):
            col3 = st.columns([1,1])
            with col3[0]:
                st.markdown(f"<h3 style='color: green'>{home_team} (Casa)</h3>", unsafe_allow_html=True)
                for index, row in home_lineup.iterrows():
                    # Formatar a string com número da camisa, nome, e o apelido (se existir)
                    nickname = f" ({row['player_nickname']})" if row['player_nickname'] else ""
                    df_home = f"{row['jersey_number']} - {row['player_name']}{nickname}"
                    
                    # Exibir o resultado no Streamlit
                    st.write(df_home)
            with col3[1]:
                st.markdown(f"<h3 style='color: red'>{away_team} (Visitante)</h3>", unsafe_allow_html=True)
                for index, row in away_lineup.iterrows():
                    # Formatar a string com número da camisa, nome, e o apelido (se existir)
                    nickname = f" ({row['player_nickname']})" if row['player_nickname'] else ""
                    df_away = f"{row['jersey_number']} - {row['player_name']}{nickname}"
                    
                    # Exibir o resultado no Streamlit
                    st.write(df_away)
    
    # ========================== Detalhes da Partida ==========================
    with tab2:
        with st.expander("🏟️👔 Partida e Técnicos:", expanded=True):
            #st.subheader("Detalhes da Partida")
            st.write(f"**Estádio:** {match['stadium']}")
            # match_week
            st.write(f"**Semana:** {match['match_week']}")
            # Group Stage
            st.write(f"**Fase:** {match['competition_stage']}")
            
            st.subheader("Técnicos")
            col3 = st.columns([1,1])
            with col3[0]:
                # Tecnicos
                home_managers = df_match['home_managers'].values[0]
                st.markdown(f"<h3 style='color: green'>{home_team}</h3>", unsafe_allow_html=True)
                st.markdown(f"<h5 >{home_managers}</h5>", unsafe_allow_html=True)
            with col3[1]:
                away_managers = df_match['away_managers'].values[0]
                st.markdown(f"<h3 style='color: red'>{away_team}</h3>", unsafe_allow_html=True)
                st.markdown(f"<h5 >{away_managers}</h5>", unsafe_allow_html=True)    
    


    

    
    
    #st.write(f"**Cidade:** {match['city']}")
    #st.write(sb.lineups(match_id=match_id))
    
    st.dataframe(df)
    st.dataframe(df_match)


    #st.write(sb.matches(competition_id=43, season_id=season_id))

if __name__ == "__main__":
    run()