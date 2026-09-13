import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.database.repository import log_to_db, load_data
from src.models.registry import mlflow_register_model
from src.models.evaluate import check_candidate
from src.models.trainer_factory import TrainerFactory
from src.utils.train_test_split import train_test_split_data
from prefect import flow, task


@task(name='Train and Log Model')
def train_and_log_task(model_name):
    data = load_data('data/processed/creditcard_model_preprocessed.csv')

    X_train, X_test, y_train, y_test = train_test_split_data(data, target_column='Class')

    trainers = TrainerFactory.create_all()

    results = []
    for trainer in trainers:
        run_id, model_uri, best_score = trainer.run_process(X_train, y_train, X_test, y_test)
        results.append((best_score, model_uri, run_id))
        print(f"{trainer.__class__.__name__}: recall={best_score:.4f}, run_id={run_id}")

    best_score, best_uri, best_run_id = max(results, key=lambda x: x[0])
    print(f"Best model: recall={best_score:.4f}, uri={best_uri}")
    mlflow_register_model(model_name=model_name, model_uri=best_uri, alias='candidate')


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