import mlflow
import sys
import os


def load_prod_model(model_name):
    mlflow.set_tracking_uri("sqlite:///C:/Users/kamil/GitHub/e2e_fraud_detection/mlflow.db")
    client = mlflow.tracking.MlflowClient()
    try:
        prod_version = client.get_model_version_by_alias(model_name, "prod")
    except mlflow.exceptions.MlflowException:
        print("No model on prod.")
        return None

    model_uri = f"models:/{model_name}@prod"
    model = mlflow.sklearn.load_model(model_uri)
    print(f"Loaded prod model version {prod_version.version} (run_id={prod_version.run_id}).")
    return model


def predict(model, df):
    prediction = model.predict(df)[0]
    probability = model.predict_proba(df)[0]
    return int(prediction), float(max(probability))