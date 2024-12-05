import json
import boto3
import uuid
from datetime import datetime

s3_client = boto3.client('s3')  # Inicializa o cliente S3

def handle_story_insights(event, context):
    # Nome do bucket e caminho do arquivo
    bucket_name = "escala-in10"
    folder_path = "raw/webhook/natfrangos/instagram_story/"
    try:
        # Obtenha o corpo da requisição
        body = json.loads(event['body'])  # Converte a string JSON para um objeto Python

        # Cria um nome de arquivo único baseado em UUID e timestamp
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_id = str(uuid.uuid4())
        file_name = f"{folder_path}story_insights_{timestamp}_{unique_id}.json"

        # Salva o JSON no S3
        s3_client.put_object(
            Bucket=bucket_name,
            Key=file_name,
            Body=json.dumps(body),
            ContentType='application/json'
        )

        # Retorna resposta de sucesso
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Data stored successfully", "file": file_name})
        }
    except Exception as e:
        # Trata erros e retorna resposta
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

def verify_token(event, context):
    # Extraia parâmetros de consulta
    params = event.get('queryStringParameters', {})
    mode = params.get('hub.mode', '')
    token = params.get('hub.verify_token', '')
    challenge = params.get('hub.challenge', '')

    # Verifique o token
    if mode == 'subscribe' and token == 'iknow':
        return {
            "statusCode": 200,
            "body": challenge
        }
    else:
        return {
            "statusCode": 403,
            "body": "Forbidden"
        }
