import base64
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
from openai import OpenAI
import re
from PIL import Image
from io import BytesIO


# Função para decodificar a imagem a partir do Base64
def decode_base64_image(base64_string):
    image_data = base64.b64decode(base64_string)
    return image_data

# Função para gerar a descrição da imagem usando o BLIP-2
def generate_image_description(image):
    
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
            "role": "user",
            "content": [
                {
                "type": "text",
                "text": "Descrição completa da imagem, e abaixo retornar em forma de Markdown",
                },
                {
                "type": "image_url",
                "image_url": {
                    "url":  f"data:image/png;base64,{image}",
                    "detail": "high"
                },
                },
            ],
            }
        ],
    )

    #print(response.choices[0])
    
    return response.choices[0].message.content

# Função para formatar a descrição em Markdown
def format_description_to_markdown(description):
    markdown = f"# Descrição da Imagem\n\n{description}\n"
    return markdown

def process_image_files(project_path):
    pre_processed_path = os.path.join(project_path, 'Pre_Processados')
    processed_path = os.path.join(project_path, 'Arquivos_Processados')

    if not os.path.exists(processed_path):
        os.makedirs(processed_path)

    md_files = [f for f in os.listdir(pre_processed_path) if f.endswith('.md')]
    print(md_files)
    for md_file in md_files:
        md_file_path = os.path.join(pre_processed_path, md_file)
        with open(md_file_path, 'r', encoding='utf-8') as file:
            markdown_content = file.read()

        # Regex to find base64 images in Markdown
        image_pattern = r'!\[(.*?)\]\(data:image\/.*?;base64,(.*?)\)'
        
        def replace_image_with_description(match):
            alt_text = match.group(1).replace('\n', ' ')
            base64_data = match.group(2).replace('\n', '')
            try:
                description = generate_image_description(base64_data)
            except Exception as e:
                print(f"Error processing image in file {md_file}: {e}")
                description = alt_text

            # Return the description in place of the image
            return description

        # Replace images in Markdown content
        processed_content = re.sub(image_pattern, replace_image_with_description, markdown_content, flags=re.DOTALL)
        
        output_file_path = os.path.join(processed_path, md_file)
        with open(output_file_path, 'w', encoding='utf-8') as out_file:
            out_file.write(processed_content)

        # Optionally, delete the original pre-processed markdown file
        os.remove(md_file_path)

def define_openai_api_key(openai_api_key):
    os.environ['OPENAI_API_KEY'] = openai_api_key

def start_process_image_files(openai_api_key):
    project_path = os.path.dirname(os.path.abspath(__file__))
    define_openai_api_key(openai_api_key)
    process_image_files(project_path)

def main():
    # Exemplo de uso
    project_path = os.path.dirname(os.path.abspath(__file__))
    
    openai_api_key = '<Escreva-aqui-sua-chave-de-API-OpenAI>'
    define_openai_api_key(openai_api_key)
    process_image_files(project_path)
    
    
if __name__ == "__main__":
    main()
