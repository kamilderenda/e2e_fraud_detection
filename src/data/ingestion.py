import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from src.config.config import DB_CONFIG,DB_RAW_TABLE


def load_data() -> pd.DataFrame:
    try:
        connection_url = URL.create(
            "postgresql+psycopg2",
            username=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            database=DB_CONFIG["dbname"]
        )
        engine = create_engine(connection_url)
        data = pd.read_sql(f"SELECT * FROM {DB_RAW_TABLE}", engine)
        return data
    except Exception as e:
        print(f"Error loading data: {e}")
        return None