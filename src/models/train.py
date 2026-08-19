import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import QuantileTransformer, PowerTransformer, OneHotEncoder
from sklearn.metrics import classification_report, ConfusionMatrixDisplay, fbeta_score, f1_score, recall_score, make_scorer, precision_score, accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.utils.class_weight import compute_sample_weight
from sklearn.base import clone
from xgboost import XGBClassifier
import optuna
import mlflow
from src.models.registry import mlflow_logs

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

def train_and_log(X_train, X_test, y_train, y_test, model_name='Fraud_Detection_Model'):
    mlflow.set_experiment("Recall_PowerTransformer_v2")
    num_process = Pipeline(steps=[
        ('scaler', PowerTransformer())
    ])

    preprocessor = ColumnTransformer(transformers=[
        ('numeric', num_process, X_train.select_dtypes(include=np.number).columns.tolist())
    ], remainder='passthrough')
    with mlflow.start_run(run_name="XGBoost_Optuna_Recall") as parent_run:
        def objective(trial):
            return optuna_objective(trial, preprocessor, X_train, y_train, X_test, y_test)
        study = optuna.create_study(direction='maximize')
        study.optimize(objective, n_trials=80)

        best_trial = study.best_trial

        best_model = XGBClassifier(**best_trial.params, random_state=42, objective='binary:logistic', eval_metric='logloss', verbosity=0, scale_pos_weight=545)
        best_pipeline = Pipeline(steps=[
            ('preprocessor', clone(preprocessor)),
            ('model', best_model)
        ])
        best_pipeline.fit(X_train, y_train)
        y_pred_best = best_pipeline.predict(X_test)
        mlflow_logs(best_trial, y_test, y_pred_best)
        model_info = mlflow.sklearn.log_model(best_pipeline, artifact_path=model_name) 
    return parent_run.info.run_id, model_info.model_uri