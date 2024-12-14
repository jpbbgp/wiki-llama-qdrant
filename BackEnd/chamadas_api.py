from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import os

app = FastAPI()
from Import_files_S3 import processar_download_aws, list_with_filter_s3_documents, processar_all_download_aws
from Process_Files import start_process_files_aws, start_process_files, list_files_downloaded, list_files_qdrant, list_files_local, list_files_wiki
from image_converter_with_OpenAI import start_process_image_files
from process_llama_qdrant import clear_variables_global, variables_qdrant, send_documents_to_qdrant, question_to_vector

class RequestModel(BaseModel):
    param1: str
    param2: int

class StringModel(BaseModel):
    name: str

class APIKeyModel(BaseModel):
    openai_api_key: str

class S3DownloadModel(BaseModel):
    bucket_name: str
    aws_region_name: str
    aws_access_key_id: str
    aws_secret_access: str
    
class QdrantModel(BaseModel):
    collection_name: str
    qdrant_url: str
    qdrant_api_key: str

class QuestionModel(BaseModel):
    question: str
    collection: str

class ListModel(BaseModel):
    names: List[str]
    
class ProcessModel(BaseModel):
    collection: str
    recorrente: str
    
@app.post("/api/set_qdrant_variables")
async def set_qdrant_variables(request: QdrantModel):
    os.environ['QDRANT_COLLECTION_NAME'] = request.collection_name
    os.environ['QDRANT_URL'] = request.qdrant_url
    os.environ['QDRANT_API_KEY'] = request.qdrant_api_key
    #variables_qdrant(request.collection_name, request.qdrant_url, request.qdrant_api_key)
    return {"message": "True"}

@app.get("/api/get_exist_API_Key")
async def get_exist_API_Key():
    if 'OPENAI_API_KEY' in os.environ:
        return {"message": "True"}  
    return {"message": "False"}

@app.get("/api/get_exist_Qdrant_env")
async def get_exist_Qdrant_env():
    required_vars = ['QDRANT_COLLECTION_NAME', 'QDRANT_URL', 'QDRANT_API_KEY']
    missing_vars = [var for var in required_vars if var not in os.environ]
    if missing_vars:
        return {"message": "False"}
    return {"message": "True"}  
    

@app.post("/api/set_collection_name")
async def set_collection_name(request: StringModel):
    os.environ['QDRANT_COLLECTION_NAME'] = request.name
    return {"message": "True"}

@app.post("/api/set_api_key")
async def set_api_key(request: APIKeyModel):
    os.environ['OPENAI_API_KEY'] = request.openai_api_key
    return {"message": "True"}

@app.post("/api/set_aws_credentials")
async def set_aws_credentials(request: S3DownloadModel):
    os.environ['BUCKET_NAME'] = request.bucket_name
    os.environ['AWS_REGION_NAME'] = request.aws_region_name
    os.environ['AWS_ACCESS_KEY_ID'] = request.aws_access_key_id
    os.environ['AWS_SECRET_ACCESS'] = request.aws_secret_access
    return {"message": "Credenciais da AWS definidas com sucesso"}

@app.post("/api/download_from_s3")
async def download_from_s3(request: ListModel):
    required_vars = ['BUCKET_NAME', 'AWS_REGION_NAME', 'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS']
    missing_vars = [var for var in required_vars if var not in os.environ]
    
    if missing_vars:
        raise HTTPException(status_code=400, detail=f"As seguintes variáveis de ambiente estão faltando: {', '.join(missing_vars)}")
    print(request.names)
    todos_sucesso, lista = processar_download_aws(
        os.environ['BUCKET_NAME'],
        os.environ['AWS_REGION_NAME'],
        os.environ['AWS_ACCESS_KEY_ID'],
        os.environ['AWS_SECRET_ACCESS'],
        request.names
    )
    if todos_sucesso:
        return {"message": "True", "result": lista}
    return {"message": "False", "result": lista}

