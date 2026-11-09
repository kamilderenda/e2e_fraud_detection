import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from src.config.config import DB_CONFIG


def load_data(table_name: str) -> pd.DataFrame:
    connection_url = URL.create(
        "postgresql+psycopg2",
        username=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
        database=DB_CONFIG["dbname"]
    )

    engine = create_engine(connection_url)
    try:
        with engine.connect() as conn:
            query = text(f'SELECT * FROM "{table_name}"')
            data = pd.read_sql_query(query, conn)
        return data

    except Exception as e:
        print(f"Error loading data: {e}")
        raise

    finally:
        engine.dispose()