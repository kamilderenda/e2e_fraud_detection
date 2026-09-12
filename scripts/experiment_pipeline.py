import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.database.repository import log_to_db, load_data
from src.models.train import *
from src.models.registry import mlflow_register_model
from src.models.evaluate import check_candidate
from scripts.preprocess_pipeline import run_preprocessing_pipeline
from prefect import flow, task

def run_experiment_pipeline(model_name):
    data = load_data('data/processed/creditcard_model_preprocessed.csv')
    X_train, X_test, y_train, y_test = train_test_split_data(data, target_column='Class')
    run_id, model_uri = train_and_log(X_train, X_test, y_train, y_test)
    mlflow_register_model(model_name=model_name, model_uri=model_uri, alias='candidate')

@task(name='Train and Log Model')
def train_and_log_task(model_name):
    print(f"Training and logging model: {model_name}")
    data = load_data('data/processed/creditcard_model_preprocessed.csv')
    X_train, X_test, y_train, y_test = train_test_split_data(data, target_column='Class')
    run_id, model_uri = train_and_log(X_train, X_test, y_train, y_test)
    mlflow_register_model(model_name=model_name, model_uri=model_uri, alias='candidate')

@task(name='Check Candidate Model and log to db')
def check_candidate_task(model_name):
    print(f"Checking candidate model: {model_name}")
    model_name, version, run_id, alias, candidate_metrics=check_candidate('Fraud_Detection_Model')
    log_to_db(model_name, version, run_id, alias, candidate_metrics)

@flow(name="E2E Fraud Detection Model Pipeline")
def e2e_fraud_detection_pipeline(model_name):
    train_and_log_task(model_name)
    check_candidate_task(model_name)

if __name__ == "__main__":
    e2e_fraud_detection_pipeline(model_name='Fraud_Detection_Model')
