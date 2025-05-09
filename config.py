import hvac
import os

from dotenv import load_dotenv
from hvac.exceptions import InvalidPath
from common_lib.logger import logger

load_dotenv()

client = hvac.Client(
    url=os.environ.get('VAULT_URL'),
    token=os.environ.get('VAULT_TOKEN'),
)

try:
    postgres_data = client.secrets.kv.v2.read_secret_version(
        path="Postgres", # Имя секрета
        mount_point='pipif' # Имя engine
    )
    DB_USER = postgres_data['data']['data']['DB_USER']
    DB_PASS = postgres_data['data']['data']['DB_PASS']
    DB_HOST = postgres_data['data']['data']['DB_HOST']
    DB_PORT = int(postgres_data['data']['data']['DB_PORT'])
    DB_NAME = postgres_data['data']['data']['DB_NAME']
except InvalidPath:
    logger.critical('Не найдены параметры подключения к БД Postgres')

try:
    jwt_data = client.secrets.kv.v2.read_secret_version(
        path="Pass_secrets",
        mount_point='pipif'
    )
    SECRET_KEY = jwt_data['data']['data']['SECRET_KEY']
    SECRET_KEY_REFRESH = jwt_data['data']['data']['SECRET_KEY_REFRESH']
except InvalidPath:
    logger.critical('Не найдены параметры JWT')

try:
    grafana_data = client.secrets.kv.v2.read_secret_version(
        path="Grafana",
        mount_point='pipif'
    )
    GRAFANA_HOST = grafana_data['data']['data']['GRAFANA_HOST']
    GRAFANA_PORT = int(grafana_data['data']['data']['GRAFANA_PORT'])
    GRAFANA_TOKEN = grafana_data['data']['data']['GRAFANA_TOKEN']
except InvalidPath:
    logger.critical('Не найдены параметры для Grafana')

try:
    s3_data = client.secrets.kv.read_secret_version(
        path="S3",
        mount_point='pipif'
    )
    S3_ACCESS_KEY = s3_data['data']['data']['S3ACCESSKEY']
    S3_SECRET_KEY = s3_data['data']['data']['S3SECRETKEY']
    S3_SSL_CERT = s3_data['data']['data']['S3SSLCERT']
except InvalidPath:
    logger.critical('Не найдены параметры для S3')