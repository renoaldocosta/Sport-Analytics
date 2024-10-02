# Bibliotecas Padrão
import time
from datetime import datetime
from urllib.request import urlopen

# Bibliotecas Externas
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image

# StatsBomb API
from statsbombpy import sb

# Bibliotecas de Visualização - MPL Soccer
from mplsoccer import (
    Pitch,
    Sbopen,
    Radar,
    FontManager,
    grid,
    VerticalPitch,
    inset_image,
    PyPizza,
    add_image
)

# Plotly para visualizações interativas
import plotly.graph_objects as go

# Biblioteca para bandeiras de países
import flagpy as fp

# Funções customizadas de texto
from app.Scripts.text_functions import mkd_text_divider, mkd_text, mkd_paragraph


parser = Sbopen()


def plot_pizza_comparison(params, values_player1, values_player2, player1, player2, font_normal, font_italic, font_bold, player1_team, player2_team):
    
    values = values_player1 + values_player2
    min_values = [min(values)] * len(params)
    max_values = [max(values)] * len(params)
    
    # st.write(len(params), len(values_player1), len(values_player2))
    length = len(params)
    while len(values_player1) < length:
        values_player1.append(0)
    while len(values_player2) < length:
        values_player2.append(0)
    """
    Plota um gráfico de comparação sobreposto para dois jogadores usando PyPizza.
    
    Args:
        params (list): Lista de parâmetros/eventos.
        values_player1 (list): Valores para o primeiro jogador.
        values_player2 (list): Valores para o segundo jogador.
        player1 (str): Nome do primeiro jogador.
        player2 (str): Nome do segundo jogador.
        font_normal, font_italic, font_bold: Fontes para estilização.
    
    Returns:
        matplotlib.figure.Figure: Figura do gráfico gerado.
    """
    # Instanciar a classe PyPizza
    
                            
    baker = PyPizza(
        params=params,                  # lista de parâmetros
        background_color="#EBEBE9",     # cor de fundo
        straight_line_color="#222222",  # cor das linhas retas
        straight_line_lw=1,             # largura das linhas retas
        last_circle_lw=1,               # largura da última circunferência
        last_circle_color="#222222",    # cor da última circunferência
        other_circle_ls="-.",           # estilo da linha das outras circunferências
        other_circle_lw=1,                # largura das outras circunferências
        min_range=min_values,                    # valor mínimo
        max_range=max_values  
    )
    
    # Plotar o gráfico de pizza
    fig, ax = baker.make_pizza(
        values_player1,                     # lista de valores do jogador 1
        compare_values=values_player2,      # lista de valores do jogador 2
        figsize=(10, 10),                   # tamanho da figura
        param_location=110,                 # localização dos parâmetros
        kwargs_slices=dict(
            facecolor="#1A78CF", edgecolor="#222222",
            zorder=2, linewidth=1
        ),                                  # estilo das fatias do jogador 1
        kwargs_compare=dict(
            facecolor="#FF9300", edgecolor="#222222",
            zorder=2, linewidth=1,
        ),                                  # estilo das fatias do jogador 2
        kwargs_params=dict(
            color="#000000", fontsize=12,
            fontproperties=font_normal.prop, va="center"
        ),                                  # estilo dos parâmetros
        kwargs_values=dict(
            color="#000000", fontsize=12,
            fontproperties=font_normal.prop, zorder=3,
            bbox=dict(
                edgecolor="#000000", facecolor="cornflowerblue",
                boxstyle="round,pad=0.2", lw=1
            )
        ),                                  # estilo dos valores do jogador 1
        kwargs_compare_values=dict(
            color="#000000", fontsize=12, fontproperties=font_normal.prop, zorder=3,
            bbox=dict(edgecolor="#000000", facecolor="#FF9300", boxstyle="round,pad=0.2", lw=1)
        ),                                  # estilo dos valores do jogador 2
    )
    
    
    fig.text(
        0.515, 0.97, f"{player1} vs {player2}", size=18,
        ha="center", fontproperties=font_bold.prop, color="#000000"
    )
    # Adicionar subtítulo
    # add subtitle
    fig.text(
        0.515, 0.942,
        f"{player1_team} vs {player2_team}",
        size=15,
        ha="center", fontproperties=font_bold.prop, color="#000000"
    )
    
    # Adicionar créditos
    CREDIT_1 = "data: statsbomb viz fbref"
    CREDIT_2 = "inspired by: @Worville, @FootballSlices, @somazerofc & @Soumyaj15209314"
    
    fig.text(
        0.99, 0.005, f"{CREDIT_1}\n{CREDIT_2}", size=9,
        fontproperties=font_italic.prop, color="#000000",
        ha="right"
    )
    
    params_offset = [False] * len(params)  # Exemplo: nenhum ajuste
    
    baker.adjust_texts(params_offset, offset=-0.17, adj_comp_values=True)
    
    return fig


def somar_eventos(df_player1, df_player2):
    """
    Função para somar os eventos de dois dataframes, combinando as linhas com base na coluna 'Parâmetros'.
    
    Args:
    df_player1 (pd.DataFrame): DataFrame do primeiro jogador.
    df_player2 (pd.DataFrame): DataFrame do segundo jogador.

    Returns:
    pd.DataFrame: DataFrame resultante com os valores somados, ordenado pela soma dos eventos ('Total').
    """
    # Fazendo merge dos dois dataframes com base na coluna 'Parâmetros'
    df_total = pd.merge(df_player1, df_player2, on='Parâmetros', how='outer', suffixes=('_player1', '_player2'))
    
    # Substituindo valores NaN por 0 para somar corretamente
    df_total.fillna(0, inplace=True)

    # Selecionando apenas colunas numéricas para realizar a soma
    colunas_numericas = df_total.columns.difference(['Parâmetros'])
    
    # Somando as colunas numéricas de player1 e player2
    df_total['Total'] = df_total[colunas_numericas].sum(axis=1)

    # Retornando apenas a coluna 'Parâmetros' e 'Total', ordenado pelo total
    df_total = df_total[['Parâmetros', 'Total']].sort_values(by='Total', ascending=False)

    return df_total


def calculate_event_counts(player_id, event_type,events):
            return events[(events['player_id'] == player_id) & (events['type'] == event_type)].shape[0]

