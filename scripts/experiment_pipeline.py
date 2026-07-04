import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.training.training import *
from ml_flow.model_versioning import *


if __name__ == "__main__":
    run_experiment_pipeline('Fraud_Detection_Model')
    model_name, version, run_id, prod, candidate_metrics=check_candidate('Fraud_Detection_Model')
    log_to_db(model_name, version, run_id, prod, candidate_metrics)
