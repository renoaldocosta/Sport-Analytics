import streamlit as st
from statsbombpy import sb
import pandas as pd
from datetime import datetime
from app.Scripts.text_functions import mkd_text_divider, mkd_text, mkd_paragraph
import flagpy as fp
from mplsoccer import Pitch,Sbopen

parser = Sbopen()

def match_data(match_id):
    return parser.event(match_id=match_id)[0]

def plot_passes(match_id, player_name, type='Pass'):
    
    player_filter = (match_id.type_name == type) & (match_id.player_name == player_name)
    df_pass = match_id.loc[player_filter, ['x', 'y', 'end_x', 'end_y']]
    pitch = Pitch(pitch_color='#aabb97', line_color='white',
              stripe_color='#c2d59d', stripe=False)  # optional stripes
    
    fig, ax = pitch.grid(grid_height=0.9, title_height=0.06, axis=False, endnote_height=0.04, 
                         title_space=0, endnote_space=0)
    pitch.arrows(df_pass.x, df_pass.y, df_pass.end_x, df_pass.end_y, color='white', ax=ax['pitch'])
    
    pitch.kdeplot(df_pass.x, df_pass.y, ax=ax['pitch'], alpha=0.5, shade=True, cmap='coolwarm')
    
    return fig

def year_filter(df):
    if 'id_index_season_name' not in st.session_state:
        st.session_state.clear()
        st.session_state.id_index_season_name = 0
        id_index_season_name = 0
    else:
        id_index_season_name = st.session_state.id_index_season_name
    
    st.write("")
    season_options = df['season_name'].unique()
    id_index_season_name = valid_index(season_options, id_index_season_name)
    season_name = st.selectbox('Selecione a copa do mundo:', season_options, key='season_name', index=id_index_season_name, on_change=restart_session_state('season_name'))
    
    id_index_season_name = list(season_options).index(season_name)
    st.session_state.id_index_season_name = id_index_season_name
    
    season_id = df[df['season_name'] == season_name].season_id.values[0]
    df = df[df['season_id'] == season_id]
    return df, season_id


def filter_events(events):
    if 'id_index_event_type' not in st.session_state:
        st.session_state.id_index_event_type = 0
        id_index_event_type = 0
    else:
        id_index_event_type = st.session_state.id_index_event_type
    
    options_event_type = ["Todos"] + events['type'].unique().tolist()
    id_index_event_type = valid_index(options_event_type, id_index_event_type)
    event_type = st.selectbox(
            "Selecione o tipo de evento", 
            options_event_type,
            index=id_index_event_type,
        )
    id_index_event_type = options_event_type.index(event_type)
    st.session_state.id_index_event_type = id_index_event_type
    
    if event_type == "Todos":
        return events, event_type
        
    else:
        return events[events['type'] == event_type], event_type

def filter_players(events, todos=True):
    if 'id_index_player' not in st.session_state:
        st.session_state.id_index_player = 0
        id_index_player = 0
    else:
        id_index_player = st.session_state.id_index_player
    if todos:
        options_player = ["Todos"] + events['player'].unique().tolist()
    else:
        options_player = events['player'].unique().tolist()
    # remove nan values
    options_player = [x for x in options_player if str(x) != 'nan']
    id_index_player = valid_index(options_player, id_index_player)
    player = st.selectbox(
            "Selecione o jogador", 
            options_player,
            index=id_index_player,
        )
    
    id_index_player = options_player.index(player)
    st.session_state.id_index_player = id_index_player
    
    if player == "Todos":
        return events, player
        
    else:
        return events[events['player'] == player], player


def filter_vision(visao, match_id, home_team, away_team):
    events = get_events(match_id)
    if visao == "Casa":
        events = events[events['team'] == home_team]
    elif visao == "Visitante":
        events = events[events['team'] == away_team]
    elif visao == "Geral":
        pass
    return events





