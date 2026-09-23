from abc import ABC, abstractmethod
from sklearn.model_selection import train_test_split
from sklearn.metrics import recall_score
import mlflow
import optuna
from src.models.xgboost import XGBoostModel
from src.models.lightgbm import LightGBMModel
from src.models.catboost import CatBoostModel
from src.models.registry import mlflow_logs
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import PowerTransformer

class Trainer(ABC):

    EXPERIMENT_NAME: str = "def_experiment"
    RUN_NAME: str = "deft_run"
    MODEL_NAME: str = "def_model"

    def evaluate(self, model, X_test, y_test) -> float:
        y_pred = model.predict(X_test)
        return recall_score(y_test, y_pred)

    @abstractmethod
    def build_model(self, preprocessor, **params) -> object:
        pass

    @abstractmethod
    def get_optuna_params(self, trial) -> dict:
        pass

    @abstractmethod
    def evaluate(self, model, X_test, y_test) -> float:
        pass
    
    def build_preprocessor(self, X_train):
        num_process = Pipeline(steps=[('scaler', PowerTransformer())])
        preprocessor = ColumnTransformer(transformers=[
            ('numeric', num_process, X_train.select_dtypes(include='number').columns.tolist())
        ], remainder='passthrough')
        return preprocessor

    def run_process(self, X_train, y_train, X_test, y_test):
        mlflow.set_experiment(self.EXPERIMENT_NAME)
        preprocessor = self.build_preprocessor(X_train)
        with mlflow.start_run(run_name=self.RUN_NAME) as parent_run:

            def objective(trial):
                params = self.get_optuna_params(trial)
                model = self.build_model(preprocessor, **params)
                model.train(X_train, y_train)
                return self.evaluate(model, X_test, y_test)

            study = optuna.create_study(direction='maximize')
            study.optimize(objective, n_trials=80)

            best_trial = study.best_trial
            best_model = self.build_model(preprocessor, **best_trial.params)
            best_model.train(X_train, y_train)

            y_pred = best_model.predict(X_test)
            best_score = self.evaluate(best_model, X_test, y_test)
            mlflow_logs(best_trial, y_test, y_pred)
            model_info = mlflow.sklearn.log_model(
                best_model.get_pipeline(),
                artifact_path=self.MODEL_NAME
            )

        return parent_run.info.run_id, model_info.model_uri, best_score
    
class XGBoostTrainer(Trainer):

    EXPERIMENT_NAME = "Recall_PowerTransformer_v2"
    RUN_NAME = "XGBoost_Optuna_Recall"
    MODEL_NAME = "Churn_XGBoost_Model"

    FIXED_PARAMS = {
        'random_state': 42,
        'objective': 'binary:logistic',
        'eval_metric': 'logloss',
        'scale_pos_weight': 545,
        'verbosity': 0,
    }

    def build_model(self, preprocessor, **params):
        return XGBoostModel(preprocessor, **self.FIXED_PARAMS, **params)

    def get_optuna_params(self, trial) -> dict:
        return {
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
     
class LGBMTrainer(Trainer):

    EXPERIMENT_NAME = "Recall_PowerTransformer_v2"
    RUN_NAME = "LGBM_Optuna_Recall"
    MODEL_NAME = "Churn_LGBM_Model"

    FIXED_PARAMS = {
        'objective': 'binary',
        'metric': 'binary_logloss',
        'scale_pos_weight': 545,
        'verbosity': -1,
        'random_state': 42,
        'n_jobs': -1,
    }

    def build_model(self, preprocessor, **params):
        return LightGBMModel(preprocessor, **self.FIXED_PARAMS, **params)

    def get_optuna_params(self, trial) -> dict:
        return {
            'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3, log=True),
            'n_estimators': trial.suggest_int('n_estimators', 100, 1000),
            'max_depth': trial.suggest_int('max_depth', 3, 12),
            'num_leaves': trial.suggest_int('num_leaves', 20, 300),
            'min_child_samples': trial.suggest_int('min_child_samples', 5, 100),
            'subsample': trial.suggest_float('subsample', 0.1, 1.0),
            'subsample_freq': trial.suggest_int('subsample_freq', 1, 10),
            'colsample_bytree': trial.suggest_float('colsample_bytree', 0.1, 1.0),
            'reg_alpha': trial.suggest_float('reg_alpha', 0, 1),
            'reg_lambda': trial.suggest_float('reg_lambda', 0, 2),
            'min_split_gain': trial.suggest_float('min_split_gain', 0, 1),
        }


class CatTrainer(Trainer):

    EXPERIMENT_NAME = "Recall_PowerTransformer_v2"
    RUN_NAME = "CatBoost_Optuna_Recall"
    MODEL_NAME = "Churn_CatBoost_Model"

    FIXED_PARAMS = {
        'loss_function': 'Logloss',
        'eval_metric': 'Recall',
        'scale_pos_weight': 545,
        'verbose': 0,
        'random_seed': 42,
        'thread_count': -1,
    }

    def build_model(self, preprocessor, **params):
        return CatBoostModel(preprocessor, **self.FIXED_PARAMS, **params)

    def get_optuna_params(self, trial) -> dict:
        return {
        'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3, log=True),
        'iterations': trial.suggest_int('iterations', 100, 1000),
        'depth': trial.suggest_int('depth', 3, 10),
        'l2_leaf_reg': trial.suggest_float('l2_leaf_reg', 1, 10),
        'bagging_temperature': trial.suggest_float('bagging_temperature', 0, 1),
        'random_strength': trial.suggest_float('random_strength', 0, 1),
        'border_count': trial.suggest_int('border_count', 32, 255),
        'min_data_in_leaf': trial.suggest_int('min_data_in_leaf', 1, 50),   
        }
