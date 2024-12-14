import streamlit as st
from components.custom_table import custom_table
import requests
import json
import config
import os

from utils.app import run_app


def push_env_aws(aws_region, aws_access_key, aws_secret_key, aws_bucket):
    response = requests.post(url=config.API_URL+"/set_aws_credentials", json={"bucket_name": aws_bucket, "aws_region_name": aws_region, "aws_access_key_id": aws_access_key, "aws_secret_access": aws_secret_key })
    response_dict = response.json()  # Converte a resposta JSON para um dicionário
    # Extraia o valor do campo 'message'
    message_value = response_dict.get('message')
    if message_value == 'True':
        return True
    else:
        return False

def reset_session():
    st.session_state['files_downloaded'] = None
    st.session_state['files_local'] = None
    st.session_state['files_wiki'] = None

def check_env_aws():
    if 'tem_variavel_aws' not in st.session_state or st.session_state['tem_variavel_aws'] is None:
        response = requests.get(url=config.API_URL+"/get_status_env_aws")
        response_dict = response.json()  # Converte a resposta JSON para um dicionário
        # Extraia o valor do campo 'message'
        message_value = response_dict.get('message')
        aws_bucket = response_dict.get('bucket_name')
        if message_value == 'False':
            st.session_state['tem_variavel_aws'] = False
        else:
            st.session_state['tem_variavel_aws'] = True

def block_btn():
    select_aws_images = st.session_state.get('select_aws_images', 'Não')
    if select_aws_images == "Sim":
        check_env_aws()
        if st.session_state['tem_variavel_aws'] == False:
            st.session_state['act_btn_proc'] = False
            