def return_df_events_players(events, player_id, event_translation):
    params = []
    values = []

    for event in list(event_translation.keys()):
        # Traduzir o evento
        translated_event = event_translation[event]
        # Calcular o número de vezes que o evento ocorreu para o jogador
        event_count = calculate_event_counts(player_id, event,events)
        # Adicionar à lista de parâmetros e valores
        params.append(translated_event)
        values.append(event_count)
    df = pd.DataFrame({'Parâmetros': params, 'Valores': values}).sort_values(by='Valores', ascending=False).reset_index(drop=True)
    
    return df

def translate_position(position):
    # Dicionário para mapear posições de futebol em inglês para português
    position_translation = {
        'Right Wing Back': 'Ala Direito',
        'Right Defensive Midfield': 'Volante Direito',
        'Right Center Back': 'Zagueiro Direito',
        'Left Defensive Midfield': 'Volante Esquerdo',
        'Left Wing Back': 'Ala Esquerdo',
        'Left Center Back': 'Zagueiro Esquerdo',
        'Center Back': 'Zagueiro Central',
        'Goalkeeper': 'Goleiro',
        'Center Attacking Midfield': 'Meia Ofensivo Central',
        'Left Center Forward': 'Atacante Esquerdo',
        'Right Center Forward': 'Atacante Direito',
        'Substitute': 'Substituto',
        'Center Forward': 'Atacante Central',
        'nan': 'Indefinido'  # Para lidar com valores NaN
    }
    return position_translation.get(position, position)


def percent(value, total):
    if total == 0:
        return 0
    else:
        return round((value / total) * 100,2)

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


@st.cache_data
def plot_fouls_suffered_top10(match_data, visao='Geral', home_team='', away_team=''):
    """
    Plota um gráfico de barras horizontal mostrando os top 10 jogadores que sofreram mais faltas.
    
    Args:
        match_data (pd.DataFrame): DataFrame contendo os dados da partida.
        visao (str): Visão da análise ('Geral', 'Casa', 'Visitante').
        home_team (str): Nome do time da casa.
        away_team (str): Nome do time visitante.
    
    Returns:
        plotly.graph_objects.Figure: Figura Plotly contendo o gráfico.
    """
    # Definir os nomes das colunas relevantes
    type_col = 'type_name'
    team_col = 'team_name'
    player_col = 'player_name'
    pass_recipient_col = 'pass_recipient_name'
    outcome_col = 'outcome_name'
    minute_col = 'minute'
    second_col = 'second'
    index_col = 'index'

    # Filtrar com base na visão
    if visao == "Casa":
        teams = [home_team]
    elif visao == "Visitante":
        teams = [away_team]
    else:
        teams = [home_team, away_team] if home_team and away_team else match_data[team_col].unique().tolist()

    # Filtrar eventos apenas das equipes de interesse
    match_data = match_data[match_data[team_col].isin(teams)].copy()

    # Ordenar os eventos em ordem cronológica
    match_data.sort_values(by=[minute_col, second_col, index_col], inplace=True)

    # Resetar o índice
    match_data.reset_index(drop=True, inplace=True)

    # Inicializar a coluna 'fouled_player' com NaN
    match_data['fouled_player'] = pd.NA

    # Variável para rastrear o jogador em posse da bola
    current_possession_player = pd.NA

    # Iterar sobre os eventos para identificar quem está em posse da bola
    for idx, row in match_data.iterrows():
        event_type = row[type_col]
        player = row[player_col]
        
        if event_type in ['Pass', 'Ball Receipt', 'Carry', 'Clearance', 'Interception', 'Dribble']:
            # Atualizar o jogador em posse da bola
            current_possession_player = row[player_col]
        elif event_type == 'Foul Committed':
            # Atribuir o jogador que sofreu a falta como o jogador em posse da bola antes da falta
            match_data.at[idx, 'fouled_player'] = current_possession_player
            # Após a falta, a posse pode mudar ou ser interrompida; resetar
            current_possession_player = pd.NA
        elif event_type in ['Shot', 'Goal Keeper', 'Block', 'Goal']:
            # Eventos que podem interromper a posse de bola
            current_possession_player = pd.NA
        # Adicione outras condições se necessário

    # Filtrar apenas os eventos onde 'fouled_player' foi identificado
    df_fouls_suffered = match_data.dropna(subset=['fouled_player']).copy()

    # Contar as faltas sofridas por cada jogador
    fouls_suffered_counts = df_fouls_suffered['fouled_player'].value_counts().reset_index()
    fouls_suffered_counts.columns = ['Jogador', 'Faltas_Sofridas']

    # Selecionar os Top 10 jogadores
    top10_fouls = fouls_suffered_counts.head(10)

    # Verificar se há dados para plotar
    if top10_fouls.empty:
        st.warning("Nenhum dado de faltas sofridas encontrado para as equipes selecionadas.")
        return None

    # Criar o gráfico de barras horizontal com Plotly
    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=top10_fouls['Jogador'][::-1],  # Inverter para que o Top 1 apareça no topo
        x=top10_fouls['Faltas_Sofridas'][::-1],
        orientation='h',
        marker=dict(color='orange'),
        text=top10_fouls['Faltas_Sofridas'][::-1],
        textposition='auto'
    ))

    # Atualizar layout
    fig.update_layout(
        title=f"Top 10 Jogadores com Mais Faltas Sofridas - {visao}",
        xaxis_title="Número de Faltas Sofridas",
        yaxis_title="Jogador",
        template="plotly_white",
        plot_bgcolor='rgba(0,0,0,0)',
        height=600
    )

    # Ajustar a aparência das legendas e rótulos
    fig.update_layout(
        font=dict(
            family="Arial",
            size=12,
            color="Black"
        )
    )

    return fig

