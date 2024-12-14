import os
import json
from IPython.display import Markdown, display
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core import StorageContext
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core import Settings
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.storage.chat_store import SimpleChatStore
from llama_index.embeddings.openai import OpenAIEmbedding
from qdrant_client import models
from llama_index.embeddings.openai import OpenAIEmbedding
from qdrant_client import QdrantClient
from llama_index.llms.openai import OpenAI
from llama_index.core.llms import ChatMessage
from llama_index.core.ingestion import IngestionPipeline
import multiprocessing
from llama_index.core.node_parser import SentenceSplitter
# Variável Index Global
index = None


# Função para carregar ou criar o chat_store
def load_or_create_chat_store(file_path):
    if os.path.exists(file_path):
        print("Histórico encontrado. Carregando...")
        with open(file_path, "r") as f:
            data = json.load(f)
            return SimpleChatStore.from_dict(data)
    else:
        print("Histórico não encontrado. Criando novo...")
        return SimpleChatStore()


def define_openai_api_key(openai_api_key):
    os.environ['OPENAI_API_KEY'] = openai_api_key

def initialize_or_create_collection(qdrant_client, qdrant_collection_name):

    if qdrant_client is None or qdrant_collection_name is None:
        raise Exception("Variáveis do Qdrant não definidas")
    collections = qdrant_client.get_collections().collections

    # Check if the collection exists
    if qdrant_collection_name not in [collection.name for collection in collections]:
        # Create the collection if it doesn't exist
        qdrant_client.create_collection(
            collection_name=qdrant_collection_name,
            vectors_config={
                "text-dense": models.VectorParams(
                    size=1536,
                    distance=models.Distance.COSINE,
                )
            },
            sparse_vectors_config={
                "text-sparse": models.SparseVectorParams(
                    index=models.SparseIndexParams()
                ),
            },
        )

    # Initialize the vector store with the existing collection
    qdrant_store = QdrantVectorStore(
        client=qdrant_client,
        collection_name=qdrant_collection_name,
        enable_hybrid=True,
        fastembed_sparse_model="Qdrant/bm25",
    )

    storage_context = StorageContext.from_defaults(vector_store=qdrant_store)

    embedding_model = OpenAIEmbedding(
        model="text-embedding-3-small",
        dimensions=1536,
        embed_batch_size=500,
    )
    global index
    index = VectorStoreIndex.from_vector_store(
        vector_store=qdrant_store,
        storage_context=storage_context,
        embed_model=embedding_model,
    )
    return index


def send_documents_to_qdrant():
    qdrant_collection_name = os.environ['QDRANT_COLLECTION_NAME']
    qdrant_url = os.environ['QDRANT_URL']
    qdrant_api_key = os.environ['QDRANT_API_KEY']
    project_path = os.path.dirname(os.path.abspath(__file__))
    processed_path = os.path.join(project_path, 'Arquivos_Processados')
    success_files_path = os.path.join(project_path, 'Arquivos_No_Qdrant')
    try:
        qdrant_client = QdrantClient(
            url=qdrant_url,
            api_key=qdrant_api_key,
            timeout=300.0,
        )
        
        collections = qdrant_client.get_collections().collections
        
        # Check if the collection exists
        if qdrant_collection_name not in [collection.name for collection in collections]:
            initialize_or_create_collection(qdrant_client, qdrant_collection_name)
        
        vector_store = QdrantVectorStore(
            collection_name=qdrant_collection_name,
            client=qdrant_client,
            enable_hybrid=True,
            fastembed_sparse_model="Qdrant/bm25",
        )
        
        documents = SimpleDirectoryReader(processed_path).load_data()
        
        # Configura o pipeline de ingestão
        splitter = SentenceSplitter(chunk_size=512, chunk_overlap=50)
        transformations = [splitter]
        pipeline = IngestionPipeline(transformations=transformations)
        
        num_cpus = multiprocessing.cpu_count()
        cal =  num_cpus // 4
        num_final = cal * 3
        num_max_workers = max(1, num_final)

        # Processa os documentos usando o pipeline
        nodes = pipeline.run(
            nodes=documents, 
            num_workers=num_max_workers, 
            show_progress=True
        )
        
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        
        embedding_model = OpenAIEmbedding(
            model="text-embedding-3-small",
            dimensions=1536,
            embed_batch_size=500,
        )
        
        # Indexa os documentos processados
        VectorStoreIndex(
            nodes=nodes,
            storage_context=storage_context,
            show_progress=True,
            embed_model=embedding_model,
            insert_batch_size=len(nodes),
        )

    except Exception as e:
        print(f"Error processing documents: {e}")
        return e
    return True


def question_to_vector(question, qdrant_collection_name, qdrant_url, qdrant_api_key, chat_store_user="user1", chat_history_file="chat_store.json"):
    qdrant_client = QdrantClient(
        url=qdrant_url,
        api_key=qdrant_api_key,
        timeout=120.0,
    )
    global index
    if index is None:
        index = initialize_or_create_collection(qdrant_client, qdrant_collection_name)
    
    llm = OpenAI(model="gpt-4o")
    
    if os.path.exists(chat_history_file):
        chat_store = SimpleChatStore.from_persist_path(
            persist_path=chat_history_file
        )
    else:
        chat_store = SimpleChatStore()

    chat_memory = ChatMemoryBuffer.from_defaults(
        token_limit=1000,
        chat_store=chat_store,
        chat_store_key=qdrant_collection_name,
    )
    
    chat_engine = index.as_chat_engine(
        llm=llm,
        memory=chat_memory,
        similarity_top_k=20,
        sparse_top_k=10,
        vector_store_query_mode="hybrid",
        verbose=False,)
    response = chat_engine.chat(question)
    chat_store.persist(persist_path=chat_history_file)
    return str(response)

def variables_qdrant(collection_name, qdrant_url, qdrant_api_key):
    os.environ['QDRANT_COLLECTION_NAME'] = collection_name
    os.environ['QDRANT_URL'] = qdrant_url
    os.environ['QDRANT_API_KEY'] = qdrant_api_key
    

def clear_variables_global():

    global index

    index = None

def main():

    openai_api_key = ''
    define_openai_api_key(openai_api_key)
    qdrant_api_key = ''
    qdrant_url = ''
    #index = load_existing_index(qdrant_url, qdrant_api_key, openai_api_key)
    variables_qdrant("local", qdrant_url, qdrant_api_key)
    
    index = send_documents_to_qdrant()
    #result = question_to_vector("wiki_content", qdrant_url, qdrant_api_key, "E agora poderia falar sobre o item numero 3?")
    print("Resposta abaixo")
    #print(result)
    
if __name__ == "__main__":
    main()
    
