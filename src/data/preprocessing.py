import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from src.config.config import DB_CONFIG,DB_TRAIN_TABLE

# config = load_config()
cols=['V1', 'V2', 'V3', 'V4', 'V5', 'V7', 'V9', 'V10', 'V11', 'V12', 'V14', 'V16', 'V17', 'V18', 'Class']

def set_columns(data: pd.DataFrame) -> pd.DataFrame:
    if all(col in data.columns for col in cols):
        data = data[cols]
        print("Columns set successfully.")
    else:
        print("Warning: Not all required columns are present in the DataFrame.")
    return data

def save_train_data(data: pd.DataFrame):
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

        data.to_sql(
            DB_TRAIN_TABLE,
            engine,
            if_exists="replace",
            index=False
        )
    except Exception as e:
        print(f"Error saving data: {e}")