@st.cache_data
def plot_passes_vs_goals(match_data, visao='Geral', home_team='', away_team=''):
    """
    Plota um gráfico de barras agrupadas mostrando o número de passes e gols por equipe em uma partida usando Plotly Objects.

    Args:
        match_data (pd.DataFrame): DataFrame contendo os dados da partida com colunas 'type_name', 'team_name', etc.
        visao (str): Visão da análise ('Geral', 'Casa', 'Visitante').
        home_team (str): Nome do time da casa.
        away_team (str): Nome do time visitante.

    Returns:
        plotly.graph_objects.Figure: Figura Plotly contendo o gráfico.
    """
    # Verificar e exibir nomes das colunas para depuração

    # Definir os nomes das colunas relevantes
    type_col = 'type_name'
    team_col = 'team_name'
    outcome_col = 'outcome_name'

    # Verificar se as colunas existem
    if type_col not in match_data.columns or team_col not in match_data.columns:
        st.error(f"As colunas '{type_col}' e/ou '{team_col}' não existem no DataFrame.")
        return None

    # Filtrar dados com base na visão
    if visao == "Casa":
        teams = [home_team]
    elif visao == "Visitante":
        teams = [away_team]
    else:
        teams = [home_team, away_team] if home_team and away_team else match_data[team_col].unique().tolist()

    # Limpar e normalizar os dados
    match_data[type_col] = match_data[type_col].astype(str).str.strip().str.title()
    match_data[team_col] = match_data[team_col].astype(str).str.strip()

    # Filtrar eventos de Pass e Shot
    df_filtered = match_data[
        match_data[type_col].isin(['Pass', 'Shot']) &
        match_data[team_col].isin(teams)
    ].copy()

    # Traduzir nomes de eventos se necessário
    translation_dict = {'Pass': 'Passe', 'Shot': 'Chute'}
    df_filtered[type_col] = df_filtered[type_col].replace(translation_dict)


    # Contar Passes por equipe
    pass_counts = df_filtered[df_filtered[type_col] == 'Passe'].groupby(team_col).size().reset_index(name='Passes')

    # Contar Gols por equipe (Shot com outcome_name = Goal)
    if outcome_col in match_data.columns:
        # Filtrar eventos de Shot com outcome_name igual a Goal
        gol_filter = (match_data[type_col].str.strip().str.lower() == 'shot') & (match_data[outcome_col].str.strip().str.lower() == 'goal')
        df_gols = match_data[gol_filter].copy()
        # Traduzir 'Shot' para 'Gol'
        df_gols[type_col] = 'Gol'
        goal_counts = df_gols.groupby(team_col).size().reset_index(name='Gols')
    else:
        st.warning(f"A coluna '{outcome_col}' não existe no DataFrame. Nenhum gol será contabilizado.")
        goal_counts = pd.DataFrame(columns=[team_col, 'Gols'])

    # Unir contagens de Passes e Gols
    df_counts = pd.merge(pass_counts, goal_counts, on=team_col, how='outer').fillna(0)

    # Garantir que os valores sejam inteiros
    df_counts['Passes'] = df_counts['Passes'].astype(int)
    df_counts['Gols'] = df_counts['Gols'].astype(int)

    # Ordenar as equipes conforme a lista de teams
    df_counts[team_col] = pd.Categorical(df_counts[team_col], categories=teams, ordered=True)
    df_counts = df_counts.sort_values(team_col)


    # Verificar se há gols a serem plotados
    if df_counts['Gols'].sum() == 0:
        st.warning("Nenhum gol encontrado na filtragem. Verifique os dados e a tradução.")

    # Iniciar a figura
    fig = go.Figure()

    # Adicionar barras para Passes
    fig.add_trace(go.Bar(
        x=df_counts[team_col],
        y=df_counts['Passes'],
        name='Passes',
        marker_color='blue',
        text=df_counts['Passes'],
        textposition='auto'
    ))

    # Adicionar barras para Gols
    fig.add_trace(go.Bar(
        x=df_counts[team_col],
        y=df_counts['Gols'],
        name='Gols',
        marker_color='red',
        text=df_counts['Gols'],
        textposition='auto'
    ))

    # Atualizar layout para barras agrupadas
    fig.update_layout(
        barmode='group',
        title={
            'text': f"Relação entre Número de Passes e Gols por Equipe - {visao}",
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
        xaxis_title="Equipe",
        yaxis_title="Quantidade",
        legend_title="Métrica",
        template="plotly_white",
        plot_bgcolor='rgba(0,0,0,0)'
    )

    # Atualizar eixo y para iniciar em zero
    max_y = max(df_counts['Passes'].max(), df_counts['Gols'].max())
    fig.update_yaxes(range=[0, max_y * 1.2])

    # Ajustar a aparência das legendas e rótulos
    fig.update_layout(
        font=dict(
            family="Arial",
            size=12,
            color="Black"
        )
    )

    return fig


def carregar_dados():
    # Interface do Streamlit
    st.title("Dashboard de Futebol - FIFA World Cup")

    # Barra de Progresso
    progress_bar = st.progress(0)
    status_text = st.empty()
    time.sleep(tempo_carregamento)

    selected_competition = st.selectbox('Selecione a Competição', competitions_df['competition_name'].unique())

    selected_season = st.selectbox('Selecione a Temporada', competitions_df['season_name'].unique())

    # Obter competition_id e season_id baseados na seleção
    selected_row = competitions_df[
        (competitions_df['competition_name'] == selected_competition) &
        (competitions_df['season_name'] == selected_season)
    ]
    selected_competition_id = selected_row['competition_id'].values[0]
    selected_season_id = selected_row['season_id'].values[0]

    selected_match = st.selectbox('Selecione a Partida', matches_df['match_date'].unique())
    selected_match_id = matches_df[matches_df['match_date'] == selected_match]['match_id'].values[0]


def match_data(match_id):
    return parser.event(match_id=match_id)[0]

@st.cache_data
def plot_passes_without_filter_player(match_data, event_type='Pass', arrows=True, heat_map=False, visao='Geral', home_team='', away_team=''):
    # Filtrar os dados para o tipo de evento e equipe especificada
    if visao == "Casa":
        team_name = home_team
    elif visao == "Visitante":
        team_name = away_team
    else:
        team_name = ''
    
    if team_name:
        teams_filter = (match_data['type_name'] == event_type) & (match_data['team_name'] == team_name)
    else:
        teams_filter = match_data['type_name'] == event_type
        
    df_events = match_data.loc[teams_filter, ['x', 'y', 'end_x', 'end_y']].copy()
    
    # Substituir strings vazias por NaN
    df_events[['end_x', 'end_y']] = df_events[['end_x', 'end_y']].replace('', pd.NA)
    
    # Converter para float (se necessário)
    df_events[['x', 'y', 'end_x', 'end_y']] = df_events[['x', 'y', 'end_x', 'end_y']].astype(float)
    
    # Soma dos valores da linha 0
    try:
        soma_linha_zero = df_events.iloc[0].sum()
    except:
        soma_linha_zero = 0
    
    # Separar eventos com e sem end_x/end_y
    df_valid = df_events.dropna(subset=['end_x', 'end_y'])
    df_invalid = df_events[df_events['end_x'].isna() | df_events['end_y'].isna()]
    
    # Configurar o campo
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#aabb97', line_color='white',
                  stripe_color='#c2d59d', stripe=False)  # Ajuste conforme necessário
    
    fig, ax = pitch.draw(figsize=(10, 7))
    
    # Traduzir o tipo de evento para a legenda
    event_type_translated = translate_event(event_type)
    
    # Título do Gráfico
    titulo = f"{event_type_translated} - {visao}"
    if team_name:
        titulo += f" - {team_name}"
    ax.set_title(titulo, fontsize=20, fontweight='bold', pad=20)
    
    
    # Plotar setas para eventos válidos
    if arrows and not df_valid.empty:
        pitch.arrows(df_valid['x'], df_valid['y'], df_valid['end_x'], df_valid['end_y'], 
                    width=2, color='blue', alpha=0.6, ax=ax, label=f'{event_type_translated}')
    
    # Plotar pontos para eventos inválidos
    if not df_invalid.empty:
        scatter = pitch.scatter(df_invalid['x'], df_invalid['y'], s=100, color='red', edgecolors='black', 
                                alpha=0.7, ax=ax, label='Passes Inválidos')
    
    # Adicionar mapa de calor se solicitado
    if heat_map and not df_valid.empty:
        try:
            pitch.kdeplot(df_valid['x'], df_valid['y'], ax=ax, alpha=0.5, shade=True, cmap='coolwarm', label='Mapa de Calor')
        except Exception as e:
            st.write("Não foi possível plotar o mapa de calor:", e)
    
    # Adicionar legenda
    handles, labels = ax.get_legend_handles_labels()
    if handles:
        ax.legend(handles, labels, loc='upper right', fontsize=12)
    
    # Adicionar informações de total de eventos
    total_valid = len(df_valid)
    total_invalid = len(df_invalid)
    info_text = f"Total de {event_type_translated}: {total_valid}"
    plt.gcf().text(0.02, 0.95, info_text, fontsize=12, verticalalignment='top', bbox=dict(facecolor='white', alpha=0.5))
    
    return fig, soma_linha_zero

