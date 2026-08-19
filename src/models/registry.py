import mlflow
import matplotlib.pyplot as plt
from sklearn.metrics import  ConfusionMatrixDisplay, f1_score, precision_score, accuracy_score



def get_model_by_alias(model_name: str, alias: str):
    client = mlflow.tracking.MlflowClient()
    return client.get_model_version_by_alias(model_name,alias)

def get_model_metrics(run_id: str):
    client = mlflow.tracking.MlflowClient()
    run = client.get_run(run_id)
    return run.data.metrics


def promote_model(model_name: str,version: str,alias: str = "prod"):
    client = mlflow.tracking.MlflowClient()
    client.set_registered_model_alias(model_name,alias,version)
    
def mlflow_logs(best_trial, y_test, y_pred_best):
    mlflow.log_params({f"best_{k}": v for k, v in best_trial.params.items()})
    mlflow.log_metric('best_recall', best_trial.value)
    mlflow.log_metric('best_accuracy', accuracy_score(y_test, y_pred_best))
    mlflow.log_metric('best_f1_score', f1_score(y_test, y_pred_best))
    mlflow.log_metric('best_precision', precision_score(y_test, y_pred_best))
    fig, ax = plt.subplots(figsize=(8, 6))
    ConfusionMatrixDisplay.from_predictions(y_test, y_pred_best, ax=ax)
    mlflow.log_figure(fig, "confusion_matrix.png")
    plt.close(fig)

def mlflow_register_model(model_name, model_uri, alias):
    client = mlflow.tracking.MlflowClient()
    model_version = mlflow.register_model(model_uri=model_uri, name=model_name)
    client.set_registered_model_alias(model_name, alias=alias, version=model_version.version)