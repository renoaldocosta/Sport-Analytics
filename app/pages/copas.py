import streamlit as st
from statsbombpy import sb
import pandas as pd
from datetime import datetime
from app.Scripts.text_functions import mkd_text_divider, mkd_text, mkd_paragraph
import flagpy as fp




def year_filter(df):
    if 'id_index_season_name' not in st.session_state:
        st.session_state.id_index_season_name = 0
        id_index_season_name = 0
    else:
        id_index_season_name = st.session_state.id_index_season_name
    
    st.write("")
    season_options = df['season_name'].unique()
    id_index_season_name = valid_index(season_options, id_index_season_name)
    season_name = st.selectbox('Selecione a copa do mundo:', season_options, key='season_name', index=id_index_season_name)
    
    id_index_season_name = list(season_options).index(season_name)
    st.session_state.id_index_season_name = id_index_season_name
    
    season_id = df[df['season_name'] == season_name].season_id.values[0]
    df = df[df['season_id'] == season_id]
    return df, season_id


def filter_events(events):
    options_event_type = ["Todos"] + events['type'].unique().tolist()
    event_type = st.selectbox(
            "Selecione o tipo de evento", 
            options_event_type,
            key='event_type'
        )
    
    if event_type == "Todos":
        return events
        
    else:
        return events[events['type'] == event_type]


def filter_vision(visao, match_id, home_team, away_team):
    events = get_events(match_id)
    if visao == "Casa":
        events = events[events['team'] == home_team]
    elif visao == "Visitante":
        events = events[events['team'] == away_team]
    elif visao == "Geral":
        pass
    return events


        




def restart_session_state():
    st.session_state.id_index_match_id = 0


def valid_index(options, index):
    pass
    if len(options) < index:
        return 0
    else:
        return index


def match_filter(df, season_id, competition_id):
    if 'id_index_match_id' not in st.session_state:
        st.session_state.id_index_match_id = 0
        id_index_match_id = 0
    else:
        id_index_match_id = st.session_state.id_index_match_id
    
    df_matches = load_matches(competition_id=competition_id[0], season_id=season_id)
    options_match = df_matches['match_id'].unique()
    
    id_index_match_id = valid_index(options_match, id_index_match_id)
    
    # Add the 'key' parameter to store the selection in st.session_state
    match_id = st.selectbox('Selecione o jogo:', options_match,
                            format_func=lambda idx: get_match_label(df_matches, idx),
                            key='match_id',
                            index=id_index_match_id,
                            on_change=restart_session_state)
    
    id_index_match_id = list(df_matches['match_id']).index(match_id)
    st.session_state.id_index_match_id = id_index_match_id
    
    
    df_matches = df_matches[df_matches['match_id'] == match_id]
    return df_matches, match_id


def get_match_label(matches, match_id):
    row = matches[matches['match_id'] == match_id].iloc[0]
    return f"{row['match_date']} - {row['home_team']} x {row['away_team']}"

@st.cache_data
def load_matches(competition_id, season_id):
    return sb.matches(competition_id=competition_id, season_id=season_id)



@st.cache_data
def get_events(match_id):
    events = sb.events(match_id=match_id, flatten_attrs=True)
    return events

@st.cache_data
def load_data():
    competitions = sb.competitions()
    df = competitions[competitions['competition_name'] == 'FIFA World Cup']
    competition_id = df['competition_id'].unique()
    return df, competition_id

def filter_season(df):
    with st.sidebar:
        st.subheader("Filtros")
        df, season_id = year_filter(df)
    return df, season_id 