def plot_passes(match_data, player_name, event_type='Pass'):
    # Filtrar os dados para o tipo de evento e jogador especificado
    player_filter = (match_data['type_name'] == event_type) & (match_data['player_name'] == player_name)
    df_events = match_data.loc[player_filter, ['x', 'y', 'end_x', 'end_y']].copy()
    
    # Substituir strings vazias por NaN
    df_events[['end_x', 'end_y']] = df_events[['end_x', 'end_y']].replace('', pd.NA)
    
    # Converter para float (se necessário)
    df_events[['x', 'y', 'end_x', 'end_y']] = df_events[['x', 'y', 'end_x', 'end_y']].astype(float)
    # soma os valores da linha 0
    try:
        soma_linha_zero = df_events.iloc[0].sum()
    except:
        soma_linha_zero = 0
    # Separar eventos com e sem end_x/end_y
    df_valid = df_events.dropna(subset=['end_x', 'end_y'])
    df_invalid = df_events[df_events['end_x'].isna() | df_events['end_y'].isna()]
    
    # Configurar o campo
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#aabb97', line_color='white',
                  stripe_color='#c2d59d', stripe=False)  # Ajuste conforme necessário
    
    fig, ax = pitch.draw(figsize=(10, 7))
    
    # Plotar setas para eventos válidos
    if not df_valid.empty:
        pitch.arrows(df_valid['x'], df_valid['y'], df_valid['end_x'], df_valid['end_y'], 
                    width=2, color='white', ax=ax)
    
    event_type_translated = translate_event(event_type)
    # Plotar pontos para eventos inválidos
    if not df_invalid.empty:
        pitch.scatter(df_invalid['x'], df_invalid['y'], s=100, color='red', edgecolors='black', 
                     alpha=0.7, ax=ax, label=event_type_translated)
    
    # Opcional: Adicionar mapa de calor para os eventos válidos
    if not df_valid.empty:
        try:
            pitch.kdeplot(df_valid['x'], df_valid['y'], ax=ax, alpha=0.5, shade=True, cmap='coolwarm')
        except Exception as e:
            st.write("Não foi possível plotar o mapa de calor:", e)
    
    # Legenda (apenas se houver eventos inválidos)
    if not df_invalid.empty:
        ax.legend()
    
    return fig, soma_linha_zero


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
    # Carregar Matches com Spinner
    
    season_name = st.selectbox('Selecione a copa do mundo:', season_options, key='season_name', index=id_index_season_name, on_change=restart_session_state('season_name'))
        
        
    id_index_season_name = list(season_options).index(season_name)
    st.session_state.id_index_season_name = id_index_season_name
    
    season_id = df[df['season_name'] == season_name].season_id.values[0]
    df = df[df['season_id'] == season_id]
    return df, season_id

