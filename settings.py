import os
from dotenv import load_dotenv

load_dotenv()

DB_ENGINE = 'postgresql+psycopg2'
DB_USER = os.getenv('RDS_USERNAME')
DB_PASSWORD = os.getenv('RDS_PASSWORD')
DB_HOSTNAME = os.getenv('RDS_HOSTNAME')
DB_DATABASE_NAME = os.getenv('RDS_DB_NAME')

IPINFO_TOKEN = os.getenv('IPINFO_TOKEN')

S3_BUCKET = 'audioexplorer'
S3_STREAMED = f'https://s3.eu-central-1.amazonaws.com/{S3_BUCKET}/'
AWS_REGION = 'eu-central-1'