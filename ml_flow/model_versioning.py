import mlflow 
import os
from src.inference.config import DB_MLFLOW_CONFIG
import psycopg2
mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000"))


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

def check_candidate(model_name):
    client = mlflow.tracking.MlflowClient()
    alias="candidate"
    try:
        candidate_version = client.get_model_version_by_alias(model_name, "candidate")
    except mlflow.exceptions.MlflowException:
        print("No candidate model found. Skipping.")
        return

    candidate_recall = client.get_run(candidate_version.run_id).data.metrics.get("best_recall", 0)
    candidate_run = client.get_run(candidate_version.run_id)
    candidate_metrics = candidate_run.data.metrics

    try:
        prod_version = client.get_model_version_by_alias(model_name, "prod")
        prod_recall = client.get_run(prod_version.run_id).data.metrics.get("best_recall", 0)

        if candidate_recall > prod_recall:
            print(f"Promoting candidate v{candidate_version.version} → prod")
            client.set_registered_model_alias(model_name, "prod", candidate_version.version)
            alias = "prod"
        else:
            print(f"Prod stays (v{prod_version.version}): {prod_recall:.4f} >= {candidate_recall:.4f}")

    except mlflow.exceptions.MlflowException:
        print(f"No prod model. Promoting candidate v{candidate_version.version} → prod")
        client.set_registered_model_alias(model_name, "prod", candidate_version.version)
        alias = "prod"
    return model_name, candidate_version.version, candidate_version.run_id, alias, candidate_metrics

