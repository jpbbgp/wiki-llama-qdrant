import html2text
import re
import requests
import os
import sys
import html2text
import boto3
import base64
import tempfile
import uuid
sys.stdout.reconfigure(encoding='utf-8')



def list_existing_files(download_path):
    try:
        existing_files = os.listdir(download_path)
        return existing_files
    except FileNotFoundError:
        print(f"The directory {download_path} does not exist.")
        return []


def separete_files_by_type(files):
    html_files_list = []
    md_files_list = []

    for file in files:
        if file.endswith('.html'):
            html_files_list.append(file)
        elif file.endswith('.md'):
            md_files_list.append(file)
            
    return html_files_list, md_files_list
    
def list_files_downloaded(local_path):
    download_path = os.path.join(local_path, 'Arquivos_Baixados_AWS')
    try:
        files = os.listdir(download_path)
        return files
    except FileNotFoundError:
        print(f"The directory {download_path} does not exist.")
        return []
    
def list_files_local(local_path):
    local_files_path = os.path.join(local_path, 'Local_Files')
    try:
        files = os.listdir(local_files_path)
        return files
    except FileNotFoundError:
        print(f"The directory {local_files_path} does not exist.")
        return []
    
def list_files_wiki(local_path):
    local_files_path = os.path.join(local_path, 'Wiki_Files')
    try:
        files = os.listdir(local_files_path)
        return files
    except FileNotFoundError:
        print(f"The directory {local_files_path} does not exist.")
        return []

def list_files_qdrant(local_path):
    qdrant_path = os.path.join(local_path, 'Arquivos_No_Qdrant')
    try:
        files = os.listdir(qdrant_path)
        return files
    except FileNotFoundError:
        print(f"The directory {qdrant_path} does not exist.")
        return []

