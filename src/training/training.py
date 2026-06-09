import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import QuantileTransformer, PowerTransformer, OneHotEncoder
from sklearn.metrics import classification_report, ConfusionMatrixDisplay, fbeta_score, f1_score, recall_score, make_scorer, precision_score, accuracy_score
from sklearn.model_selection import train_test_split, StratifiedKFold, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score
from sklearn.utils.class_weight import compute_sample_weight
from sklearn.base import clone
from category_encoders import TargetEncoder
from xgboost import XGBClassifier
from catboost import CatBoostClassifier
import lightgbm as lgb
import optuna
import mlflow
import matplotlib.pyplot as plt

def load_data(file_path):
    return pd.read_csv(file_path)

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

def mlflow_register_model(model_name,run_id, alias):
    client = mlflow.tracking.MlflowClient()
    model_version=mlflow.register_model(model_uri=f"runs:/{run_id}/{model_name}", name=model_name)
    client.set_registered_model_alias(model_name, alias=alias, version=model_version.version)


def train_and_log(X_train, X_test,y_train,y_test, model_name='Fraud_Detection_Model'):
    mlflow.set_experiment("Recall_PowerTransformer")
    num_process=Pipeline(steps=[
        ('scaler', PowerTransformer())
    ])

    preprocessor=ColumnTransformer(transformers=[
        ('numeric', num_process, X_train.select_dtypes(include=np.number).columns.tolist())
    ], remainder='passthrough')
    with mlflow.start_run(run_name="XGBoost_Optuna_Recall") as parent_run:
        def objective(trial):
            return optuna_objective(trial, preprocessor, X_train, y_train, X_test, y_test)
        study = optuna.create_study(direction='maximize')
        study.optimize(objective, n_trials=10)

        best_trial = study.best_trial

        best_model = XGBClassifier(**best_trial.params, random_state=42, objective='binary:logistic', eval_metric='logloss', verbosity=0, scale_pos_weight=545)
        best_pipeline = Pipeline(steps=[
            ('preprocessor', clone(preprocessor)),
            ('model', best_model)
        ])
        best_pipeline.fit(X_train, y_train)
        y_pred_best = best_pipeline.predict(X_test)
        mlflow_logs(best_trial, y_test, y_pred_best)
        mlflow.sklearn.log_model(best_pipeline, name=model_name)
    return parent_run.info.run_id

def run_experiment_pipeline(model_name):
    data = load_data('data/processed/creditcard_model_preprocessed.csv')
    X_train, X_test, y_train, y_test = train_test_split_data(data, target_column='Class')
    run_id=train_and_log(X_train, X_test, y_train, y_test)
    mlflow_register_model(model_name=model_name, run_id=run_id, alias='candidate')