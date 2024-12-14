import boto3
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')


def list_s3_documents(bucket_name, aws_region_name, aws_access_key_id, aws_secret_access):
    s3 = boto3.client(
        's3',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access,
        region_name=aws_region_name
    )
    
    response = s3.list_objects_v2(Bucket=bucket_name)
    
    documents = []
    if 'Contents' in response:
        for obj in response['Contents']:
            key = obj['Key']
            if key.endswith(('.html', '.md')):
                documents.append(key)
    
    return documents

def list_with_filter_s3_documents(bucket_name, aws_region_name, aws_access_key_id, aws_secret_access, atual_dir):
    s3 = boto3.client(
        's3',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access,
        region_name=aws_region_name
    )
    
    response = s3.list_objects_v2(Bucket=bucket_name)
    
    download_path = os.path.join(atual_dir, 'Arquivos_Baixados_AWS')
    processado_path = os.path.join(atual_dir, 'Arquivos_Processados')
    pre_processado_path = os.path.join(atual_dir, 'Pre_Processados')
    documents = []
    if 'Contents' in response:
        for obj in response['Contents']:
            key = obj['Key']
            if key.endswith(('.html', '.md')):
                documents.append(key)
    lista = []
    for document in documents:
        nome_arquivo = document.rsplit('/', 1)[-1]
        file_name = os.path.basename(nome_arquivo)
        file_path = os.path.join(download_path, file_name)
        file_path_processado = os.path.join(processado_path, os.path.splitext(file_name)[0] + '.md')
        file_path_pre_processado = os.path.join(pre_processado_path, os.path.splitext(file_name)[0] + '.md')
        if not os.path.exists(file_path) and not os.path.exists(file_path_processado) and not os.path.exists(file_path_pre_processado):
            lista.append(document)
    return lista
        
def download_s3_document(bucket_name, aws_region_name, document_key, download_path, processado_path, pre_processado_path, aws_access_key_id, aws_secret_access):
    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access,
            region_name=aws_region_name
        )
        nome_arquivo = document_key.rsplit('/', 1)[-1]
        file_name = os.path.basename(nome_arquivo)
        file_path = os.path.join(download_path, file_name)
        file_path_processado = os.path.join(processado_path, os.path.splitext(file_name)[0] + '.md')
        file_path_pre_processado = os.path.join(pre_processado_path, os.path.splitext(file_name)[0] + '.md')
        if not os.path.exists(file_path) and not os.path.exists(file_path_processado) and not os.path.exists(file_path_pre_processado):
            s3.download_file(bucket_name, document_key, file_path)
            print(f'Downloaded {document_key} to {file_path}')
        else:
            print(f'{document_key} already exists')
        return True
    except Exception as e:
        print(f'Error downloading {document_key}: {e}')
        return False


def processar_all_download_aws(bucket_name, aws_region_name, aws_access_key_id, aws_secret_access):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    download_path = os.path.join(script_dir, 'Arquivos_Baixados_AWS')
    processado_path = os.path.join(script_dir, 'Arquivos_Processados')
    pre_processado_path = os.path.join(script_dir, 'Pre_Processados')
    documents = list_s3_documents(bucket_name, aws_region_name, aws_access_key_id, aws_secret_access)
    lista = []
    todos_sucesso = True
    for doc in documents:
        Resposta = download_s3_document(bucket_name, aws_region_name, doc, download_path, processado_path, pre_processado_path, aws_access_key_id, aws_secret_access)
        if Resposta:
            lista.append(doc)
        else:
            todos_sucesso = False
    return todos_sucesso, lista

def processar_download_aws(bucket_name, aws_region_name, aws_access_key_id, aws_secret_access, documents):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    download_path = os.path.join(script_dir, 'Arquivos_Baixados_AWS')
    processado_path = os.path.join(script_dir, 'Arquivos_Processados')
    pre_processado_path = os.path.join(script_dir, 'Pre_Processados')
    lista = []
    todos_sucesso = True
    for doc in documents:
        Resposta = download_s3_document(bucket_name, aws_region_name, doc, download_path, processado_path, pre_processado_path, aws_access_key_id, aws_secret_access)
        if Resposta:
            lista.append(doc)
        else:
            todos_sucesso = False
    return todos_sucesso, lista

def main():
    aws_access_key_id = ''
    aws_secret_access = ''
    bucket_name = ''
    aws_region_name = 'us-east-1'
    script_dir = os.path.dirname(os.path.abspath(__file__))
    download_path = os.path.join(script_dir, 'Arquivos_Baixados_AWS')
    processado_path = os.path.join(script_dir, 'Arquivos_Processados')
    pre_processado_path = os.path.join(script_dir, 'Pre_Processados')
    documents = list_s3_documents(bucket_name, aws_region_name, aws_access_key_id, aws_secret_access)
    for doc in documents:
        download_s3_document(bucket_name, aws_region_name, doc, download_path, processado_path, pre_processado_path, aws_access_key_id, aws_secret_access)

if __name__ == "__main__":
    main()