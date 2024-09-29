import streamlit as st
import pandas as pd

# Função para carregar e mostrar a descrição das tabelas
def mostrar_descricao_tabela(tabela_nome):
    descricoes = {
        "Competitions": """
        **Competitions**
        Contém informações sobre as competições de futebol disponíveis no conjunto de dados.
        
        - **competition_id**: Identificador único da competição (INTEGER, Primary Key).
        - **season_id**: Identificador único da temporada dentro da competição (INTEGER, Foreign Key para Seasons).
        - **country_name**: Nome do país onde a competição é realizada (TEXT).
        - **competition_name**: Nome oficial da competição (TEXT).
        - **competition_gender**: Categoria de gênero da competição (e.g., masculino, feminino) (TEXT).
        - **season_name**: Nome da temporada (e.g., "2019/2020") (TEXT).
        - **match_updated**: Data e hora da última atualização dos dados de partidas (DATETIME).
        - **match_available**: Data e hora em que os dados da partida ficaram disponíveis (DATETIME).
        """,
        "Matches": """
        **Matches**
        Contém informações detalhadas sobre as partidas individuais em uma competição.
        
        - **match_id**: Identificador único da partida (INTEGER, Primary Key).
        - **match_date**: Data em que a partida foi jogada (DATE).
        - **kick_off**: Hora programada para o início da partida (TIME).
        - **competition**: Nome da competição incluindo o país (e.g., "Alemanha - Bundesliga") (TEXT).
        - **season**: Temporada em que a partida foi jogada (e.g., "2019/2020") (TEXT).
        - **home_team**: Nome do time mandante (TEXT).
        - **away_team**: Nome do time visitante (TEXT).
        - **home_score**: Gols marcados pelo time mandante (INTEGER).
        - **away_score**: Gols marcados pelo time visitante (INTEGER).
        - **match_status**: Status de disponibilidade dos dados da partida (e.g., "disponível") (TEXT).
        - **last_updated**: Data e hora da última atualização dos dados da partida (DATETIME).
        """,
        "Lineups": """
        **Lineups**
        Contém informações sobre os jogadores que participaram de uma partida por equipe.
        
        - **player_id**: Identificador único do jogador (INTEGER, Primary Key).
        - **player_name**: Nome completo do jogador (TEXT).
        - **player_nickname**: Apelido ou nome conhecido do jogador (TEXT, pode ser NULL).
        - **birth_date**: Data de nascimento do jogador (DATE).
        - **player_gender**: Gênero do jogador (e.g., "masculino", "feminino") (TEXT).
        - **player_height**: Altura do jogador em centímetros (FLOAT, pode ser NULL).
        - **player_weight**: Peso do jogador em quilogramas (FLOAT, pode ser NULL).
        - **jersey_number**: Número da camisa usada pelo jogador na partida (INTEGER).
        - **country**: País de nacionalidade do jogador (TEXT).
        """,
        "Events": """
        **Events**
        Contém dados detalhados de eventos para uma partida específica, capturando cada ação de bola durante a partida.
        
        - **id**: Identificador único para o evento (TEXT, Primary Key).
        - **index**: Índice sequencial do evento dentro da partida (INTEGER).
        - **period**: Período da partida em que o evento ocorreu (1 = Primeiro Tempo, 2 = Segundo Tempo, etc.) (INTEGER).
        - **minute**: Minuto da partida em que o evento ocorreu (INTEGER).
        - **second**: Segundo dentro do minuto em que o evento ocorreu (INTEGER).
        - **type**: Tipo de evento (e.g., Passe, Chute, Drible) (TEXT).
        - **possession_team**: Nome do time em posse da bola (TEXT).
        - **play_pattern**: Padrão de jogo que levou ao evento (e.g., Jogo Regular, Lateral) (TEXT).
        - **team**: Nome do time realizando o evento (TEXT).
        - **player**: Nome do jogador envolvido no evento (TEXT).
        - **position**: Posição do jogador no campo (e.g., Ponta Direita) (TEXT).
        - **location**: Coordenadas [x, y] indicando onde o evento ocorreu no campo (ARRAY).
        """,
        "Dribbles": """
        **Dribbles**
        Contém dados específicos relacionados aos eventos de dribles extraídos da tabela de eventos.

        - **id**: Identificador único para o evento de drible (TEXT, Primary Key).
        - **index**: Índice sequencial do evento dentro da partida (INTEGER).
        - **period**: Período da partida em que o drible ocorreu (INTEGER).
        - **minute**: Minuto da partida em que o drible ocorreu (INTEGER).
        - **team**: Nome do time que realizou o drible (TEXT).
        - **player**: Nome do jogador que realizou o drible (TEXT).
        - **location**: Coordenadas [x, y] onde o drible ocorreu (ARRAY).
        """,
        "360 Metrics": """
        **360 Metrics**
        Contém métricas 360 graus para eventos, proporcionando contexto adicional, como posições dos jogadores e passes que quebram linhas.

        - **id**: Identificador único para o evento (TEXT, Primary Key).
        - **index**: Índice sequencial do evento dentro da partida (INTEGER).
        - **minute**: Minuto da partida em que o evento ocorreu (INTEGER).
        - **possession_team**: Nome do time em posse da bola durante o evento (TEXT).
        - **team**: Nome do time realizando o evento (TEXT).
        - **player**: Nome do jogador envolvido no evento (TEXT).
        - **location**: Coordenadas [x, y] indicando onde o evento ocorreu (ARRAY).
        """,
        "360 Frames": """
        **360 Frames**
        Contém dados de frames 360 graus, fornecendo o contexto espacial dos jogadores durante os eventos.

        - **event_uuid**: Identificador único do evento associado ao frame (TEXT, Foreign Key para Events).
        - **match_id**: Identificador da partida em que o frame ocorreu (INTEGER, Foreign Key para Matches).
        - **actor**: Indica se o jogador é o ator (realizando o evento) (BOOLEAN).
        - **keeper**: Indica se o jogador é o goleiro (BOOLEAN).
        - **teammate**: Indica se o jogador é um companheiro de equipe do ator (BOOLEAN).
        - **location**: Coordenadas [x, y] do jogador durante o frame (ARRAY).
        """,
        "Aggregated Stats (Player Match Stats)": """
        **Aggregated Stats (Player Match Stats)**
        Contém estatísticas agregadas para os jogadores no nível de partidas.

        - **player_id**: Identificador único para o jogador (INTEGER, Foreign Key para Players).
        - **player_name**: Nome do jogador (TEXT).
        - **match_id**: Identificador da partida (INTEGER, Foreign Key para Matches).
        - **player_match_goals**: Número de gols marcados pelo jogador na partida (INTEGER).
        - **player_match_assists**: Número de assistências feitas pelo jogador na partida (INTEGER).
        - **player_match_shots**: Total de chutes realizados pelo jogador na partida (INTEGER).
        """,
        "Aggregated Stats (Team Match Stats)": """
        **Aggregated Stats (Team Match Stats)**
        Contém estatísticas agregadas para os times no nível de partidas.

        - **team_id**: Identificador único para o time (INTEGER, Primary Key).
        - **team_name**: Nome do time (TEXT).
        - **match_id**: Identificador da partida (INTEGER, Foreign Key para Matches).
        - **team_match_goals**: Total de gols marcados pelo time na partida (INTEGER).
        - **team_match_passes**: Total de passes tentados pelo time na partida (INTEGER).
        """
    }
    
    return descricoes.get(tabela_nome, "Descrição não disponível.")


def run():
    # Interface principal
    st.title("Análise de Dados de Futebol com Streamlit")
    st.write("Esse aplicativo permite visualizar e explorar dados de futebol usando diferentes tabelas.")

    # Selecionar tabela para visualizar
    tabela_selecionada = st.selectbox("Selecione uma tabela para visualizar:", ["Competitions", "Matches", "Lineups", "Events", "Dribbles", "360 Metrics", "360 Frames", "Aggregated Stats (Player Match Stats)", "Aggregated Stats (Team Match Stats)"])

    # Mostrar descrição da tabela selecionada
    st.subheader(f"Descrição da Tabela: {tabela_selecionada}")
    st.write(mostrar_descricao_tabela(tabela_selecionada))

if __name__ == "__main__":
    run()