import mlflow 
import pandas as pd
import numpy as np

def check_candidate(model_name):
    client = mlflow.tracking.MlflowClient()
    candidate_version = client.get_model_version_by_alias(model_name, alias="candidate")
    candidate_recall = client.get_run(candidate_version.run_id).data.metrics["best_recall"]
    # print(mlflow.get_tracking_uri())
    try:
        prod_version = client.get_model_version_by_alias(model_name, "prod")
        prod_recall = client.get_run(prod_version.run_id).data.metrics["best_recall"]
        if candidate_recall > prod_recall:
            print(f"Candidate is better ({candidate_recall:.4f} > {prod_recall:.4f}).")
            client.delete_registered_model_alias(model_name, alias="candidate")
            client.set_registered_model_alias(model_name, alias="prod", version=candidate_version.version)
        else:
            print(f"Prod is better ({prod_recall:.4f} >= {candidate_recall:.4f}).")
    except mlflow.exceptions.MlflowException:
        print("No Model on prod.")
        client.set_registered_model_alias(model_name, alias="prod", version=candidate_version.version)

