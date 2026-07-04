import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.training.training import *
from ml_flow.model_versioning import *
from src.preprocessing.preprocessing import *
from prefect import flow, task

@task(name="Data Preprocessing", retries=3, retry_delay_seconds=10)
def preprocessing_task():
    print("Uruchamianie czyszczenia danych...")
    run_preprocessing_pipeline()

@task(name='Train and Log Model')
def train_and_log_task(model_name):
    print(f"Training and logging model: {model_name}")
    run_experiment_pipeline(model_name)

@task(name='Check Candidate Model and log to db')
def check_candidate_task(model_name):
    print(f"Checking candidate model: {model_name}")
    model_name, version, run_id, alias, candidate_metrics=check_candidate('Fraud_Detection_Model')
    log_to_db(model_name, version, run_id, alias, candidate_metrics)

@flow(name="E2E Fraud Detection Model Pipeline")
def e2e_fraud_detection_pipeline(model_name):
    preprocessing_task()
    train_and_log_task(model_name)
    check_candidate_task(model_name)

if __name__ == "__main__":
    e2e_fraud_detection_pipeline(model_name='Fraud_Detection_Model')
