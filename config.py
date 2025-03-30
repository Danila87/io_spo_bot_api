import os
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.environ.get('DB_USER')
DB_PASS = os.environ.get('DB_PASS')
DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT')
DB_NAME = os.environ.get('DB_NAME')

SECRET_KEY = os.environ.get('SECRET_KEY')
SECRET_KEY_REFRESH = os.environ.get('SECRET_KEY_REFRESH')

GRAFANA_HOST = os.environ.get('GRAFANA_HOST')
GRAFANA_PORT = os.environ.get('GRAFANA_PORT')
GRAFANA_TOKEN = os.environ.get('GRAFANA_TOKEN')

S3_ACCESS_KEY = os.environ.get('S3ACCESSKEY')
S3_SECRET_KEY = os.environ.get('S3SECRETKEY')