# app/pages/introducao.py

import streamlit as st


def run():
    # Título da Página
    st.title("⚽ Dashboard de Análise das Copas do Mundo")

    # Seção de Introdução
    st.markdown("""

    Este aplicativo foi desenvolvido para proporcionar uma análise detalhada e interativa das partidas das Copas do Mundo de Futebol. Utilizando dados reais obtidos através da biblioteca [StatsBombPy](https://github.com/statsbomb/statsbombpy) e visualizações avançadas com [mplsoccer](https://mplsoccer.readthedocs.io/en/latest/), o dashboard oferece uma variedade de informações e insights para técnicos, analistas, gestores e fãs do futebol.

    ### Objetivo do Projeto

    O principal objetivo deste projeto é demonstrar como a análise de dados pode ser aplicada ao futebol para:
    - **Analisar Desempenho de Jogadores:** Compare estatísticas individuais, como passes, chutes, desarmes e outros eventos importantes.
    - **Explorar Estatísticas de Partidas:** Visualize e interprete dados detalhados de cada partida, incluindo mapas de passes e chutes.
    - **Tomar Decisões Baseadas em Dados:** Forneça informações essenciais que auxiliem na tomada de decisões estratégicas e táticas.

    ### Funcionalidades Principais

    - **Filtro por Temporada e Partida:** Selecione a temporada e a partida específica que deseja analisar.
    - **Informações Detalhadas da Partida:** Exiba dados como data e horário, técnicos, locais, árbitros, placar e eventos ocorridos.
    - **Visualizações Interativas:** Utilize mapas de calor estáticos e customizáveis para uma melhor compreensão das dinâmicas da partida.
    - **Escalação dos Times:** Visualize a formação e os jogadores de cada equipe.
    - **Comparação de Jogadores:** Compare estatísticas de diferentes jogadores com gráficos de comparação sobrepostos.

    ### Por Que Utilizar Este Dashboard?

    Com o crescimento do mercado de **Sports Analytics**, este dashboard serve como uma ferramenta poderosa para:
    - **Técnicos e Analistas:** Avaliar o desempenho individual e coletivo para aprimorar estratégias.
    - **Gestores:** Tomar decisões informadas sobre contratações e treinamentos.
    - **Fãs e Entusiastas:** Obter insights profundos sobre suas equipes e jogadores favoritos.

    ### Explore e Analise!

    Utilize as opções interativas para explorar os dados das Copas do Mundo e descubra tendências, padrões e informações valiosas que podem transformar a forma como você entende o futebol. Além disso, é possivel descobrir algumas curiosidades, como por exemplo:
    

    """)
    st.markdown(f"<h3 style='color: green'>Durante a copa, Neymar realmente sofreu muita falta?</h3>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='color: green'><strong>Divirta-se explorando os dados! ⚽📊</strong></p>", unsafe_allow_html=True)