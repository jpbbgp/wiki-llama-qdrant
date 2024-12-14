import streamlit as st
from dotenv import load_dotenv
import config
import uuid
from utils.app import run_app
from utils.features import access_data, save_data
import requests
from json import loads
import json
from datetime import datetime
import re
import markdown2
import pdfkit
import tempfile
import io
#from streamlit_feedback import streamlit_feedback
import pandas as pd
#from llama_index.core.memory import ChatMemoryBuffer
load_dotenv()



def create_new_chat():
    del st.session_state.chat_id
    del st.session_state.response
    del st.session_state.memory
    st.rerun()


def create_chat():
    if 'chats' not in st.session_state:
        st.session_state.chats = {}

    chat_id = str(uuid.uuid4())
    st.session_state.chat_id = chat_id

    st.session_state.chats[chat_id] = {
        'start_date': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
        'last_interaction_date': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
        'summary': 'Esse chat ainda está sem resumo, continue conversando!',
        'summary_used_messages': 0,
        'tags': '',
        'title': '',
        'messages': [
            {
                'role': 'assistant',
                'content': 'O que você gostaria de saber hoje?',
                'feedback': {
                    'score': None,
                    'text': None,
                }
            }
        ]
    }


def get_chat():
    return st.session_state.chats[st.session_state.chat_id]


def display_chat_messages(messages):
    for message in messages:
        avatar = config.CHAT_IA_IMG if message['role'] == 'assistant' else config.CHAT_USER_IMG
        with st.chat_message(message['role'], avatar=avatar):
            st.write(message['content'])


def add_message_to_history(role, content):
    chat = st.session_state.chats[st.session_state.chat_id]
    message = {'role': role, 'content': content}
    chat['messages'].append(message)
    chat['last_interaction_date'] = datetime.now().strftime('%d/%m/%Y %H:%M:%S')


def load_question(question):
    st.chat_message('user', avatar=config.CHAT_USER_IMG).write(question)
    add_message_to_history('user', question)


def remove_noise_from_context(text):
    text = re.sub(r'^### (.*)', r'#### \1', text, flags=re.MULTILINE)
    
    text = re.sub(r'^## (.*)', r'### \1', text, flags=re.MULTILINE)

    text = re.sub(r'^# (.*)', r'## \1', text, flags=re.MULTILINE)

    text = re.sub(r'^---\s*$', '', text, flags=re.MULTILINE)
    
    return text


def load_context():
    with st.popover('Contexto'):
        st.subheader('Contexto')
        if st.session_state.response == []:
            st.write('Nenhum documento foi retornado.')
        


def load_response(question):
    placeholder = st.empty()
    api_data = {}
    print(question)
    if 'chat_mode' not in st.session_state:
        st.session_state.chat_mode = 'Wiki'
    
    api_data = {
        "question": question,
        "collection": st.session_state.chat_mode.lower()
    }
    
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }

    response = requests.post(url=config.API_QUESTION, headers=headers, data=json.dumps(api_data))
    streaming_response = loads(response.content.decode())
    print(streaming_response)
    
    placeholder.write(streaming_response)
    add_message_to_history('assistant', streaming_response)
    st.session_state.last_trace = streaming_response
    st.session_state.memory.append({
        "role": "user",
        "content": question
    }
    )
    st.session_state.memory.append({
        "role" : "assistant",
        "content" : streaming_response
    })        

    return streaming_response

def reset_feedback():
    del st.session_state.response


def main():
    has_openAI = st.session_state.get('tem_openAI_key', 'False')
    has_Qdrant = st.session_state.get('tem_env_Qdrant', 'False')
    if has_openAI == 'False' or has_Qdrant == 'False':
        st.warning("Atenção! Variáveis de ambiente da OpenAI ou Qdrant não configuradas. Por favor, configure as variáveis de ambiente para processar os arquivos.")
        st.session_state['current_page'] = "Chat.py"
        st.switch_page('pages/Inserir_Credenciais.py')
    if 'user' in st.session_state:
        print(st.session_state['user'])    
    st.title(config.CHAT_TITLE) 

    if 'chat_id' not in st.session_state:
        create_chat()

    if 'memory' not in st.session_state:
        st.session_state.memory = []
    
    if 'last_trace' not in st.session_state:
        st.session_state.last_trace = None
    
    if 'response' not in st.session_state:
        st.session_state.response = None

    collec_names = ["Wiki", "Local", "Aws"]
    
    with st.sidebar:
        chat_mode = st.selectbox(
            label='Nome da Coleção de Dados',
            key='chat_mode',
            options=collec_names,
            help='Selecione um nome da coleção de dados para o Chatbot.'
        )

    if st.sidebar.button('+ Novo Chat', type='primary'):
        create_new_chat()
    
    
    chat = get_chat()

    display_chat_messages(chat['messages'])

    if question := st.chat_input('Sua pergunta'):
        load_question(question)
        with st.chat_message('assistant', avatar=config.CHAT_IA_IMG):    
            st.session_state.response = load_response(question)

    


if __name__ == '__main__':
    run_app(main)