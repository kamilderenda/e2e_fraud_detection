import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.config.config import MODEL_NAME
from src.models.train import train_and_log_task


def run_experiment_pipeline(model_name):
    train_and_log_task(model_name)


if __name__ == "__main__":
    run_experiment_pipeline(model_name=MODEL_NAME)