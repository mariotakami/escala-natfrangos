import os
import json
import boto3
import requests
from datetime import datetime
# from dotenv import load_dotenv
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

# Carregar variáveis de ambiente do arquivo .env
# load_dotenv()

# Variáveis de ambiente
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
IG_USER_ID = os.getenv('IG_USER_ID')
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')
GRAPH_API_URL = 'https://graph.facebook.com/v21.0'

# Inicializar o cliente do S3
s3_client = boto3.client('s3')

def obter_stories():
    url = f"{GRAPH_API_URL}/{IG_USER_ID}/stories"
    params = {'access_token': ACCESS_TOKEN}
    response = requests.get(url, params=params)
    response.raise_for_status()  # Levanta uma exceção para códigos de status HTTP de erro
    return response.json().get('data', [])

def obter_insights(story_id):
    url = f"{GRAPH_API_URL}/{story_id}/insights"
    params = {
        'metric': 'impressions,reach,replies,profile_visits',
        'access_token': ACCESS_TOKEN
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json().get('data', [])

def salvar_no_s3(story_id, insights):
    try:
        # Adicionar o horário de extração dos insights
        extraction_time = datetime.utcnow().isoformat() + 'Z'  # Formato ISO 8601 com 'Z' indicando UTC
        insights_with_timestamp = {
            'story_id': story_id,
            'extraction_time': extraction_time,
            'insights': insights
        }
        # Converter os insights para JSON
        insights_json = json.dumps(insights_with_timestamp)
        # Nome do arquivo no S3
        s3_key = f"raw/nat_frangos/midias/instagram/stories_insights_lambda/{story_id}.json"
        # Fazer upload para o S3
        s3_client.put_object(Bucket=S3_BUCKET_NAME, Key=s3_key, Body=insights_json)
        print(f"Insights do story {story_id} salvos no S3 com sucesso.")
    except (NoCredentialsError, PartialCredentialsError) as e:
        print(f"Erro de credenciais ao tentar acessar o S3: {e}")
    except Exception as e:
        print(f"Erro ao salvar insights no S3: {e}")

def processar_stories_e_insights(event,context):
    try:
        stories = obter_stories()
        if not stories:
            print("Nenhum story ativo encontrado.")
            return
        for story in stories:
            story_id = story['id']
            insights = obter_insights(story_id)
            salvar_no_s3(story_id, insights)
    except requests.exceptions.RequestException as e:
        print(f"Erro ao obter dados do Instagram: {e}")

