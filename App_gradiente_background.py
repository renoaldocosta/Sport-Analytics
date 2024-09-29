import streamlit as st
from app.Scripts.sidebar import sidebar
import os
import sys
import importlib  # Serve para importar módulos dinamicamente

Project_name = "Sport Analytics"

st.set_page_config(
    page_title=Project_name,
    # page_icon="./app/assets/image/favicon_64_64.png",  # Atualize o caminho se necessário
    layout="wide"  # Define o layout como 'wide' por padrão
)

# Atualiza o caminho da pasta de páginas para 'pages'
pages_dir = os.path.join('app', 'pages')
sys.path.append(pages_dir)

def load_css():
    """Função para injetar CSS para ocultar elementos e definir estilos."""
    css = """
        <style>
        /* Ocultar o menu principal do Streamlit */
        /*#MainMenu {visibility: hidden;} */
        /* Ocultar o cabeçalho inteiro */
        /*header {visibility: hidden;} */
        
        /* Define a cor de fundo da sidebar */
        .css-1d391kg {background-color: transparent;}  /* Torna a sidebar transparente */
        /* Ocultar a navegação automática de páginas do Streamlit */
        [data-testid="sidebar-nav"] {display: none;}

        /* Fonte personalizada */
        body, button, input, textarea {
            font-family: 'Arial', sans-serif;
        }

        /* Estilização de títulos */
        .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {
            color: #FFFFFF;  /* Preto Sofisticado 343A40*/
            text-align: center;
        }

        /* Botões personalizados */
        .stButton button {
            background-color: #007BFF;  /* Azul Elétrico */
            color: white;
            border-radius: 10px;
            border: none;
            padding: 10px 20px;
            transition: background-color 0.3s;
        }

        .stButton button:hover {
            background-color: #0056b3;  /* Azul mais escuro no hover */
        }

        /* Links personalizados */
        a {
            color: #007BFF;  /* Azul Elétrico */
            text-decoration: none;
        }

        a:hover {
            color: #0056b3;  /* Azul mais escuro no hover */
            text-decoration: underline;
        }

        /* Barra de Progresso personalizada */
        .stProgress > div > div > div > div {
            background-color: #28A745;  /* Verde Dinâmico */
        }

        /* Estilização das tabelas */
        .stDataFrame thead th {
            background-color: #007BFF;  /* Azul Elétrico */
            color: white;
        }

        .stDataFrame tr:nth-child(even) {
            background-color: #f2f2f2;
        }

        /* Estilização de gráficos Plotly */
        .plotly .main-svg path {
            stroke: #007BFF;  /* Azul Elétrico */
        }

        /* Estilização dos elementos da sidebar */
        .sidebar .sidebar-content {
            background-color: transparent;  /* Torna a sidebar transparente */
        }

        /* Customização do Option Menu */
        [data-testid="option_menu"] .option-menu-item-selected {
            background-color: #007BFF;  /* Azul Elétrico */
            color: white;
        }

        [data-testid="option_menu"] .option-menu-item {
            color: #343A40;  /* Preto Sofisticado */
        }

        [data-testid="option_menu"] .option-menu-item:hover {
            background-color: #6C757D;  /* Cinza Aço */
            color: white;
        }

        /* Badges e etiquetas */
        .badge {
            background-color: #28A745;  /* Verde Dinâmico */
            color: white;
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 0.8em;
        }

        /* Animação de gradiente de fundo */
        .stApp {
            background: linear-gradient(45deg, #007BF0, #28A745);
            background-size: 400% 400%;
            animation: gradient 15s ease infinite;
            min-height: 100vh;
        }

        @keyframes gradient {
            0% {
                background-position: 0% 50%;
            }
            50% {
                background-position: 100% 50%;
            }
            100% {
                background-position: 0% 50%;
            }
        }
        </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def load_page(module_name):
    """Função para carregar dinamicamente um módulo de página."""
    try:
        imported_module = importlib.import_module(module_name)
        if hasattr(imported_module, 'run'):
            imported_module.run()
        else:
            st.write(f"O módulo '{module_name}' não possui uma função 'run()'.")
    except ModuleNotFoundError:
        st.error(f"Módulo '{module_name}' não encontrado em '{pages_dir}'.")
    except Exception as e:
        st.error(f"Erro ao carregar o módulo '{module_name}': {e}")

def list_pages_directory():
    """Função para listar os arquivos no diretório de páginas para depuração."""
    try:
        files = os.listdir(pages_dir)
        st.write("Arquivos disponíveis em 'paginas':", files)
    except Exception as e:
        st.error(f"Erro ao listar diretório 'paginas': {e}")

def run():
    load_css()
    selected_page, pages = sidebar()
    #st.title(Project_name)
    if selected_page == "Introdução":
        import introducao
        introducao.run()
    else:
        # Obtenha o nome do módulo a partir do dicionário de páginas
        module_name = pages[selected_page]
        load_page(module_name)

if __name__ == "__main__":
    run()
