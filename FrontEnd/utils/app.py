
import streamlit as st
import os
from dotenv import load_dotenv
#from components.msal_st import msal_st
import config
from utils.features import access_data, save_data
import base64

load_dotenv()

def get_base64_of_bin_file(bin_file) -> base64:
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()


def set_top_padding():
    st.markdown(
        """
        <style>
            section.main > .block-container {
                padding-top: 30px;
            }
        </style>
        """, unsafe_allow_html=True,
    )


def hide_sidebar_button() -> None:
    st.markdown(
        f"""
        <style>
            [data-testid="collapsedControl"] {{
                display: none; 
            }}
        </style>
        """, unsafe_allow_html=True
    )


@st.cache_data
def add_sidebar_logo(image_path):
    encoded_image = get_base64_of_bin_file(image_path)

    st.markdown(
        f"""
        <style>
            [data-testid="stSidebarNav"] {{
                background-image: url('data:image/png;base64,{encoded_image}');
                background-repeat: no-repeat;
                padding-top: 140px;
                background-position: center -40px;
                background-size: 300px auto;
            }}
        </style>
        """, unsafe_allow_html=True
    )


def add_sidebar_logout_button():
    if st.sidebar.button('Sair'):
        del st.session_state.access_token
        del st.session_state.user
        del st.session_state.name

        st.session_state.layout = 'centered'
        st.session_state.sidebar_state = 'collapsed'

        st.rerun()


def set_page_background(image_path):
    encoded_image = get_base64_of_bin_file(image_path)

    st.markdown(
        f"""
        <style>
            [data-testid="stAppViewContainer"] {{
                background-image: url("data:image/png;base64,{encoded_image}");
                background-color : rgba(0, 0, 0, 0);
                background-size: cover;
            }}
           
            [data-testid="stForm"] {{
                background-color : rgba(255, 255, 255, 0.65);
                background-size: cover;
            }}
            
            [data-testid="stHeader"] {{
                background-color : rgba(0, 0, 0, 0);
                background-size: cover;
            }}
        </style>
        """, unsafe_allow_html=True
    )


def find_user(user):
    data = access_data()
    if user not in data['users'].keys():
        return None
    else:
        return user


def create_user(user):
    #data = access_data()
    #data['users'][user] = {'chats': {}}
    #save_data(data)
    return



def run_app(page):
    if 'layout' not in st.session_state:
        st.session_state.layout = 'centered'
    
    if 'sidebar_state' not in st.session_state:
        st.session_state.sidebar_state = 'collapsed'

    if 'terms_accepted' not in st.session_state:
        st.session_state.terms_accepted = False

    # Definir um usuário padrão na sessão
    if 'user' not in st.session_state:
        st.session_state.user = 'default_user'
        create_user(st.session_state.user)
        st.session_state.layout = 'wide'
        st.session_state.sidebar_state = 'expanded'
    
    if 'name' not in st.session_state:
        st.session_state.name = 'Default User'
        
    st.set_page_config(
        page_title=config.PAGE_TITLE,
        page_icon=config.PAGE_ICON,
        layout=st.session_state.layout,
        initial_sidebar_state=st.session_state.sidebar_state,
        menu_items=None
    )

    set_top_padding()
    add_sidebar_logo(config.SIDEBAR_LOGO_IMG)
    
    page()
