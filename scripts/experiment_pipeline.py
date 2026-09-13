import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import PowerTransformer

from src.database.repository import log_to_db, load_data
from src.models.registry import mlflow_register_model
from src.models.evaluate import check_candidate
from src.models.base_trainer import XGBoostTrainer
from prefect import flow, task


@task(name='Train and Log Model')
def train_and_log_task(model_name):
    data = load_data('data/processed/creditcard_model_preprocessed.csv')

    trainer = XGBoostTrainer()
    X_train, X_test, y_train, y_test = trainer.train_test_split(data, target_column='Class')

    num_process = Pipeline(steps=[('scaler', PowerTransformer())])
    preprocessor = ColumnTransformer(transformers=[
        ('numeric', num_process, X_train.select_dtypes(include=np.number).columns.tolist())
    ], remainder='passthrough')

    run_id, model_uri = trainer.run_process(preprocessor, X_train, y_train, X_test, y_test)
    mlflow_register_model(model_name=model_name, model_uri=model_uri, alias='candidate')


@task(name='Check Candidate Model and log to db')
def check_candidate_task(model_name):
    print(f"Checking candidate model: {model_name}")
    model_name, version, run_id, alias, candidate_metrics = check_candidate(model_name)
    log_to_db(model_name, version, run_id, alias, candidate_metrics)


@flow(name="E2E Fraud Detection Model Pipeline")
def e2e_fraud_detection_pipeline(model_name):
    train_and_log_task(model_name)
    check_candidate_task(model_name)


if __name__ == "__main__":
    e2e_fraud_detection_pipeline(model_name='Fraud_Detection_Model')