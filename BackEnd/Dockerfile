FROM python:3.11

# Definir o diretório de trabalho no contêiner
WORKDIR /app

# Copiar os arquivos necessários para o contêiner
COPY requirements.txt /app/requirements.txt
COPY . /app

# Instalar as dependências
RUN pip install --no-cache-dir -r /app/requirements.txt

# Expor as portas necessárias
EXPOSE 8000

# Comando para iniciar o FastAPI
CMD ["uvicorn", "chamadas_api:app", "--host", "0.0.0.0", "--port", "8000"]
