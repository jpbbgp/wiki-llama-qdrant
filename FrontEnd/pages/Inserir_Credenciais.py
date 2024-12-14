import streamlit as st
from components.custom_table import custom_table
import requests
import json
import config
import os

from utils.app import run_app


def page_set_env():
    st.session_state['current_page'] = st.session_state.get('current_page', 'Inserir_Credenciais.py')
    st.session_state['previous_page'] = st.session_state.get('previous_page', 'Inserir_Credenciais.py')
    st.title('Inserir Credenciais')
    if st.session_state['current_page'] != "Inserir_Credenciais.py":
        
        response_tem_OpenAI_API = requests.get(url=config.API_URL+"/get_exist_API_Key")
        response_api_key = response_tem_OpenAI_API.json()
        st.session_state['tem_openAI_key'] = response_api_key.get('message')
        response_tem_Qdrant = requests.get(url=config.API_URL+"/get_exist_Qdrant_env")
        response_Qdrant = response_tem_Qdrant.json()
        st.session_state['tem_env_Qdrant'] = response_Qdrant.get('message')
        st.session_state['previous_page'] = st.session_state['current_page']
        st.session_state['current_page'] = "Inserir_Credenciais.py"
    if st.session_state['previous_page'] != st.session_state['current_page']:
        previous_page = st.session_state['previous_page'].replace('.py', '')
        st.warning("Antes de começar a utilizar a página {0}, por favor, insira as credenciais necessárias.".format(previous_page))  
    if st.session_state.get('tem_openAI_key', 'False') == 'True':
        value_openAI_key = st.text_input("OpenAI Api Key já está cadastrada no sistema, atualize caso necessário abaixo:")
    else:
        value_openAI_key = st.text_input("Digite a OpenAI API Key:")
    
    if st.button("Inserir OpenAI API Key", help="Clique para configurar a chave da OpenAI"):
        if not value_openAI_key:
            st.error("Por favor, insira a OpenAI API Key.")
        else:
            result_set = requests.post(url=config.API_URL+"/set_api_key", json={"openai_api_key": value_openAI_key})
            response_dict = result_set.json()
            if response_dict.get('message') == 'True':
                st.success("Chave da OpenAI inserida/atualizada com sucesso!")
                st.session_state['tem_openAI_key'] = 'True'
                
    if st.session_state.get('tem_env_Qdrant', 'False') == 'True':
    #    value_qdrant_collection = st.text_input("A Collection do Qdrant já está cadastrada no sistema, atualize caso necessário abaixo:")
    #    if st.button("Atualizar Somente o nome do Collection Name", help="Clique para atualizar somente o nome do Collection do Qdrant"):
    #        if not value_qdrant_collection:
    #            st.error("Por favor, insira o nome da Collection do Qdrant.")
    #        else:
    #            result_set = requests.post(url=config.API_URL+"/set_collection_name", json={"name": value_qdrant_collection})
    #           response_dict = result_set.json()
    #            if response_dict.get('message') == 'True':
    #                st.success("Nome do Collection Name do Qdrant atualizado com sucesso!")
        value_qdrant_url = st.text_input("A URL do Qdrant já está cadastrada no sistema, atualize caso necessário abaixo:")
        value_qdrant_key = st.text_input("A API Key do Qdrant já está cadastrada no sistema, atualize caso necessário abaixo:")
    else:
    #    value_qdrant_collection = st.text_input("Digite o nome da Collection do Qdrant:")   
        value_qdrant_url = st.text_input("Digite a URL do Qdrant:")
        value_qdrant_key = st.text_input("Digite a API Key do Qdrant:")
    
    if st.button("Inserir variáveis do Qdrant", help="Clique para configurar as variáveis do Qdrant"):
        if not value_qdrant_url or not value_qdrant_key:
            st.error("Por favor, preencha todas as variáveis do Qdrant.")
        else:
            value_qdrant_collection = "wiki"
            result_set = requests.post(url=config.API_URL+"/set_qdrant_variables", json={"collection_name": value_qdrant_collection, "qdrant_url": value_qdrant_url, "qdrant_api_key": value_qdrant_key})
            response_dict = result_set.json()
            if response_dict.get('message') == 'True':
                st.session_state['tem_env_Qdrant'] = 'True'
                st.success("Chaves do Qdrant inseridas com sucesso!")

def main():
    page_set_env()
    last_page = st.session_state.get('previous_page', 'Inserir_Credenciais.py')
    has_openAI = st.session_state.get('tem_openAI_key', 'False')
    has_Qdrant = st.session_state.get('tem_env_Qdrant', 'False')
    if has_openAI == 'True' and has_Qdrant == 'True' and last_page != 'Inserir_Credenciais.py':
        st.session_state['previous_page'] = 'Inserir_Credenciais.py'
        st.switch_page('pages/{0}'.format(last_page))

if __name__ == "__main__":
    run_app(main)