import pandas as pd
import psycopg2
import os
from evidently import Report
from evidently.presets import DataDriftPreset, ClassificationPreset
import mlflow
from src.inference.config import DB_CONFIG, DB_PROD_TABLE, MODEL_NAME

mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000"))

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

def generate_and_log_drift_report(df_current: pd.DataFrame, report_index: int):
    df_ref_full = pd.read_csv("data/processed/creditcard_model_preprocessed.csv")
    feature_columns = [col for col in df_current.columns if col.startswith("V")]

    reference_data = df_ref_full[feature_columns].copy()
    current_data = df_current[feature_columns].copy()

    reference_data["target"] = df_ref_full["Class"]
    current_data["target"] = df_current["prediction"]

    report = Report(metrics=[
        DataDriftPreset(),
        ClassificationPreset(),
    ])
    report.run(reference_data=reference_data, current_data=current_data)

    report_path = f"/tmp/drift_report_{report_index}.html"
    report.save_html(report_path)

    client = mlflow.tracking.MlflowClient()
    prod_version = client.get_model_version_by_alias(MODEL_NAME, "prod")

    with mlflow.start_run(run_id=prod_version.run_id):
        mlflow.log_artifact(report_path, artifact_path="drift_reports")

    print(f"Raport {report_index} zapisany w MLflow dla modelu {MODEL_NAME}@prod")

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