def page_process_files():
    st.title('Processar Arquivos')
    
    st.write('Aqui você pode processar arquivos para serem utilizados no chatbot')
    options = ["Arquivos Somente Baixados", "Arquivos Processados"]
    selection = st.segmented_control(
        "Status Arquivos:", options, selection_mode="single", default=options[0]
    )
    if selection == options[0]:
        options_wiki_aws_local = ["Arquivos Wiki", "Arquivos Locais", "Arquivos AWS"]
        select_wiki_aws_local = st.segmented_control(
            "Origem Arquivos:", options_wiki_aws_local, selection_mode="single", default=options_wiki_aws_local[0], on_change=reset_session)
        if select_wiki_aws_local == options_wiki_aws_local[0]:
            options_auto = ["Não", "Sim"]
            select_recorrente = st.segmented_control(
                "Processar automaticamente novos arquivos da Wiki?", 
                options=options_auto,
                selection_mode="single",
                default=options_auto[0],
                key='select_recorrente'
            )  
        elif select_wiki_aws_local == options_wiki_aws_local[2]:
            options_aws_images = ["Não", "Sim"]
            select_aws_images = st.segmented_control(
                "Seus Arquivos Possuem Referência a Imagens Armazenadas no S3 da AWS?", 
                options=options_aws_images,
                selection_mode="single",
                default=options_aws_images[0],
                key='select_aws_images',
                on_change=block_btn
            )
            if select_aws_images == options_aws_images[0]:
                st.session_state['act_btn_proc'] = True
            
        if (select_wiki_aws_local == options_wiki_aws_local[2]) and ('act_btn_proc' not in st.session_state or st.session_state['act_btn_proc'] is None or st.session_state['act_btn_proc'] == False):
            btn_proc = st.button("Processar Arquivos", disabled=True)
        else:
            btn_proc = st.button("Processar Arquivos", disabled=False)
        if btn_proc:
            if select_wiki_aws_local == options_wiki_aws_local[2] and select_aws_images == options_aws_images[1]:
                with st.spinner('Processando Arquivos, Aguarde!'):
                    response = requests.post(url=config.API_URL+"/process_files_aws")
                    response_dict = response.json()
                    message_value = response_dict.get('message')
                if message_value == 'True':
                    st.success("Arquivos de origem AWS processados com sucesso!")
                else:
                    st.error("Erro ao processar os arquivos de origem AWS.")
            else:
                if select_wiki_aws_local == options_wiki_aws_local[0]:
                    if select_recorrente == options_auto[0]:
                        response = requests.post(url=config.API_URL+"/process_files_basic", json={"collection": "wiki", "recorrente": "False"})
                    else:
                        response = requests.post(url=config.API_URL+"/process_files_basic", json={"collection": "wiki", "recorrente": "True"})
                elif select_wiki_aws_local == options_wiki_aws_local[1]:
                    response = requests.post(url=config.API_URL+"/process_files_basic", json={"collection": "local", "recorrente": "False"})
                else:
                    response = requests.post(url=config.API_URL+"/process_files_basic", json={"collection": "aws", "recorrente": "False"})
                response_dict = response.json()
                message_value = response_dict.get('message')
                if message_value == 'True':
                    st.success("Arquivos processados com sucesso!")
                else:
                    st.error("Erro ao processar os arquivos. Erro: {0}".format(message_value))
        if select_wiki_aws_local == options_wiki_aws_local[2]:
            if select_aws_images == options_aws_images[1]:
                if 'tem_variavel_aws' not in st.session_state or st.session_state['tem_variavel_aws'] is None:
                    st.session_state['act_btn_proc'] = False
                    response = requests.get(url=config.API_URL+"/get_status_env_aws")
                    response_dict = response.json()  # Converte a resposta JSON para um dicionário
                    # Extraia o valor do campo 'message'
                    message_value = response_dict.get('message')
                    aws_bucket = response_dict.get('bucket_name')
                    if message_value == 'False':
                        st.session_state['tem_variavel_aws'] = False
                    else:
                        st.session_state['tem_variavel_aws'] = True
                    
                if not st.session_state['tem_variavel_aws']:
                    st.session_state['act_btn_proc'] = False
                    st.warning("Atenção! Variáveis de ambiente da AWS não configuradas. Por favor, configure as variáveis de ambiente para processar os arquivos de origem AWS.")
                    aws_region = st.selectbox("Selecione a região da AWS:", config.LISTA_REGIOES_AWS)
                    aws_access_key = st.text_input("Insira o Access Key da AWS")
                    aws_secret_key = st.text_input("Insira o Secret Key da AWS")
                    aws_bucket = st.text_input("Insira o Bucket da AWS")
                    if st.button("Salvar", help="Clique para salvar as variáveis de ambiente da AWS"):
                        if not aws_region or not aws_access_key or not aws_secret_key or not aws_bucket:
                            st.error("Todos os campos são obrigatórios. Por favor, preencha todas as informações.")
                        else:
                            push_env_aws(aws_region, aws_access_key, aws_secret_key, aws_bucket)
                            st.success("Variáveis de ambiente da AWS salvas com sucesso!")
                            st.session_state['act_btn_proc'] = True
                            st.session_state['tem_variavel_aws'] = True
                            st.rerun(scope="app")
            if 'files_downloaded' not in st.session_state or st.session_state['files_downloaded'] is None:
                files_response = requests.get(url=config.API_URL+"/get_files_downloaded")
                response_files_dict = files_response.json()
                files_value = response_files_dict.get('message')
                st.session_state['files_downloaded'] = files_value
                s = ""
                for i in st.session_state['files_downloaded']:
                    s += "- " + i + "\n"
            
                st.markdown(s)
            else:
                s = ""
                for i in st.session_state['files_downloaded']:
                    s += "- " + i + "\n"
                st.markdown(s)
        elif select_wiki_aws_local == options_wiki_aws_local[1]:
            if 'files_local' not in st.session_state or st.session_state['files_local'] is None:
                files_response = requests.get(url=config.API_URL+"/get_files_local")
                response_files_dict = files_response.json()
                files_value = response_files_dict.get('message')
                st.session_state['files_local'] = files_value
                s = ""
                for i in st.session_state['files_local']:
                    s += "- " + i + "\n"
            
                st.markdown(s)
            else:
                s = ""
                for i in st.session_state['files_local']:
                    s += "- " + i + "\n"
                st.markdown(s)
        else:
            if 'files_wiki' not in st.session_state or st.session_state['files_wiki'] is None:
                files_response = requests.get(url=config.API_URL+"/get_files_wiki")
                response_files_dict = files_response.json()
                files_value = response_files_dict.get('message')
                st.session_state['files_wiki'] = files_value
                s = ""
                for i in st.session_state['files_wiki']:
                    s += "- " + i + "\n"
            
                st.markdown(s)
            else:
                s = ""
                for i in st.session_state['files_local']:
                    s += "- " + i + "\n"
                st.markdown(s)
    else:
        proc_response = requests.get(url=config.API_URL+"/get_files_processed")
        response_proc_dict = proc_response.json()
        proc_value = response_proc_dict.get('message')
        
        s = ""
        if proc_value is not None and proc_value:
            st.write("Arquivos processados e disponíveis para serem utilizados no ChatBot:")
            for i in proc_value:
                s += "- " + i + "\n"
            
        st.markdown(s)

def main():

    has_openAI = st.session_state.get('tem_openAI_key', 'False')
    has_Qdrant = st.session_state.get('tem_env_Qdrant', 'False')
    if has_openAI == 'False' or has_Qdrant == 'False':
        st.warning("Atenção! Variáveis de ambiente da OpenAI ou Qdrant não configuradas. Por favor, configure as variáveis de ambiente para processar os arquivos.")
        st.session_state['current_page'] = "Processar_Arquivos.py"
        st.session_state['current_page'] = "Processar_Arquivos.py"
        st.switch_page('pages/Inserir_Credenciais.py')
    page_process_files()

if __name__ == "__main__":
    run_app(main)