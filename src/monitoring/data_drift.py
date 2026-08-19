import pandas as pd
import os
from evidently import Report, DataDefinition, Dataset
from evidently.presets import DataDriftPreset
import mlflow
from src.config.config import MODEL_NAME

mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000"))

def generate_and_log_drift_report(df_current: pd.DataFrame, report_index: int):
    df_ref_full = pd.read_csv("data/processed/creditcard_model_preprocessed.csv")
    feature_columns = [col for col in df_current.columns if col.startswith("V")]

    reference_data = df_ref_full[feature_columns].copy()
    current_data = df_current[feature_columns].copy()

    reference_data["target"] = df_ref_full["Class"]
    current_data["target"] = df_current['true_value']

    schema=DataDefinition(
    numerical_columns=['V1', 'V2', 'V3', 'V4', 'V5', 'V7', 'V9', 'V10', 'V11', 'V12', 'V14', 'V16', 'V17', 'V18'],
    categorical_columns=['target'],
    )

    reference_data = Dataset.from_pandas(
    pd.DataFrame(reference_data),
    data_definition=schema
    )

    current_data = Dataset.from_pandas(
        pd.DataFrame(current_data),
        data_definition=schema
    )
    report = Report([
    DataDriftPreset() 
        ]).run(reference_data=reference_data, current_data=current_data)
    report_path = f"drift_report_{report_index}.html"

    client = mlflow.tracking.MlflowClient()
    prod_version = client.get_model_version_by_alias(MODEL_NAME, "prod")

    mlflow.set_experiment("Drift_Monitoring")
    with mlflow.start_run(run_name=f"drift_report_{report_index}"):
        mlflow.set_tag("model_name", MODEL_NAME)
        mlflow.set_tag("model_version", prod_version.version)
        mlflow.set_tag("model_alias", "prod")
        mlflow.set_tag("report_index", report_index)
        mlflow.log_metric("records_in_batch", len(df_current))
        report.save_html(report_path)
        mlflow.log_artifact(report_path, artifact_path="drift_reports")

    print(f"Raport {report_index} zapisany w MLflow dla modelu {MODEL_NAME}@prod")
