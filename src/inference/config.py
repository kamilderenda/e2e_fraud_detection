import os
from dotenv import load_dotenv

load_dotenv()
API_URL = os.getenv("API_URL", "http://localhost:8000/predict")

MODEL_NAME = os.getenv("MODEL_NAME")

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT")),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}

DB_PROD_TABLE = os.getenv('DB_PROD_TABLE',"prod_table")

DB_MLFLOW_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT")),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}

DB_MLFLOW_TABLE = os.getenv('DB_MLFLOW_TABLE',"mlflow_table")

PREFECT_API_URL=os.getenv("PREFECT_API_URL")
PREFECT_API_KEY=os.getenv("PREFECT_API_KEY")