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

#TESTS
VALID_FEATURES = {
    "V1": -1.36, "V2": -0.07, "V3": 2.53, "V4": 1.38,
    "V5": -0.34, "V7": 0.24, "V9": 0.36, "V10": 0.09,
    "V11": -0.55, "V12": -0.62, "V14": -0.31, "V16": -0.47,
    "V17": 0.21, "V18": 0.03
}

EXPECTED_COLUMNS = [
    "V1", "V2", "V3", "V4", "V5", "V7", "V9", "V10",
    "V11", "V12", "V14", "V16", "V17", "V18"
]