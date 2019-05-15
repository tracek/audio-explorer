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

SERVE_LOCAL = os.getenv('LOCAL', False)

SAMPLING_RATE = 16000 # All audio will be resampled to this frequency
AUDIO_MARGIN = 0.2 # Margin applied to start and end of the audio to make it longer and improve UX. Not applied to any calculations.
TEMP_STORAGE = '/tmp/' # Temporary storage location
