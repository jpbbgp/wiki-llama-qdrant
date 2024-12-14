import streamlit as st
from components.custom_table import custom_table
import requests
import json
import config
import os
from streamlit_antd_components.widgets.transfer import transfer

from utils.app import run_app

# Defina o caminho padrão onde os arquivos serão salvos
default_path = "uploads/"
aws_bucket = ""



# Crie o diretório se ele não existir
if not os.path.exists(default_path):
    os.makedirs(default_path)

def push_env_aws(aws_region, aws_access_key, aws_secret_key, aws_bucket):
    response = requests.post(url=config.API_URL+"/set_aws_credentials", json={"bucket_name": aws_bucket, "aws_region_name": aws_region, "aws_access_key_id": aws_access_key, "aws_secret_access": aws_secret_key })
    response_dict = response.json()  # Converte a resposta JSON para um dicionário
    # Extraia o valor do campo 'message'
    message_value = response_dict.get('message')
    if message_value == 'True':
        return True
    else:
        return False

def local_option():
    uploaded_files = st.file_uploader("Escolha os arquivos", accept_multiple_files=True, type=["html", "md"])
    if uploaded_files:
        for uploaded_file in uploaded_files:
            st.write(uploaded_file)
            # Salve o arquivo no diretório especificado
            with open(os.path.join(default_path, uploaded_file.name), "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"Arquivo {uploaded_file.name} salvo com sucesso em {default_path}!")


def page_import_files():
    
    global aws_bucket
    
    st.title('Importar Arquivos')
    
    option = st.selectbox(
        "Qual a origem dos arquivos?",
        ("Local", "AWS", "Drive"),
    )
    if option == "Local":
        local_option()
    elif option == "AWS":
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
        
        
        if not st.session_state['tem_variavel_aws']:
            st.error("Atenção! Variáveis de ambiente da AWS não configuradas. Por favor, configure as variáveis de ambiente para acessar os arquivos de origem AWS.")
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
                    st.session_state['available_files'] = []
                    st.session_state['selected_files'] = []
                    st.session_state['tem_variavel_aws'] = None
                    st.rerun(scope="app")
        elif st.session_state['tem_variavel_aws']:
            
            aws_bucket_2 = st.text_input("Digite o nome do Bucket da AWS", value=aws_bucket)
            col1, col2 = st.columns(2)
            with col1:
                buscar_button = st.button("Buscar", help="Clique para buscar os arquivos do Bucket da AWS")
            with col2:
                reset_aws = st.button("Reinserir Credenciais AWS", help="Clique para inserir as credenciais de uma conta AWS diferete.")

            if buscar_button:
                st.session_state['available_files'] = []
                st.session_state['selected_files'] = []
                if aws_bucket_2 != aws_bucket:
                    aws_bucket = aws_bucket_2
                    response = requests.post(url=config.API_URL+"/set_aws_bucket", json={"name": aws_bucket})
                    response_dict = response.json()
                    message_value = response_dict.get('message')
                    if message_value == 'True':
                        st.success(f"Bucket {aws_bucket} configurado com sucesso!")
                    else:
                        st.error(f"Erro ao configurar o Bucket {aws_bucket}")
                response = requests.get(url=config.API_URL+"/list_files_s3")
                response_dict = response.json()
                message_value = response_dict.get('message')
                
                if isinstance(message_value, list):
                    st.session_state['available_files'] = message_value
                    st.session_state['selected_files'] = []
                
            elif reset_aws:
                response = requests.delete(url=config.API_URL+"/clear_aws_env_variables")
                st.session_state['tem_variavel_aws'] = False
                aws_bucket = ""
                st.session_state['available_files'] = []
                st.session_state['selected_files'] = []
                st.rerun(scope="app")
            if 'available_files' in st.session_state and st.session_state['available_files'] != []:
                st.write("Arquivos disponíveis e selecionados:")
                selected_files = transfer(
                    items=st.session_state['available_files'],
                    titles=["Disponíveis", "Selecionados"],
                    search=True,
                    pagination=False,
                    reload='reload data',
                    align='center',
                    width=400,
                    height=400,
                    oneway=False,
                    key="transfer"
                )
                st.session_state['selected_files'] = selected_files
                
                btn_save_all, btn_save = st.columns(2)
                with btn_save_all:
                    if st.button("Salvar todos", help="Clique para salvar todos os arquivos selecionados"):
                        response = requests.post(url=config.API_URL+"/download_all_from_s3")
                        response_dict = response.json()
                        message_value = response_dict.get('message')
                        if message_value == 'True':
                            st.success("Arquivos salvos com sucesso!")
                        else:
                            st.error("Erro ao salvar os arquivos.")
                with btn_save:
                    if st.button("Salvar", help="Clique para salvar os arquivos selecionados"):
                        response = requests.post(url=config.API_URL+"/download_from_s3", json={"names": st.session_state['selected_files']})
                        response_dict = response.json()
                        message_value = response_dict.get('message')
                        if message_value == 'True':
                            st.success("Arquivos salvos com sucesso!")
                        else:
                            st.error("Erro ao salvar os arquivos.")
                if 'selected_files' in st.session_state:
                    st.write("Arquivos selecionados:")
                    st.write(st.session_state['selected_files'])

def main():
    page_import_files()

if __name__ == "__main__":
    run_app(main)