def restart_session_state(nivel):
    if nivel == "event_type":
        try:
            del st.session_state.id_index_player
        except:
            pass
    if nivel == "season_name":
        try:
            del st.session_state.id_index_match_id
            del st.session_state.id_index_event_type
            del st.session_state.id_index_player
        except:
            pass


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
                            index=id_index_match_id
                            )
    
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
    
    # Selecionar colunas principais, como jogador, time, tipo de evento e métricas específicas de cada tipo
    event_columns = [
        'minute',          # Minuto do evento
        'second',          # Segundo do evento
        'team',            # Nome do time
        'type',            # Tipo de evento (Pass, Shot, Duel, etc.)
        'position',        # Posição do jogador no campo
        'player',          # Nome do jogador
        'pass_body_part',  # Parte do corpo usada para o passe (se for um passe)
        'pass_recipient',  # Nome do jogador que recebeu o passe (se for um passe)
        'pass_height',     # Altura do passe (se for um passe)
        'pass_length',     # Comprimento do passe (se for um passe)
        'pass_outcome',    # Resultado do passe (se for um passe)
        'under_pressure',  # Se o jogador estava sob pressão
        'location',        # Localização do evento no campo
        'pass_end_location',  # Fim do passe (se for um passe)
        'shot_outcome',    # Resultado do chute (se for um chute)
        'shot_statsbomb_xg',  # xG do chute (se for um chute)
        'shot_technique',  # Técnica do chute (se for um chute)
        'duel_outcome',    # Resultado do duelo (se for um desarme)
    ]
    
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
    tab1, tab2, tab3, tab4 = st.tabs(["Estatísticas da Partida", "Detalhes da Partida", "Escalação", "Detalhes do Jogador"])
    
    mkd_text("", level='subheader')
    home_lineup = sb.lineups(match_id=match_id)[home_team].sort_values('jersey_number')
    away_lineup = sb.lineups(match_id=match_id)[away_team].sort_values('jersey_number')
    lineups = sb.lineups(match_id=match_id)
    
    
    #Substitutions = lineups[]
    # Tecnicos
    home_managers = df_match['home_managers'].values[0]
    away_managers = df_match['away_managers'].values[0]
    
    with tab1:
        with st.container(border=True):
            col7 = st.columns([1,1,1])
            with col7[1]:
                vision_options = ["Casa", "Visitante"]
                visao = st.radio("Selecionar jogador da seleção:", vision_options, horizontal=True, index=0, key='visao_player')
                events = filter_vision(visao, match_id, home_team, away_team)
                lineups, yellow_cards, red_cards = lineups_metrics(lineups, visao, home_lineup, away_lineup)
                events, player = filter_players(events, todos=False)
                position = events['position'].value_counts().idxmax()
                events, event_type  = filter_events(events)
            events = events[event_columns]
            # Metricas passes
            passes = events['type'].value_counts().get('Pass', 0)
            passes_completos = passes - events['pass_outcome'].value_counts().get('Incomplete', 0)
            chutes_a_gol = events['type'].value_counts().get('Shot', 0)
            gols = events['shot_outcome'].value_counts().get('Goal', 0)
            
            percent_passes = percent(passes_completos, passes)
            percent_score = percent(gols, chutes_a_gol)
            
            
            col8 = st.columns([1,2,1])
            with col8[1]:
                final_data = match_data(match_id)
                fig = plot_passes(final_data, player, event_type)
                st.subheader(f"Mapa ({event_type})")
                st.pyplot(fig)
            
            st.subheader(f"{player} - ({position})")
            
            col6 = st.columns([1, 1, 1,1,1,1])
            
            with col6[0]:
                st.metric("Passes", passes)
            with col6[1]:
                st.metric("Passes Sucedidos", passes_completos)
            with col6[2]:
                st.metric("Precisão de Passe", f'{percent_passes}%')
            with col6[3]:
                st.metric("Chutes a Gol", chutes_a_gol)
            with col6[4]:
                st.metric("Gols", gols)
            with col6[5]:
                st.metric("Conversão(Gols)", f'{percent_score}%')
            st.dataframe(events)
            
        
    
    with tab3:
        with st.container(border=True):
            st.subheader("Técnicos")
            col3 = st.columns([1,1])
            with col3[0]:
                st.markdown(f"<h3 style='color: green'>{home_team}</h3>", unsafe_allow_html=True)
                st.markdown(f"<h5 >{home_managers}</h5>", unsafe_allow_html=True)
            with col3[1]:
                st.markdown(f"<h3 style='color: red'>{away_team}</h3>", unsafe_allow_html=True)
                st.markdown(f"<h5 >{away_managers}</h5>", unsafe_allow_html=True)    
            st.divider()
            st.subheader("Jogadores")
            #with st.expander("👥 Jogadores",expanded=True):
            col3 = st.columns([1,1])
            with col3[0]:
                st.markdown(f"<h3 style='color: green'>{home_team} (Casa)</h3>", unsafe_allow_html=True)
                with st.container(border=True):
                    for index, row in home_lineup.iterrows():
                        # Formatar a string com número da camisa, nome, e o apelido (se existir)
                        nickname = f" ({row['player_nickname']})" if row['player_nickname'] else ""
                        df_home = f"{row['jersey_number']} - {row['player_name']}{nickname}"
                        
                        # Exibir o resultado no Streamlit
                        st.write(df_home)
                st.dataframe(home_lineup)
            with col3[1]:
                st.markdown(f"<h3 style='color: red'>{away_team} (Visitante)</h3>", unsafe_allow_html=True)
                with st.container(border=True):
                    for index, row in away_lineup.iterrows():
                        # Formatar a string com número da camisa, nome, e o apelido (se existir)
                        nickname = f" ({row['player_nickname']})" if row['player_nickname'] else ""
                        df_away = f"{row['jersey_number']} - {row['player_name']}{nickname}"
                        
                        # Exibir o resultado no Streamlit
                        st.write(df_away)
                st.dataframe(away_lineup)
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
            
            
    with tab4:
        with st.container(border=True):
            
            st.subheader("Métricas")
            col5 = st.columns([1, 1,1])
            with col5[1]:
                visao = st.radio("", [f"Casa","Geral", "Visitante"], horizontal=True, index=1)
            # Processar os lineups
            lineups, yellow_cards, red_cards = lineups_metrics(lineups, visao, home_lineup, away_lineup)
            events = filter_vision(visao, match_id, home_team, away_team)
            #col5 = 
            col4 = st.columns([1, 1, 1, 1,1,1])
            with col4[0]:
                st.metric("Passes", events['type'].value_counts().get('Pass', 0))
                st.metric("Cartão Amarelo", yellow_cards)
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
                st.metric("Cartão Vermelho", red_cards)
            with col4[2]:
                st.metric("Dribles", events['type'].value_counts().get('Dribble', 0))
            with col4[3]:  # Add an additional column for corner kicks
                corner_passes = events[(events['type'] == 'Pass') & (events['pass_type'] == 'Corner')]
                corner_shots = events[(events['type'] == 'Shot') & (events['play_pattern'] == 'From Corner')]
                corner = len(corner_passes) + len(corner_shots)
                st.metric("Escanteios", corner)


            

            # Filtrando apenas as colunas que estão disponíveis nos eventos
            events_filtered = events[event_columns].copy()

            # Exibindo o DataFrame no Streamlit
            st.write("")
            st.subheader("Eventos da Partida")
            col6 = st.columns([1, 1, 1])
            with col6[0]:
                events_filtered, event_type = filter_events(events_filtered)
            with col6[1]:
                players_filtered, player = filter_players(events_filtered)
                
            
            st.dataframe(players_filtered, hide_index = True)
            download_df(players_filtered)

