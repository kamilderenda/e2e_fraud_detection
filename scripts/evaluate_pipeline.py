from src.models.evaluate import check_candidate
from src.database.repository import log_to_db
from src.config.config import MODEL_NAME
    
def run_evaluate_pipeline(model_name):
    model_name, version, run_id, alias, candidate_metrics = check_candidate(MODEL_NAME)
    log_to_db(model_name, version, run_id, alias, candidate_metrics)


if __name__ == "__main__":
    run_evaluate_pipeline(model_name=MODEL_NAME)