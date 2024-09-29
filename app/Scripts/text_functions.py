import streamlit as st


def mkd_text_divider(text: str, level: str = 'title', position: str = 'center'):
    """
    Function to write titles, headers, and subheaders, centered or not.

    Parameters:
    text (str): The text to be displayed.
    level (str): Text level ('title', 'header', 'subheader').
    position (str): Text position ('center' for centered, 'left' for left-aligned).
    """
    # Dynamically get the selected color from session_state
    text_color = st.session_state.get("text_color", "#000000")  # Default to black if not defined
    col = st.columns([0.3, 0.4, 0.3])
    with col[0]:
        st.divider()
    with col[1]:
        if position == 'center':
            html_tag = {
                'title': 'h1',
                'header': 'h2',
                'subheader': 'h3',
                'h4': 'h4',
                'h5': 'h5',
                'h6': 'h6',
                'h7': 'h7',
                'p': 'p',
            }.get(level, 'h1')  # Default to 'h1' if the level is not recognized
            st.markdown(
                f"<{html_tag} style='text-align: center; color: {text_color};'>{text}</{html_tag}>", 
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"<{html_tag} style='text-align: left; color: {text_color};'>{text}</{html_tag}>", 
                unsafe_allow_html=True
            )
        with col[2]:
            st.divider()


def mkd_text(text: str, level: str = 'title', position: str = 'center'):
    """
    Function to write titles, headers, and subheaders, centered or not.

    Parameters:
    text (str): The text to be displayed.
    level (str): Text level ('title', 'header', 'subheader').
    position (str): Text position ('center' for centered, 'left' for left-aligned).
    """
    # Dynamically get the selected color from session_state
    text_color = st.session_state.get("text_color", "#000000")  # Default to black if not defined

    if position == 'center':
        html_tag = {
            'title': 'h1',
            'header': 'h2',
            'subheader': 'h3',
            'h4': 'h4',
            'h5': 'h5',
            'h6': 'h6',
            'h7': 'h7',
            'p': 'p',
        }.get(level, 'h1')  # Default to 'h1' if the level is not recognized
        st.markdown(
            f"<{html_tag} style='text-align: center; color: {text_color};'>{text}</{html_tag}>", 
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"<{html_tag} style='text-align: left; color: {text_color};'>{text}</{html_tag}>", 
            unsafe_allow_html=True
        )


def mkd_paragraph(text: str, position: str = 'justify'):
    """
    Function to write paragraphs, centered or not.

    Parameters:
    text (str): The text to be displayed.
    position (str): Text position ('center' for centered, 'left' for left-aligned).
    """
    if position == 'center':
        st.markdown(f"<p style='text-align: center;'>{text}</p>", unsafe_allow_html=True)
    else:
        st.markdown(f"<p style='text-align: justify;'>{text}</p>", unsafe_allow_html=True)
