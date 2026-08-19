from src.models.registry import get_model_by_alias,get_model_metrics,promote_model

def check_candidate(model_name: str):
    try:
        candidate = get_model_by_alias(model_name,"candidate")
    except Exception:
        print("No candidate model found. Skipping.")
        return None

    candidate_metrics = get_model_metrics(candidate.run_id)
    candidate_recall = candidate_metrics.get("best_recall",0)

    try:
        production = get_model_by_alias(model_name,"prod")
        production_metrics = get_model_metrics(production.run_id)
        production_recall = production_metrics.get("best_recall",0)

        if candidate_recall > production_recall:
            print(f"Promoting candidate {candidate.version} → prod")
            promote_model(model_name,candidate.version,"prod")
            alias = "prod"
        else:
            print(f"Prod stays (v{production.version}): {production_recall:.4f} >= {candidate_recall:.4f}")
            alias = "candidate"

    except Exception:

        print(f"No prod model. Promoting candidate {candidate.version} → prod")
        promote_model(model_name,candidate.version,"prod")
        alias = "prod"
    return (model_name,candidate.version,candidate.run_id,alias,candidate_metrics,)