@app.post("/api/download_all_from_s3")
async def download_all_from_s3():
    required_vars = ['BUCKET_NAME', 'AWS_REGION_NAME', 'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS']
    missing_vars = [var for var in required_vars if var not in os.environ]
    
    if missing_vars:
        raise HTTPException(status_code=400, detail=f"As seguintes variáveis de ambiente estão faltando: {', '.join(missing_vars)}")
    
    todos_sucesso, lista = processar_all_download_aws(
        os.environ['BUCKET_NAME'],
        os.environ['AWS_REGION_NAME'],
        os.environ['AWS_ACCESS_KEY_ID'],
        os.environ['AWS_SECRET_ACCESS']
    )
    if todos_sucesso:
        return {"message": "Todos os arquivos foram baixados com sucesso.", "result": lista}
    return {"message": "Alguns Downloads tiveram problema.", "result": lista}

@app.post("/api/process_files_basic")
async def process_files_basic(request: ProcessModel):
    try:
        os.environ['QDRANT_COLLECTION_NAME'] = request.collection
        start_process_files(request.collection)
        if 'OPENAI_API_KEY' not in os.environ:
            raise HTTPException(status_code=400, detail="Variável OPENAI_API_KEY não está definido.")
        start_process_image_files(os.environ['OPENAI_API_KEY'])
        required_vars_qdrant = ['QDRANT_COLLECTION_NAME', 'QDRANT_URL', 'QDRANT_API_KEY', 'OPENAI_API_KEY']
        missing_vars_qdrant = [var for var in required_vars_qdrant if var not in os.environ]
        
        if missing_vars_qdrant:
            raise HTTPException(status_code=400, detail=f"As seguintes variáveis de ambiente estão faltando: {', '.join(missing_vars_qdrant)}")
        status = send_documents_to_qdrant()
        if status:
            return {"message": "True"}
        else:
            return {"message": status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro ao processar os arquivos: {str(e)}")
    return {"message": "True"}

@app.post("/api/process_files_aws")
async def process_files_aws():
    
    required_vars = ['BUCKET_NAME', 'AWS_REGION_NAME', 'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS']
    missing_vars = [var for var in required_vars if var not in os.environ]
    
    if missing_vars:
        raise HTTPException(status_code=400, detail=f"As seguintes variáveis de ambiente estão faltando: {', '.join(missing_vars)}")
    try:
        start_process_files_aws(
            os.environ['BUCKET_NAME'],
            os.environ['AWS_REGION_NAME'],
            os.environ['AWS_ACCESS_KEY_ID'],
            os.environ['AWS_SECRET_ACCESS']
        )
        if 'OPENAI_API_KEY' not in os.environ:
            raise HTTPException(status_code=400, detail="Variável OPENAI_API_KEY não está definido.")
        
        start_process_image_files(os.environ['OPENAI_API_KEY'])
        required_vars_qdrant = ['QDRANT_COLLECTION_NAME', 'QDRANT_URL', 'QDRANT_API_KEY', 'OPENAI_API_KEY']
        missing_vars_qdrant = [var for var in required_vars_qdrant if var not in os.environ]
        
        if missing_vars_qdrant:
            raise HTTPException(status_code=400, detail=f"As seguintes variáveis de ambiente estão faltando: {', '.join(missing_vars_qdrant)}")
        #variables_qdrant(os.environ['QDRANT_COLLECTION_NAME'], os.environ['QDRANT_URL'], os.environ['QDRANT_API_KEY'])
        
        status = send_documents_to_qdrant()
        if status:
            return {"message": "True"}
        else:
            return {"message": status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro ao processar os arquivos: {str(e)}")
    return {"message": "True"}

@app.get("/api/process_image_files")
async def process_image_files():
    if 'OPENAI_API_KEY' not in os.environ:
        raise HTTPException(status_code=400, detail="Variável OPENAI_API_KEY não está definido.")
    
    start_process_image_files(os.environ['OPENAI_API_KEY'])
    return {"message": "Imagens processadas com sucesso."}


@app.get("/api/documents_to_qdrant")
async def documents_to_qdrant():
    required_vars = ['QDRANT_COLLECTION_NAME', 'QDRANT_URL', 'QDRANT_API_KEY', 'OPENAI_API_KEY']
    missing_vars = [var for var in required_vars if var not in os.environ]
    
    if missing_vars:
        raise HTTPException(status_code=400, detail=f"As seguintes variáveis de ambiente estão faltando: {', '.join(missing_vars)}")
    
    send_documents_to_qdrant()
    return {"message": "Documentos enviados para o Qdrant com sucesso."}

@app.post("/api/question")
async def question(request: QuestionModel):
    print(request.collection)
    os.environ['QDRANT_COLLECTION_NAME'] = request.collection
    required_vars = ['QDRANT_COLLECTION_NAME', 'QDRANT_URL', 'QDRANT_API_KEY', 'OPENAI_API_KEY']
    missing_vars = [var for var in required_vars if var not in os.environ]
    
    if missing_vars:
        print(missing_vars)
        raise HTTPException(status_code=400, detail=f"As seguintes variáveis de ambiente estão faltando: {', '.join(missing_vars)}")
    print(request.question)
    return question_to_vector(request.question, os.environ['QDRANT_COLLECTION_NAME'], os.environ['QDRANT_URL'], os.environ['QDRANT_API_KEY'], chat_store_user=os.environ['QDRANT_COLLECTION_NAME'])

@app.get("/api/get_status_env_aws")
async def get_status_env_aws():
    required_vars = ['BUCKET_NAME', 'AWS_REGION_NAME', 'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS']
    missing_vars = [var for var in required_vars if var not in os.environ]
    
    if missing_vars:
        return {"message": "False"}
    return {"message": "True", "bucket_name": os.environ['BUCKET_NAME']}

@app.get("/api/list_files_s3")
async def list_files_s3():
    required_vars = ['BUCKET_NAME', 'AWS_REGION_NAME', 'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS']
    missing_vars = [var for var in required_vars if var not in os.environ]
    
    if missing_vars:
        raise HTTPException(status_code=400, detail=f"As seguintes variáveis de ambiente estão faltando: {', '.join(missing_vars)}")
    
    atual_dir = os.path.dirname(os.path.abspath(__file__))
    lista = list_with_filter_s3_documents(
        os.environ['BUCKET_NAME'],
        os.environ['AWS_REGION_NAME'],
        os.environ['AWS_ACCESS_KEY_ID'],
        os.environ['AWS_SECRET_ACCESS'],
        atual_dir
    )
    print(atual_dir)
    print(lista)
    
    return {"message": lista}

@app.post("/api/set_aws_bucket")
async def set_aws_bucket(request: StringModel):
    os.environ['BUCKET_NAME'] = request.name
    return {"message": "True"}


@app.delete("/api/clear_aws_env_variables")
async def clear_aws_env_variables():
    os.environ.pop('BUCKET_NAME', None)
    os.environ.pop('AWS_REGION_NAME', None)
    os.environ.pop('AWS_ACCESS_KEY_ID', None)
    os.environ.pop('AWS_SECRET_ACCESS', None)
    return {"message": "True"}

@app.get("/api/get_files_downloaded")
async def get_files_downloaded():
    atual_dir = os.path.dirname(os.path.abspath(__file__))
    return {"message": list_files_downloaded(atual_dir)}

@app.get("/api/get_files_local")
async def get_files_local():
    atual_dir = os.path.dirname(os.path.abspath(__file__))
    return {"message": list_files_local(atual_dir)}

@app.get("/api/get_files_wiki")
async def get_files_wiki():
    atual_dir = os.path.dirname(os.path.abspath(__file__))
    return {"message": list_files_wiki(atual_dir)}

@app.get("/api/get_files_processed")
async def get_files_processed():
    atual_dir = os.path.dirname(os.path.abspath(__file__))
    return {"message": list_files_qdrant(atual_dir)}

@app.delete("/api/clear_env_variables")
async def clear_env_variables():
    os.environ.pop('OPENAI_API_KEY', None)
    os.environ.pop('BUCKET_NAME', None)
    os.environ.pop('AWS_REGION_NAME', None)
    os.environ.pop('AWS_ACCESS_KEY_ID', None)
    os.environ.pop('AWS_SECRET_ACCESS', None)
    os.environ.pop('QDRANT_COLLECTION_NAME', None)
    os.environ.pop('QDRANT_URL', None)
    os.environ.pop('QDRANT_API_KEY', None)
    clear_variables_global()
    return {"message": "Variáveis de Ambiente foram limpas com sucesso."}