FROM python:3.11

# Definir o diretório de trabalho no contêiner
WORKDIR /app

# Copiar os arquivos necessários para o contêiner
COPY requirements.txt /app/requirements.txt
COPY . /app

# Instalar as dependências
RUN pip install --no-cache-dir -r /app/requirements.txt


# Expor as portas necessárias
EXPOSE 8501

# Comando para iniciar o Streamlit
CMD ["streamlit", "run", "index.py", "--server.port=8501", "--server.address=0.0.0.0"]
