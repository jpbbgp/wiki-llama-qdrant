import streamlit as st
from utils.app import run_app
from pages.Chat import main as chat_main
import requests
import config

def logout():
    # Itera sobre todas as chaves em st.session_state e as remove
    for key in list(st.session_state.keys()):
        st.session_state.pop(key, None)
    st.session_state.layout = 'centered'
    st.session_state.sidebar_state = 'collapsed'
    requests.delete(url=config.API_URL+"/clear_env_variables")
    
    st.switch_page('index.py')

def main():
    logout()

if __name__ == '__main__':
    run_app(main)
