# app/Scripts/sidebar.py

import streamlit as st
from streamlit_option_menu import option_menu

def sidebar():
    # Dicionário que mapeia nomes de exibição para nomes de arquivos de script
    pages = {
        "Introdução": "introducao",
        "Copas do Mundo": "copas",
    }

    # Lista de ícones apropriados para cada página
    icons = [
        "house",      # Ícone de casa para "Introdução"
        "trophy",     # Ícone de troféu para "Copas do Mundo"
        "bar-chart",  # Ícone de gráfico de barras para "Conhecendo os Dados"
        "book"        # Ícone de livro para "Dicionário de Dados"
        
    ]

    with st.sidebar:
        selected_page = option_menu(
            "World Cup Analytics",         # Título do menu
            list(pages.keys()),       # Nomes de exibição das páginas
            icons=icons,              # Lista de ícones definidos acima
            menu_icon="bi-trophy",    # Ícone do menu principal
            default_index=0,          # Primeira opção selecionada por padrão
            styles={
                "container": {
                    "padding": "0!important",
                    "background-color": "#f0f2f6"  # Cor de fundo da sidebar (Cinza Claro)
                },
                "icon": {
                    "color": "#f0f2f6",  # Preto Sofisticado para ícones quando não selecionados
                    "font-size": "18px"  # Tamanho dos ícones
                },
                "icon-selected": {
                    "color": "#343A40",  # Preto Sofisticado para ícones quando não selecionados
                    "font-size": "18px"  # Tamanho dos ícones
                },
                "nav-link": {
                    "font-size": "16px",
                    "text-align": "left",
                    "margin": "0px",
                    "color": "#343A40",  # Preto Sofisticado para o texto dos links quando não selecionados
                    "--hover-color": "#f0f0f0"  # Cor ao passar o mouse
                },
                "nav-link-selected": {
                    "background": "linear-gradient(45deg, #007BF0, #28A745)",  # Gradiente para o fundo selecionado
                    "color": "#ffffff"  # Texto branco quando selecionado
                },
                # "icon-selected" não é suportado diretamente, será tratado via CSS
            },
        )
        st.session_state['active_page'] = selected_page
        return selected_page, pages