def filter_match(df, season_id, competition_id):
    with st.sidebar:
        df_matches, match_id = match_filter(df, season_id, competition_id)
    return df_matches, match_id



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
    
    
    
    try:
        referee = df_match[df_match['match_id'] == match_id]['referee'].values[0]
    except:
        referee = "Não informado"
    
    with st.container(border=True):
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
    # ========================== Escalação ==========================
    st.header("Informações e Detalhes")
    st.write("")
    tab1, tab2, tab3 = st.tabs(["Estatísticas", "Detalhes da Partida", "Escalação"])
    
    mkd_text("", level='subheader')
    home_lineup = sb.lineups(match_id=match_id)[home_team].sort_values('jersey_number')
    away_lineup = sb.lineups(match_id=match_id)[away_team].sort_values('jersey_number')
    
    # Tecnicos
    home_managers = df_match['home_managers'].values[0]
    away_managers = df_match['away_managers'].values[0]
    
    
    with tab3:
        with st.container(border=True):
            st.subheader("Jogadores")
            #with st.expander("👥 Jogadores",expanded=True):
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
    with tab2:
        with st.container(border=True):
        # ========================== Detalhes da Partida ==========================
            #with st.expander("🏟️👔 Partida e Técnicos:", expanded=True):
            st.subheader("Detalhes da Partida")
            st.write(f"**Estádio:** {match['stadium']}")
            # match_week
            st.write(f"**Semana:** {match['match_week']}")
            # Group Stage
            st.write(f"**Fase:** {match['competition_stage']}")
            
            st.subheader("Técnicos")
            col3 = st.columns([1,1])
            with col3[0]:
                st.markdown(f"<h3 style='color: green'>{home_team}</h3>", unsafe_allow_html=True)
                st.markdown(f"<h5 >{home_managers}</h5>", unsafe_allow_html=True)
            with col3[1]:
                st.markdown(f"<h3 style='color: red'>{away_team}</h3>", unsafe_allow_html=True)
                st.markdown(f"<h5 >{away_managers}</h5>", unsafe_allow_html=True)    
    with tab1:
        with st.container(border=True):
            st.subheader("Estatísticas")
            col5 = st.columns([1, 1,1])
            with col5[1]:
                visao = st.radio("", [f"Casa","Geral", "Visitante"], horizontal=True, index=1)
            
            events = filter_vision(visao, match_id, home_team, away_team)
            #col5 = 
            col4 = st.columns([1, 1, 1, 1,1,1])
            with col4[0]:
                st.metric("Passes", events['type'].value_counts().get('Pass', 0))
            with col4[4]:
                shots = events['type'].value_counts().get('Shot', 0)
                st.metric("Chutes a Gol", shots)
            with col4[5]:
                if visao == "Casa":
                    goals = home_score
                if visao == "Visitante":
                    goals = away_score
                if visao == "Geral":
                    goals = home_score + away_score
                percent_score = round((goals / shots) * 100,2)
                st.metric("Conversão(Gols)", f'{percent_score}%')
            with col4[1]:
                st.metric("Faltas", events['type'].value_counts().get('Foul Committed', 0))
            with col4[2]:
                st.metric("Dribles", events['type'].value_counts().get('Dribble', 0))
            with col4[3]:  # Add an additional column for corner kicks
                corner_passes = events[(events['type'] == 'Pass') & (events['pass_type'] == 'Corner')]
                corner_shots = events[(events['type'] == 'Shot') & (events['play_pattern'] == 'From Corner')]
                corner = len(corner_passes) + len(corner_shots)
                st.metric("Escanteios", corner)


            # Selecionar colunas principais, como jogador, time, tipo de evento e métricas específicas de cada tipo
            event_columns = [
                'type',            # Tipo de evento (Pass, Shot, Duel, etc.)
                'minute',          # Minuto do evento
                'second',          # Segundo do evento
                'team',            # Nome do time
                'player',          # Nome do jogador
                'location',        # Localização do evento no campo
                'pass_end_location',  # Fim do passe (se for um passe)
                'pass_length',     # Comprimento do passe (se for um passe)
                'pass_outcome',    # Resultado do passe (se for um passe)
                'shot_outcome',    # Resultado do chute (se for um chute)
                'shot_statsbomb_xg',  # xG do chute (se for um chute)
                'shot_technique',  # Técnica do chute (se for um chute)
                'duel_outcome',    # Resultado do duelo (se for um desarme)
            ]

            # Filtrando apenas as colunas que estão disponíveis nos eventos
            events_filtered = events[event_columns].copy()

            # Exibindo o DataFrame no Streamlit
            st.write("")
            st.subheader("Eventos")
            col6 = st.columns([1, 1, 1])
            with col6[1]:
                events_filtered = filter_events(events_filtered)
            st.dataframe(events_filtered, hide_index = True)

        # Exemplo de algumas métricas simples que podem ser calculadas a partir do DataFrame
        total_passes = len(events[events['type'] == 'Pass'])
        total_shots = len(events[events['type'] == 'Shot'])
        total_tackles = len(events[(events['type'] == 'Duel') & (events['duel_type'] == 'Tackle')])

        # Exibindo métricas relacionadas aos eventos
        st.metric("Total de Passes", total_passes)
        st.metric("Total de Finalizações", total_shots)
        st.metric("Total de Desarmes", total_tackles)

    

        st.dataframe(events)

    
    #st.write(f"**Cidade:** {match['city']}")
    #st.write(sb.lineups(match_id=match_id))
    
    st.dataframe(df)
    st.dataframe(df_match)


    #st.write(sb.matches(competition_id=43, season_id=season_id))





if __name__ == "__main__":
    run()