def percent(value, total):
    if total == 0:
        return 0
    else:
        return round((value / total) * 100,2)

    #st.write(sb.matches(competition_id=43, season_id=season_id))
@st.cache_data
def lineups_metrics(lineups, visao, home_lineup, away_lineup):
    if "Casa" in visao:
        lineups = process_lineup(home_lineup)
        
    elif "Visitante" in visao:
        lineups = process_lineup(away_lineup)
    elif visao == "Geral":
        home_lineup = process_lineup(home_lineup)
        away_lineup = process_lineup(away_lineup)
        lineups = pd.concat([home_lineup, away_lineup])
    try:
        yellow_cards = lineups['card_0_card_type'].value_counts().get('Yellow Card', 0)
    except:
        yellow_cards = 0
    try:
        red_cards = lineups['card_0_card_type'].value_counts().get('Red Card', 0)
    except:
        red_cards = 0
    
    return lineups, yellow_cards, red_cards
    

def download_df(df):
    col7 = st.columns([1, 1,1])
    with col7[1]:
        csv = df.to_csv(index=False)
        st.download_button(label="Download CSV", data=csv, file_name='eventos.csv', mime='text/csv', use_container_width=True)
    

if __name__ == "__main__":
    run()


def expand_column(df, column_name, prefix):
    """
    Expande uma coluna que contém dicionários ou listas de dicionários em múltiplas colunas.
    
    Args:
        df (pd.DataFrame): DataFrame original.
        column_name (str): Nome da coluna a ser expandida.
        prefix (str): Prefixo para as novas colunas.
        
    Returns:
        pd.DataFrame: DataFrame com a coluna expandida.
    """
    expanded_df = df[column_name].apply(pd.Series)
    expanded_df.columns = [f'{prefix}_{col}' for col in expanded_df.columns]
    return pd.concat([df.drop(column_name, axis=1), expanded_df], axis=1)

def process_lineup(lineup_df):
    """
    Processa o DataFrame de lineup expandindo as colunas necessárias.
    
    Args:
        lineup_df (pd.DataFrame): DataFrame de lineup da equipe.
        
    Returns:
        pd.DataFrame: DataFrame processado com colunas expandidas.
    """
    # Expandir a coluna 'positions'
    lineup_df = expand_column(lineup_df, 'positions', 'position')
    
    # Expandir 'position_0' e 'position_1' se existirem
    for pos in ['position_0', 'position_1']:
        if pos in lineup_df.columns:
            lineup_df = expand_column(lineup_df, pos, pos)
    
    # Expandir a coluna 'cards'
    lineup_df = expand_column(lineup_df, 'cards', 'card')
    
    # Expandir 'card_0' se existir
    if 'card_0' in lineup_df.columns:
        lineup_df = expand_column(lineup_df, 'card_0', 'card_0')
    
    return lineup_df