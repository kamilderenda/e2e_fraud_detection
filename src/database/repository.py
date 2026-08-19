import psycopg2
import pandas as pd
from src.config.config import DB_MLFLOW_CONFIG, DB_CONFIG, DB_PROD_TABLE

def log_to_db(model_name, version, run_id, alias, metrics):
    conn = psycopg2.connect(**DB_MLFLOW_CONFIG)
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO mlflow_experiments 
                    (model_name, model_uri, run_id, alias,version, recall, precision, f1_score, accuracy)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                model_name,
                f"models:/{model_name}@{alias}",
                run_id,
                alias,
                version,
                metrics.get("best_recall"),
                metrics.get("best_precision"),
                metrics.get("best_f1_score"),
                metrics.get("best_accuracy"),
            ))
        conn.commit()
    finally:
        conn.close()

def save_to_db(features: dict, prediction: int, true_value: int, probability: float):
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cur:
            columns = list(features.keys()) + ["prediction", "true_value", "probability"]
            values = list(features.values()) + [prediction, true_value, probability]

            columns_sql = ", ".join(f'"{col}"' for col in columns)
            placeholders = ", ".join(["%s"] * len(values))

            query = f"""
                INSERT INTO {DB_PROD_TABLE} ({columns_sql})
                VALUES ({placeholders})
                RETURNING id
            """
            cur.execute(query, values)
            new_id = cur.fetchone()[0]
        conn.commit()
        return new_id
    finally:
        conn.close()
        
def load_data(file_path):
    return pd.read_csv(file_path)

def get_record_count() -> int:
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) FROM {DB_PROD_TABLE}")
            return cur.fetchone()[0]
    finally:
        conn.close()

def get_last_monitored_count() -> int:
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT records_count FROM monitoring_log
                ORDER BY created_at DESC
                LIMIT 1
            """)
            row = cur.fetchone()
            return row[0] if row else 0
    finally:
        conn.close()
        
def log_monitoring_checkpoint(records_count: int):
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO monitoring_log (records_count)
                VALUES (%s)
            """, (records_count,))
        conn.commit()
    finally:
        conn.close()

def fetch_production_data(offset: int, limit: int = 100) -> pd.DataFrame:
    conn = psycopg2.connect(**DB_CONFIG)
    query = f"""
        SELECT * FROM {DB_PROD_TABLE}
        ORDER BY created_at ASC
        LIMIT {limit} OFFSET {offset}
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df