def translate_event(event_type):
    event_translation = {
        '50/50': '50/50',
        'Bad Behaviour': 'Comportamento Antidesportivo',
        'Ball Receipt*': 'Bola Recebida',
        'Ball Recovery': 'Bola Recuperada ',
        'Block': 'Bloqueio',
        'Camera off: Deprecated': 'Câmera Desligada (Depreciado)',
        'Camera On: Deprecated': 'Câmera Ligada (Depreciado)',
        'Carry': 'Condução de Bola',
        'Clearance': 'Desarme',
        'Dispossessed': 'Perdeu a Bola',
        'Dribble': 'Drible',
        'Dribbled Past': 'Driblado pelo Adversário',
        'Duel': 'Duelo',
        'Error': 'Erro',
        'Foul Committed': 'Falta Cometida',
        'Foul Won': 'Falta Sofrida',
        'Goal Keeper': 'Goleiro',
        'Half End': 'Fim do Tempo',
        'Half Start': 'Início do Tempo',
        'Injury Stoppage': 'Parada por Lesão',
        'Interception': 'Interceptação',
        'Miscontrol': 'Perda de Controle',
        'Offside': 'Impedimento',
        'Own Goal Against': 'Gol Contra',
        'Own Goal For': 'Gol Para',
        'Pass': 'Passe',
        'Player Off': 'Jogador Saiu',
        'Player On': 'Jogador Entrou',
        'Pressure': 'Pressão',
        'Referee Ball-Drop': 'Bola Caída',
        'Shield': 'Proteção de Bola',
        'Shot': 'Chute ao Gol',
        'Starting XI': 'Escalação Inicial',
        'Substitution': 'Substituição',
        'Tactical Shift': 'Mudança Tática'
    }
    return event_translation.get(event_type, event_type)

def filter_events(events, todos=True):
    if 'id_index_event_type' not in st.session_state:
        st.session_state.id_index_event_type = 0
        id_index_event_type = 0
    else:
        id_index_event_type = st.session_state.id_index_event_type
    
    # Adicionar "Todos" à lista de opções, se necessário
    if todos:
        options_event_type = ["Todos"] + events['type'].unique().tolist()
    else:
        options_event_type = events['type'].unique().tolist()

    if todos:
        # Traduzir os eventos para exibição no selectbox
        translated_options_event_type = ["Todos"] + [translate_event(event) for event in events['type'].unique().tolist()]

        id_index_event_type = valid_index(translated_options_event_type, id_index_event_type)
    else:
        # Traduzir os eventos para exibição no selectbox
        translated_options_event_type = [translate_event(event) for event in events['type'].unique().tolist()]

        id_index_event_type = valid_index(translated_options_event_type, id_index_event_type)

    # Exibir os eventos traduzidos no selectbox
    event_type_translated = st.selectbox(
        "Selecione o tipo de evento", 
        translated_options_event_type,
        index=id_index_event_type,
    )

    # Encontrar o índice do evento traduzido na lista original
    if event_type_translated == "Todos":
        event_type = "Todos"
    else:
        event_type = options_event_type[translated_options_event_type.index(event_type_translated)]
    
    id_index_event_type = translated_options_event_type.index(event_type_translated)
    st.session_state.id_index_event_type = id_index_event_type
    
    # Filtrar eventos, se necessário
    if event_type == "Todos":
        return events, event_type
    else:
        return events[events['type'] == event_type], event_type


