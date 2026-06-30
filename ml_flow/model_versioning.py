import mlflow 
import os
mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000"))


def check_candidate(model_name):
    client = mlflow.tracking.MlflowClient()

    try:
        candidate_version = client.get_model_version_by_alias(model_name, "candidate")
    except mlflow.exceptions.MlflowException:
        print("No candidate model found. Skipping.")
        return

    candidate_recall = client.get_run(candidate_version.run_id).data.metrics.get("best_recall", 0)

    try:
        prod_version = client.get_model_version_by_alias(model_name, "prod")
        prod_recall = client.get_run(prod_version.run_id).data.metrics.get("best_recall", 0)

        if candidate_recall > prod_recall:
            print(f"Promoting candidate v{candidate_version.version} → prod ({candidate_recall:.4f} > {prod_recall:.4f})")
            client.set_registered_model_alias(model_name, "prod", candidate_version.version)
        else:
            print(f"Prod stays (v{prod_version.version}): {prod_recall:.4f} >= {candidate_recall:.4f}")

    except mlflow.exceptions.MlflowException:
        print(f"No prod model. Promoting candidate v{candidate_version.version} → prod")
        client.set_registered_model_alias(model_name, "prod", candidate_version.version)

