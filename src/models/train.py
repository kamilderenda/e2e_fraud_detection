from sklearn.pipeline import Pipeline
from sklearn.metrics import recall_score
from sklearn.model_selection import train_test_split
from sklearn.base import clone
from xgboost import XGBClassifier
from src.models.trainer_factory import TrainerFactory
from src.models.registry import mlflow_register_model
from src.data.ingestion import load_data
from src.config.config import DB_TRAIN_TABLE

def train_test_split_data(data, target_column, test_size=0.2, random_state=42):
    X = data.drop(columns=[target_column])
    y = data[target_column]
    return train_test_split(X, y, test_size=test_size, random_state=random_state, stratify=y)

def fit_model(params, preprocessor, X_train, y_train, X_test, y_test):
    model = XGBClassifier(**params)
    pipeline = Pipeline(steps=[
        ('preprocessor', clone(preprocessor)),
        ('model', model)
    ])
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)
    recall = recall_score(y_test, y_pred)
    return recall

def optuna_objective(trial, preprocessor, X_train, y_train, X_test, y_test):
    params = {
        'random_state': 42,
        'objective':'binary:logistic',
        'eval_metric':'logloss',
        'scale_pos_weight':545,
        'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3, log=True),
        'n_estimators': trial.suggest_int('n_estimators', 100, 1000),
        'max_depth': trial.suggest_int('max_depth', 2, 10),
        'subsample': trial.suggest_float('subsample', 0.1, 1.0),
        'colsample_bytree': trial.suggest_float('colsample_bytree', 0.1, 1.0),
        'colsample_bynode': trial.suggest_float('colsample_bynode', 0.1, 1.0),
        'gamma': trial.suggest_float('gamma', 0, 1),
        'reg_alpha': trial.suggest_float('reg_alpha', 0, 1),
        'reg_lambda': trial.suggest_float('reg_lambda', 0, 2),
        'max_delta_step': trial.suggest_int('max_delta_step', 1, 10),
        'min_child_weight': trial.suggest_float('min_child_weight', 0.1, 10),
    }

    recall = fit_model(params, preprocessor, X_train, y_train, X_test, y_test)
    return recall

def train_and_log_task(model_name):
    data = load_data(DB_TRAIN_TABLE)

    X_train, X_test, y_train, y_test = train_test_split_data(data=data, target_column='Class')

    trainers = TrainerFactory.create_all()

    results = []
    for trainer in trainers:
        run_id, model_uri, best_score = trainer.run_process(X_train, y_train, X_test, y_test)
        results.append((best_score, model_uri, run_id))
        print(f"{trainer.__class__.__name__}: recall={best_score:.4f}, run_id={run_id}")

    best_score, best_uri, best_run_id = max(results, key=lambda x: x[0])
    print(f"Best model: recall={best_score:.4f}, uri={best_uri}")
    mlflow_register_model(model_name=model_name, model_uri=best_uri, alias='candidate')