def filter_events_2(events, todos=True):
    if 'id_index_event_type' not in st.session_state:
        st.session_state.id_index_event_type = 0
        id_index_event_type = 0
    else:
        id_index_event_type = st.session_state.id_index_event_type
    if todos:
        options_event_type = ["Todos"] + events['type'].unique().tolist()
    else:
        options_event_type = events['type'].unique().tolist()
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
    try:
        id_index_player = options_player.index(player)
    except:
        pass
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
    tempo_carregamento = 0.1
    #carregar_dados()
    #st.title("Jogo da Copa do Mundo")
    with st.sidebar:
        with st.spinner('Processando. Por favor, aguarde...'):
            time.sleep(1)
            progress_bar = st.progress(0)
            status_text = st.empty()
    status_text.text("Carregando competições...")
    progress_bar.progress(33)    
    time.sleep(tempo_carregamento)
    
    df, competition_id = load_data()
    
    df, season_id = filter_season(df)
    status_text.text("Carregando partidas...")
    df_match, match_id = filter_match(df, season_id, competition_id)
    progress_bar.progress(66)
    time.sleep(tempo_carregamento)
    
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
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Estatísticas da Partida", "Escalação", "Detalhes do Jogador", "Comparação de Jogadores", "Outros Detalhes"])
    
    mkd_text("", level='subheader')
    home_lineup = sb.lineups(match_id=match_id)[home_team].sort_values('jersey_number')
    away_lineup = sb.lineups(match_id=match_id)[away_team].sort_values('jersey_number')
    lineups = sb.lineups(match_id=match_id)
    
    
    #Substitutions = lineups[]
    # Tecnicos
    home_managers = df_match['home_managers'].values[0]
    away_managers = df_match['away_managers'].values[0]
    
    with tab3: # ["Casa", "Visitante"]
        with st.container(border=True):
            col7 = st.columns([1,1,1])
            with col7[1]:
                vision_options = ["Casa", "Visitante"]
                visao = st.radio("Selecionar jogador da seleção:", vision_options, horizontal=True, index=0, key='visao_player')
                status_text.text("Carregando eventos da partida...")
                events = filter_vision(visao, match_id, home_team, away_team)
                progress_bar.progress(100)
                time.sleep(tempo_carregamento*1.6)
                progress_bar.empty()
                status_text.text("")
                
                
                lineups, yellow_cards, red_cards = lineups_metrics(lineups, visao, home_lineup, away_lineup)
                events, player = filter_players(events, todos=False)
                position = events['position'].value_counts().idxmax()
            events = events[event_columns]
            # Metricas passes
            passes = events['type'].value_counts().get('Pass', 0)
            passes_completos = passes - events['pass_outcome'].value_counts().get('Incomplete', 0)
            chutes_a_gol = events['type'].value_counts().get('Shot', 0)
            gols = events['shot_outcome'].value_counts().get('Goal', 0)
            
            percent_passes = percent(passes_completos, passes)
            percent_score = percent(gols, chutes_a_gol)

                
                
            st.write(f"")
            position = translate_position(position)
            jersey_number = lineups[lineups['player_name'] == player]['jersey_number'].values[0]
            st.subheader(f"Posição: {position} | Camisa: {jersey_number}")
            st.write(f"")
            
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
            
            st.write('')
            st.divider()
            st.subheader('Eventos do jogador')
            
            events, event_type  = filter_events(events, todos=False)
            col8 = st.columns([1,2,1])
            with col8[1]:
                final_data = match_data(match_id)
                fig,soma_linha_zero = plot_passes(final_data, player, event_type)
                event_type = translate_event(event_type)
                if soma_linha_zero != 0:
                    st.subheader(f"Mapa: {event_type}")
                    st.pyplot(fig)
            st.subheader(f"Detalhamento do evento de {event_type}")

            events_to_show = events.reset_index(drop=True)
            events_to_show.index = events_to_show.index + 1
            st.dataframe(events_to_show)
            
            def match_data_2(match_id):
                return parser.event(match_id=match_id)[0]
        
    
    with tab2: # st.subheader("Técnicos")
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
            with col3[1]:
                st.markdown(f"<h3 style='color: red'>{away_team} (Visitante)</h3>", unsafe_allow_html=True)
                with st.container(border=True):
                    for index, row in away_lineup.iterrows():
                        # Formatar a string com número da camisa, nome, e o apelido (se existir)
                        nickname = f" ({row['player_nickname']})" if row['player_nickname'] else ""
                        df_away = f"{row['jersey_number']} - {row['player_name']}{nickname}"
                        
                        # Exibir o resultado no Streamlit
                        st.write(df_away)
    with tab5: # st.subheader("Detalhes da Partida")
        with st.container(border=True):
        # ========================== Detalhes da Partida ==========================
            st.subheader("Detalhes da Partida")
            st.write(f"**Estádio:** {match['stadium']}")
            # match_week
            st.write(f"**Semana:** {match['match_week']}")
            # Group Stage
            st.write(f"**Fase:** {match['competition_stage']}")
            
            
    with tab1: # st.subheader("Métricas")
        with st.container(border=True):
            
            col_team = st.columns([1,1])
            with col_team[0]:
                st.markdown(f"<h3 style='color: green'>{home_team} (Casa)</h3>", unsafe_allow_html=True)
            with col_team[1]:
                st.markdown(f"<h3 style='color: red'>{away_team} (Visitante)</h3>", unsafe_allow_html=True)
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
                # st.metric("Cartão Amarelo", yellow_cards)
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
                # st.metric("Cartão Vermelho", red_cards)
            with col4[2]:
                st.metric("Dribles", events['type'].value_counts().get('Dribble', 0))
            with col4[3]:  # Add an additional column for corner kicks
                corner_passes = events[(events['type'] == 'Pass') & (events['pass_type'] == 'Corner')]
                corner_shots = events[(events['type'] == 'Shot') & (events['play_pattern'] == 'From Corner')]
                corner = len(corner_passes) + len(corner_shots)
                st.metric("Escanteios", corner)
            
            final_data = match_data(match_id)
            
            col11 = st.columns([1,1,1])
            with col11[1]:
                st.divider()
            col11 = st.columns([1.3,1,1])
            with col11[1]:
                plot_heat_arraw_map = st.checkbox("Mostrar Gráficos", value=False, key='pass_chart')
                
            if plot_heat_arraw_map:
                load_time_plot = 0.01
                # Interface aprimorada com barra de progresso e status para os dois eventos
                col9 = st.columns([1, 1])

                # ---- Seção para o evento de tipo 'Pass' ----
                with col9[0]:
                    with st.spinner('Processando. Por favor, aguarde...'):
                        # Barra de progresso e status
                        progress_bar_col9 = st.progress(0)
                        status_text_col9 = st.empty()

                        time.sleep(load_time_plot)  # Simulação de um pequeno tempo de processamento
                        progress_bar_col9.progress(20)
                        status_text_col9.text("Inicializando...")

                        # Configuração de opções para o gráfico de Pass
                        event_type = 'Pass'
                        event_type_translated = translate_event(event_type)
                        with st.container(border=True):
                            st.subheader(f"Mapa: {event_type_translated}")
                            
                            col10 = st.columns([1, 1])
                            with col10[0]:
                                arrows = st.checkbox("Mostrar Setas", value=False, key='arrows1')
                            with col10[1]:
                                heat_map = st.checkbox("Mostrar Mapa de Calor", value=True, key='heat_map1')

                            # Atualizando progresso após a escolha das opções
                            time.sleep(load_time_plot)  # Simulação de tempo para configuração
                            progress_bar_col9.progress(40)
                            status_text_col9.text("Configurando opções...")

                            # Plotagem do gráfico de Pass
                            fig, soma_linha_zero = plot_passes_without_filter_player(final_data, event_type, arrows=arrows, heat_map=heat_map, visao=visao, home_team=home_team, away_team=away_team)

                            # Atualizando progresso após a plotagem
                            progress_bar_col9.progress(80)
                            status_text_col9.text("Gerando gráfico...")

                            # Exibir o gráfico se houver dados
                            if soma_linha_zero != 0:
                                st.pyplot(fig)
                                progress_bar_col9.progress(100)
                                status_text_col9.text("Plotagem concluída!")
                            else:
                                st.warning("Nenhum dado disponível para plotagem.")

                            # Limpar a barra de progresso e a mensagem de status após um breve tempo
                            time.sleep(load_time_plot)
                            progress_bar_col9.empty()
                            status_text_col9.empty()

                # ---- Seção para o evento de tipo 'Shot' ----
                with col9[1]:
                    with st.spinner('Processando. Por favor, aguarde...'):
                        # Barra de progresso e status
                        progress_bar_col9_shot = st.progress(0)
                        status_text_col9_shot = st.empty()

                        time.sleep(load_time_plot)  # Simulação de um pequeno tempo de processamento
                        progress_bar_col9_shot.progress(20)
                        status_text_col9_shot.text("Inicializando...")

                        # Configuração de opções para o gráfico de Shot
                        event_type = 'Shot'
                        event_type_translated = translate_event(event_type)
                        with st.container(border=True):
                            
                            st.subheader(f"Mapa: {event_type_translated}")
                            
                            col10_shot = st.columns([1, 1])
                            with col10_shot[0]:
                                arrows = st.checkbox("Mostrar Setas", value=True, key='arrows2')
                            with col10_shot[1]:
                                heat_map = st.checkbox("Mostrar Mapa de Calor", value=False, key='heat_map2')

                            # Atualizando progresso após a escolha das opções
                            time.sleep(load_time_plot)  # Simulação de tempo para configuração
                            progress_bar_col9_shot.progress(40)
                            status_text_col9_shot.text("Configurando opções...")

                            # Plotagem do gráfico de Shot
                            fig, soma_linha_zero = plot_passes_without_filter_player(final_data, event_type, arrows=arrows, heat_map=heat_map, visao=visao, home_team=home_team, away_team=away_team)

                            # Atualizando progresso após a plotagem
                            progress_bar_col9_shot.progress(80)
                            status_text_col9_shot.text("Gerando gráfico...")

                            # Exibir o gráfico se houver dados
                            if soma_linha_zero != 0:
                                st.pyplot(fig)
                                progress_bar_col9_shot.progress(100)
                                status_text_col9_shot.text("Plotagem concluída!")
                            else:
                                st.warning("Nenhum dado disponível para plotagem.")

                            # Limpar a barra de progresso e a mensagem de status após um breve tempo
                            time.sleep(load_time_plot)
                            progress_bar_col9_shot.empty()
                            status_text_col9_shot.empty()
                fig_passes_goals = plot_passes_vs_goals(final_data, visao=visao, home_team=home_team, away_team=away_team)
                st.plotly_chart(fig_passes_goals, use_container_width=True)
                
                # Plotagem dos Top 10 Jogadores com Mais Faltas Sofridas
                st.subheader("Top 10 Jogadores com Mais Faltas Sofridas")
                fig_top10_fouls = plot_fouls_suffered_top10(
                    match_data=final_data,
                    visao=visao,
                    home_team=home_team,
                    away_team=away_team
                )
                if fig_top10_fouls:
                    st.plotly_chart(fig_top10_fouls, use_container_width=True)
                
            # Filtrando apenas as colunas que estão disponíveis nos eventos
            events_filtered = events[event_columns].copy()

            # Exibindo o DataFrame no Streamlit
            st.write("")
            with st.expander("📝📥 Relação de Eventos da Partida", expanded=False):
                st.subheader("Eventos da Partida")
                col6 = st.columns([1, 1])
                with col6[0]:
                    events_filtered, event_type = filter_events(events_filtered, todos=True)
                with col6[1]:
                    players_filtered, player = filter_players(events_filtered, todos=True)
                st.dataframe(players_filtered, hide_index = True)
                download_df(players_filtered)

    with tab4: # st.subheader("Comparação de Jogadores")
        with st.container(border=True):
            st.subheader("Comparação de Jogadores")
            col12 = st.columns([1,1,2,2,1,1])
            with col12[2]:
                players_id = lineups['player_id'].unique()
                players = [lineups.loc[lineups['player_id'] == player_id, 'player_name'].values[0] for player_id in players_id]
                player1 = st.selectbox("Selecione o primeiro jogador:", players, key='player1')
                player1_id = lineups.loc[lineups['player_name'] == player1, 'player_id'].values[0]
                try:
                    player1_team = events[events['player_id'] == player1_id]['team'].values[0]
                except:
                    player1_team = "Não informado"
                
            with col12[3]:
                players.remove(player1)
                player2 = st.selectbox("Selecione o segundo jogador:", players, key='player2')
                palyer2_id = lineups.loc[lineups['player_name'] == player2, 'player_id'].values[0]
                try:
                    player2_team = events[events['player_id'] == palyer2_id]['team'].values[0]
                except:
                    player2_team = "Não informado"
            conteiner_filtro_eventos = st.container()
            with st.expander("📊📈 Comparação de Jogadores", expanded=True):
                col13 = st.columns([1,1])
            
            # Função para calcular as ocorrências de eventos para o jogador
            
            event_translation = {
                '50/50': '50/50',
                'Bad Behaviour': 'Comportamento Antidesportivo',
                'Ball Receipt*': 'Bola Recebida',
                'Ball Recovery': 'Bola Recuperada',
                'Block': 'Bloqueio',
                'Carry': 'Condução de Bola',
                'Clearance': 'Desarme',
                'Dispossessed': 'Perdeu a Bola',
                'Dribble': 'Drible',
                'Dribbled Past': 'Driblado pelo Adversário',
                'Duel': 'Duelo',
                'Foul Committed': 'Falta Cometida',
                'Foul Won': 'Falta Sofrida',
                'Goal Keeper': 'Goleiro',
                'Half End': 'Fim do Tempo',
                'Half Start': 'Início do Tempo',
                'Injury Stoppage': 'Parada por Lesão',
                'Interception': 'Interceptação',
                'Miscontrol': 'Perda de Controle',
                'Pass': 'Passe',
                'Pressure': 'Pressão',
                'Shot': 'Chute ao Gol',
                'Substitution': 'Substituição',
                'Tactical Shift': 'Mudança Tática'
            }
            df_player1 = return_df_events_players(events, player1_id, event_translation)
            df_player1 = df_player1[df_player1['Valores'] > 0] 
            
            df_player2 = return_df_events_players(events, palyer2_id, event_translation)
            df_player2 = df_player2[df_player2['Valores'] > 0]
            
            
            df_resultado = somar_eventos(df_player1, df_player2)
            columns_top10 = df_resultado['Parâmetros'].head(10).to_list()
            
            # Inverter o dicionário event_translation para ter traduções como chave e inglês como valor
            inverted_event_translation = {v: k for k, v in event_translation.items()}

            # Lista de eventos em português (columns_top10) que queremos destraduzir
            columns_top10 = ['Passe', 'Bola Recebida', 'Condução de Bola', 'Pressão', 'Bola Recuperada',
                            'Falta Cometida', 'Bloqueio', 'Desarme', 'Duelo', 'Falta Sofrida']

            # Destraduzir usando o dicionário invertido
            events_in_english = [inverted_event_translation[event] for event in columns_top10]

            # Criar um dataframe com os eventos destraduzidos
            df_top_10_destraduzido = pd.DataFrame({'Parâmetros': events_in_english})

            # Configurar o multiselect corretamente
            with conteiner_filtro_eventos:
                    selected_events = st.multiselect(
                        "Selecione até 12 eventos para incluir no gráfico:",
                        options=list(event_translation.keys()),  # Use as chaves em inglês
                        format_func=lambda x: event_translation[x],  # Traduzir para exibição
                        max_selections=12,  # Limite de 12 seleções
                        key='selected_events',  # Chave para armazenar a seleção
                        default=df_top_10_destraduzido  # Use as chaves em inglês como padrão
                    )
                    

                    if selected_events:
                        def plot_pizza(player_id):
                            # Lista de parâmetros e valores correspondentes
                            params = []
                            values = []

                            for event in selected_events:
                                # Traduzir o evento
                                translated_event = event_translation[event]
                                # Calcular o número de vezes que o evento ocorreu para o jogador
                                event_count = calculate_event_counts(player_id, event,events)
                                # Adicionar à lista de parâmetros e valores
                                params.append(translated_event)
                                values.append(event_count)
                                df = pd.DataFrame({'Parâmetros': params, 'Valores': values})
                            return params, values, df
                        params_player1, values_player1, df_player1_pizza = plot_pizza(player1_id)
                        params_player2, values_player2, df_player2_pizza = plot_pizza(palyer2_id)

                        font_normal = FontManager('https://raw.githubusercontent.com/googlefonts/roboto/main/'
                                                'src/hinted/Roboto-Regular.ttf')
                        font_italic = FontManager('https://raw.githubusercontent.com/googlefonts/roboto/main/'
                                                'src/hinted/Roboto-Italic.ttf')
                        font_bold = FontManager('https://raw.githubusercontent.com/google/fonts/main/apache/robotoslab/'
                                                'RobotoSlab[wght].ttf')
                        

                        def get_plot_piza(params, values, player, df):
                            df = pd.DataFrame({'Parâmetros': params, 'Valores': values})
                            df = df[df['Valores'] > 0]
                            params = df['Parâmetros'].tolist()
                            values = df['Valores'].tolist()
                            # st.write(df)
                            count_values = len(values)
                            # st.write(count_values)
                            min_df = df['Valores'].min()
                            list_values_min = [min_df] * count_values
                            
                            max_df = df['Valores'].max()
                            list_values_max = [max_df] * count_values
                            # instantiate PyPizza class
                            baker = PyPizza(
                                params=params,                  # list of parameters
                                straight_line_color="#000000",  # color for straight lines
                                straight_line_lw=1,             # linewidth for straight lines
                                last_circle_lw=1,               # linewidth of last circle
                                other_circle_lw=1,              # linewidth for other circles
                                other_circle_ls="-.",            # linestyle for other circles
                                min_range=list_values_min,                    # valor mínimo
                                max_range=list_values_max         # valor máximo do gráfico
                            )

                            # plot pizza
                            fig, ax = baker.make_pizza(
                                values,              # list of values
                                figsize=(8, 8),      # adjust figsize according to your need
                                param_location=110,  # where the parameters will be added
                                kwargs_slices=dict(
                                    facecolor="cornflowerblue", edgecolor="#000000",
                                    zorder=2, linewidth=1
                                ),                   # values to be used when plotting slices
                                kwargs_params=dict(
                                    color="#000000", fontsize=12,
                                    fontproperties=font_normal.prop, va="center"
                                ),                   # values to be used when adding parameter
                                kwargs_values=dict(
                                    color="#000000", fontsize=12,
                                    fontproperties=font_normal.prop, zorder=3,
                                    bbox=dict(
                                        edgecolor="#000000", facecolor="cornflowerblue",
                                        boxstyle="round,pad=0.2", lw=1
                                    )
                                )                    # values to be used when adding parameter-values
                            )

                            # add title
                            fig.text(
                                0.515, 0.97, f"{player} - ()", size=18,
                                ha="center", fontproperties=font_bold.prop, color="#000000"
                            )

                            # add credits
                            CREDIT_1 = "data: statsbomb viz fbref"
                            CREDIT_2 = "inspired by: @Worville, @FootballSlices, @somazerofc & @Soumyaj15209314"

                            fig.text(
                                0.99, 0.005, f"{CREDIT_1}\n{CREDIT_2}", size=9,
                                fontproperties=font_italic.prop, color="#000000",
                                ha="right"
                            )
                            return fig

                        try:
                            fig1 = get_plot_piza(params_player1, values_player1, player1,df_player1_pizza)
                            col13[0].pyplot(fig1)
                            col13[0].dataframe(df_player1, use_container_width=True)
                        except:
                            st.warning("**Seleção de jogador Inválida**: Nenhum dado disponível para plotagem referente ao **jogador 1**")
                        try:
                            fig2 = get_plot_piza(params_player2, values_player2, player2, df_player2_pizza)
                            col13[1].pyplot(fig2)
                            col13[1].dataframe(df_player2, use_container_width=True)
                        except:
                            st.warning("**Seleção de jogador Inválida**: Nenhum dado disponível para plotagem referente ao **jogador 2**")
                        
            try:
                # Renomeando as colunas de valores para identificar os jogadores
                df_player1_pizza.rename(columns={'Valores': 'Player1'}, inplace=True)
                df_player2_pizza.rename(columns={'Valores': 'Player2'}, inplace=True)

                # Merge dos dois DataFrames usando 'Evento' como chave
                df_comparacao = pd.merge(df_player1_pizza, df_player2_pizza, on='Parâmetros', how='outer')

                # Substituindo valores NaN por 0
                df_comparacao.fillna(0, inplace=True)

                # Convertendo para inteiros para evitar casas decimais
                df_comparacao[['Player1', 'Player2']] = df_comparacao[['Player1', 'Player2']].astype(int)
                df_comparacao = df_comparacao.sort_values(by='Player1', ascending=False)
                df_comparacao = df_comparacao[(df_comparacao['Player1'] > 0) | (df_comparacao['Player2'] > 0)]
                # st.write(df_comparacao)
                params_final = df_comparacao['Parâmetros'].tolist()
                values_player1 = df_comparacao['Player1'].tolist()
                values_player2 = df_comparacao['Player2'].tolist()

                fig_comparison = plot_pizza_comparison(
                    params=params_final,
                    values_player1=values_player1,
                    values_player2=values_player2,
                    player1=player1,
                    player2=player2,
                    font_normal=font_normal,
                    font_italic=font_italic,
                    font_bold=font_bold,
                    player1_team=player1_team,
                    player2_team=player2_team
                )
                
                # Exibir o gráfico no Streamlit
                st.pyplot(fig_comparison)
            except Exception as e:
                st.warning("Nenhum dado disponível para plotagem. Tente com outros jogadores.")
            



if __name__ == "__main__":
    run()