def process_html_content_aws(html_files_list, project_path, download_path, s3_client, bucket_name):
    pre_processed_path = os.path.join(project_path, 'Pre_Processados')
    if not os.path.exists(pre_processed_path):
        os.makedirs(pre_processed_path)
    
    for html_file in html_files_list:
        html_file_path = os.path.join(download_path, html_file)
        with open(html_file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()
        
        # Convert HTML to Markdown
        markdown_content = html2text.html2text(html_content)
            
        image_pattern = r'!\[(.*?)\]\((.*?)\)'

        def replace_image(match):
            alt_text = match.group(1).replace('\n', ' ')
            img_src = match.group(2).replace('\n', '')

            if img_src.startswith('data:image'):
                # Image is already in base64
                base64_data = img_src.split(',')[1]
            elif re.match(r'^https?://', img_src):
                # Handle external URL
                img_src = re.sub(r'\s*=\d+x$', '', img_src)
                try:
                    img_response = requests.get(img_src)
                    if img_response.status_code == 200:
                        img_data = img_response.content
                        base64_data = base64.b64encode(img_data).decode('utf-8')
                    else:
                        print(f"Failed to download image from URL {img_src}: {img_response.status_code}")
                        base64_data = None
                except Exception as e:
                    print(f"Error downloading image from URL {img_src}: {str(e)}")
                    base64_data = None
            else:
                # Handle S3 image download
                img_src = re.sub(r'\s*=\d+x$', '', img_src)
                if img_src.startswith('/'):
                    img_src = img_src[1:]  # Adjust if the path has a leading slash
                # Construct the S3 key
                s3_key = img_src  # Assuming this matches directly with S3 key
                temp_dir = tempfile.gettempdir()  # Get platform-independent temporary directory
                local_image_path = os.path.join(temp_dir, f"{uuid.uuid4()}.png")  # Use temp directory
                try:
                    s3_client.download_file(bucket_name, s3_key, local_image_path)
                    with open(local_image_path, "rb") as image_file:
                        img_data = image_file.read()
                        base64_data = base64.b64encode(img_data).decode('utf-8')
                except Exception as e:
                    print(f"Failed to download image from S3 with key {s3_key}: {str(e)}")
                    base64_data = None
            
            if base64_data:
                # Return the image in base64 format
                return f'![{alt_text}](data:image/png;base64,{base64_data})'
            else:
                return match.group(0)  # Return the original match if there's an error

        # Replace images in Markdown content
        processed_content = re.sub(image_pattern, replace_image, markdown_content, flags=re.DOTALL)
        # Save the processed content to the "Pre_Processados" folder
        output_file_name = f"{os.path.splitext(html_file)[0]}.md"
        output_file_path = os.path.join(pre_processed_path, output_file_name)
        with open(output_file_path, 'w', encoding='utf-8') as out_file:
            out_file.write(processed_content)

        # Excluir o arquivo HTML original
        os.remove(html_file_path)


# Function to process Markdown content
def process_markdown_files_aws(md_files_list, project_path, download_path, s3_client, bucket_name):
    pre_processed_path = os.path.join(project_path, 'Pre_Processados')
    if not os.path.exists(pre_processed_path):
        os.makedirs(pre_processed_path)
        
    
    for md_file in md_files_list:
        md_file_path = os.path.join(download_path, md_file)
        with open(md_file_path, 'r', encoding='utf-8') as file:
            markdown_content = file.read()
        image_pattern = r'!\[(.*?)\]\((.*?)\)'

        def replace_image(match):
            alt_text = match.group(1).replace('\n', ' ')
            img_src = match.group(2).replace('\n', '')

            if img_src.startswith('data:image'):
                # Image is already in base64
                base64_data = img_src.split(',')[1]
            elif re.match(r'^https?://', img_src):
                # Handle external URL
                img_src = re.sub(r'\s*=\d+x$', '', img_src)
                print(f"Attempting to download image from URL: {img_src}")
                try:
                    img_response = requests.get(img_src)
                    if img_response.status_code == 200:
                        img_data = img_response.content
                        base64_data = base64.b64encode(img_data).decode('utf-8')
                    else:
                        print(f"Failed to download image from URL {img_src}: {img_response.status_code}")
                        base64_data = None
                except Exception as e:
                    print(f"Error downloading image from URL {img_src}: {str(e)}")
                    base64_data = None
            else:
                # Handle S3 image download
                img_src = re.sub(r'\s*=\d+x$', '', img_src)
                print(f"Attempting to download image from S3: {img_src}")
                if img_src.startswith('/'):
                    img_src = img_src[1:]  # Adjust if the path has a leading slash
                # Construct the S3 key
                s3_key = img_src  # Assuming this matches directly with S3 key
                temp_dir = tempfile.gettempdir()  # Get platform-independent temporary directory
                local_image_path = os.path.join(temp_dir, f"{uuid.uuid4()}.png")  # Use temp directory
                try:
                    s3_client.download_file(bucket_name, s3_key, local_image_path)
                    with open(local_image_path, "rb") as image_file:
                        img_data = image_file.read()
                        base64_data = base64.b64encode(img_data).decode('utf-8')
                except Exception as e:
                    print(f"Failed to download image from S3 with key {s3_key}: {str(e)}")
                    base64_data = None
            
            if base64_data:
                # Return the image in base64 format
                return f'![{alt_text}](data:image/png;base64,{base64_data})'
            else:
                return match.group(0)  # Return the original match if there's an error

        # Replace images in Markdown content
        processed_content = re.sub(image_pattern, replace_image, markdown_content, flags=re.DOTALL)
        # Save the processed content to the "Pre_Processados" folder
        output_file_path = os.path.join(pre_processed_path, md_file)
        with open(output_file_path, 'w', encoding='utf-8') as out_file:
            out_file.write(processed_content)

        # Excluir o arquivo Markdown original
        os.remove(md_file_path)

def process_html_content(html_files_list, project_path, download_path, decide_path):
    pre_processed_path = os.path.join(project_path, 'Pre_Processados')
    if not os.path.exists(pre_processed_path):
        os.makedirs(pre_processed_path)
    
    for html_file in html_files_list:
        html_file_path = os.path.join(download_path, html_file)
        with open(html_file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()
        
        # Convert HTML to Markdown
        markdown_content = html2text.html2text(html_content)
            
        image_pattern = r'!\[(.*?)\]\((.*?)\)'

        def replace_image(match):
            alt_text = match.group(1).replace('\n', ' ')
            img_src = match.group(2).replace('\n', '')

            if img_src.startswith('data:image'):
                # Image is already in base64
                base64_data = img_src.split(',')[1]
            elif re.match(r'^https?://', img_src):
                # Handle external URL
                img_src = re.sub(r'\s*=\d+x$', '', img_src)
                try:
                    img_response = requests.get(img_src)
                    if img_response.status_code == 200:
                        img_data = img_response.content
                        base64_data = base64.b64encode(img_data).decode('utf-8')
                    else:
                        print(f"Failed to download image from URL {img_src}: {img_response.status_code}")
                        base64_data = None
                except Exception as e:
                    print(f"Error downloading image from URL {img_src}: {str(e)}")
                    base64_data = None
            else:
                base64_data = None
            if base64_data:
                # Return the image in base64 format
                return f'![{alt_text}](data:image/png;base64,{base64_data})'
            else:
                return match.group(0)  # Return the original match if there's an error

        # Replace images in Markdown content
        processed_content = re.sub(image_pattern, replace_image, markdown_content, flags=re.DOTALL)
        # Save the processed content to the "Pre_Processados" folder
        output_file_name = f"{os.path.splitext(html_file)[0]}.md"
        output_file_path = os.path.join(pre_processed_path, output_file_name)
        with open(output_file_path, 'w', encoding='utf-8') as out_file:
            out_file.write(processed_content)

        # Excluir o arquivo HTML original
        if decide_path != 'wiki':
            os.remove(html_file_path)


# Function to process Markdown content
def process_markdown_files(md_files_list, project_path, download_path, decide_path):
    pre_processed_path = os.path.join(project_path, 'Pre_Processados')
    if not os.path.exists(pre_processed_path):
        os.makedirs(pre_processed_path)
        
    
    for md_file in md_files_list:
        md_file_path = os.path.join(download_path, md_file)
        with open(md_file_path, 'r', encoding='utf-8') as file:
            markdown_content = file.read()
        image_pattern = r'!\[(.*?)\]\((.*?)\)'

        def replace_image(match):
            alt_text = match.group(1).replace('\n', ' ')
            img_src = match.group(2).replace('\n', '')

            if img_src.startswith('data:image'):
                # Image is already in base64
                base64_data = img_src.split(',')[1]
            elif re.match(r'^https?://', img_src):
                # Handle external URL
                img_src = re.sub(r'\s*=\d+x$', '', img_src)
                print(f"Attempting to download image from URL: {img_src}")
                try:
                    img_response = requests.get(img_src)
                    if img_response.status_code == 200:
                        img_data = img_response.content
                        base64_data = base64.b64encode(img_data).decode('utf-8')
                    else:
                        print(f"Failed to download image from URL {img_src}: {img_response.status_code}")
                        base64_data = None
                except Exception as e:
                    print(f"Error downloading image from URL {img_src}: {str(e)}")
                    base64_data = None
            else:
                base64_data = None
            
            if base64_data:
                # Return the image in base64 format
                return f'![{alt_text}](data:image/png;base64,{base64_data})'
            else:
                return match.group(0)  # Return the original match if there's an error

        # Replace images in Markdown content
        processed_content = re.sub(image_pattern, replace_image, markdown_content, flags=re.DOTALL)
        # Save the processed content to the "Pre_Processados" folder
        output_file_path = os.path.join(pre_processed_path, md_file)
        with open(output_file_path, 'w', encoding='utf-8') as out_file:
            out_file.write(processed_content)

        # Excluir o arquivo Markdown original
        if decide_path != 'wiki':
            os.remove(md_file_path)

def start_process_files(decide_path):
    project_path = os.path.dirname(os.path.abspath(__file__))
    if decide_path == 'local':
        download_path = os.path.join(project_path, 'Local_Files')
    elif decide_path == 'aws':
        download_path = os.path.join(project_path, 'Arquivos_Baixados_AWS')
    else:
        download_path = os.path.join(project_path, 'Wiki_Files')
    existing_files = list_existing_files(download_path)
    html_files_list, md_files_list = separete_files_by_type(existing_files)

    process_markdown_files(md_files_list, project_path, download_path, decide_path)
    process_html_content(html_files_list, project_path, download_path, decide_path)
    

def start_process_files_aws(bucket_name, aws_region_name, aws_access_key_id, aws_secret_access):
    project_path = os.path.dirname(os.path.abspath(__file__))
    download_path = os.path.join(project_path, 'Arquivos_Baixados_AWS')
    existing_files = list_existing_files(download_path)
    html_files_list, md_files_list = separete_files_by_type(existing_files)
    
    s3_client = boto3.client(
        's3',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access,
        region_name=aws_region_name
    )
    
    process_markdown_files_aws(md_files_list, project_path, download_path, s3_client, bucket_name)
    process_html_content_aws(html_files_list, project_path, download_path, s3_client, bucket_name)    
    
def main():
    aws_access_key = ''
    aws_secret_key = ''
    aws_region_name = 'us-east-1'
    bucket_name = ''
    project_path = os.path.dirname(os.path.abspath(__file__))
    download_path = os.path.join(project_path, 'Arquivos_Baixados_AWS')
    existing_files = list_existing_files(download_path)
    html_files_list, md_files_list = separete_files_by_type(existing_files)
    
    s3_client = boto3.client(
        's3',
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
        region_name=aws_region_name
    )
    
    process_markdown_files(md_files_list, project_path, download_path, s3_client, bucket_name)
    process_html_content(html_files_list, project_path, download_path, s3_client, bucket_name)
    


if __name__ == "__main__":
    main()