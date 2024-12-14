import os

# Diretório raiz do projeto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


###################################################
#            Streamlit
###################################################

API_URL = 'http://fastapi:8000/api'
API_QUESTION = API_URL + '/question'


PAGE_ICON = os.path.join(BASE_DIR, 'resources/images/puc_brasao_icone_browser.png')

MSG_HOW_TO_USE = '''

## Esta é a demonstração do software de chatbot desenvolvido para o TCC de João Pedro Barros Botelho.

### O que é o Chatbot?

O Chatbot é uma ferramenta de inteligência artificial que permite a interação entre usuários e um sistema de perguntas e respostas. Através de uma interface de chat, o usuário poderá fazer perguntas sobre os documentos da sua base de conhecimento WikiJs e até mesmo dos documentos enviados localmente, para assim receber respostas rápidas e precisas.
### Como utilizar a solução?


1. Inicialmente, no menu da barra lateral acesse a página "Inserir Credenciais", pois só desta forma será permitido utilizas as páginas "Chat" e "Processar Arquivos". 

2. No menu da barra lateral acesse a página "Chat" para iniciar uma nova conversa.

2. Antes de processarmos os arquivos, precisamos que os mesmos estejam disponível no repositório local, para isso acesse a página "Importar Arquivos" e siga as instruções.:

    I. A origem dos arquivos pode ser de um arquivo local enviado pelo um usuário. Após selecionar os arquivos em "Browse files", os mesmos serão salvos na local, ficando assim disponível para serem processados na página "Processar Arquivos".

    II. Caso 

'''


PAGE_TITLE = 'TCC João Pedro - Chat Wiki'
CHAT_IA_IMG = os.path.join(BASE_DIR, 'resources/images/robot-icone.png')
CHAT_USER_IMG = os.path.join(BASE_DIR, 'resources/images/user-icone.png')
SIDEBAR_LOGO_IMG = os.path.join(BASE_DIR, 'resources/images/Logo-Tcc.jpeg')
LOGIN_BACKGROUND_IMG = os.path.join(BASE_DIR, 'resources/images/background.jpg')
UPLOADED_DOCUMENTS_PATH = os.path.join(BASE_DIR, 'uploaded_files')
DATA_JSON_PATH = 'C:/Users/jpbbg/OneDrive/Documentos/tcc2_V21/tcc2_2/chat_store.json'
CHAT_TITLE = 'TCC João Pedro Barros Botelho ⚡️'


###################################################
#            LLM
###################################################
LLM_EMBEDDING_MODEL = 'text-embedding-3-large'
LLM_EMBEDDINGS_DIM = 3072
LLM_MODEL_DEFAULT = 'gpt-4o'

######### OPENAI PROMPTS ##########################
PROMPT_QA_OPENAI = (
    "O contexto para responder a pergunta está abaixo\n"
    "---------------------\n"
    "{context_str}\n"
    "---------------------\n"
    "Dado o contexto, respire profundamente e responda detalhadamente a pergunta a seguir "
    "Pergunta a ser respondida: {query_str}\n"
    "Sempre cite os documentos utilizados para cada parte da resposta. Sempre responda em português"
    "")

PROMPT_REFINE_OPENAI = (
    "Nós temos a oportunidade de refinar a resposta anterior. "
    "(apenas se necessário) com mais o contexto abaixo.\n"
    "------------\n"
    "{context_msg}\n"
    "------------\n"
    "Dado o novo contexto, refine a resposta para responder melhor a questão.  "
    "Responda a questão: {query_str}. "
    "Caso o contexto não seja útil, responda a saída original de novo. Lembre sempre de citar a fonte\n"
    "Resposta Original: {existing_answer}"
)

PROMPT_SYSTEM_OPENAI = "Ok, irei respirar profundamente e utilizar o contexto fornecido para responder detalhadamente à pergunta {query_str} \
            Também sempre citarei os documentos utilizados como fonte da informação. Sempre responderei em português."

###################################################
#            QDRANT
###################################################
QDRANT_COLLECTION = 'tcc_content'
QDRANT_SIM_TOP_K=20
QDRANT_SPARSE_TOP_K=10

###################################################
#            AWS-Regions
###################################################
LISTA_REGIOES_AWS = [
    "us-east-1",
    "sa-east-1",
    "us-east-2",
    "us-west-1",
    "us-west-2",
    "af-south-1",
    "ap-east-1",
    "ap-south-2",
    "ap-southeast-3",
    "ap-southeast-5",
    "ap-southeast-4",
    "ap-south-1",
    "ap-northeast-3",
    "ap-northeast-2",
    "ap-southeast-1",
    "ap-southeast-2",
    "ap-northeast-1",
    "ca-central-1",
    "ca-west-1",
    "cn-north-1",
    "cn-northwest-1",
    "eu-central-1",
    "eu-west-1",
    "eu-west-2",
    "eu-south-1",
    "eu-west-3",
    "eu-south-2",
    "eu-north-1",
    "eu-central-2",
    "il-central-1",
    "me-south-1",
    "me-central-1"
]