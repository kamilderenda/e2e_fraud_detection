from abc import ABC, abstractmethod
from sklearn.model_selection import train_test_split
from sklearn.metrics import recall_score
import mlflow
import optuna
from src.models.xgboost import XGBoostModel
from src.models.registry import mlflow_logs

class Trainer(ABC):

    EXPERIMENT_NAME: str = "default_experiment"
    RUN_NAME: str = "default_run"
    MODEL_NAME: str = "default_model"

    def train_test_split(self, data, target_column, test_size=0.2, random_state=42):
        X = data.drop(columns=[target_column])
        y = data[target_column]
        return train_test_split(X, y,test_size=test_size,random_state=random_state,stratify=y)

    @abstractmethod
    def build_model(self, preprocessor, **params) -> object:
        pass

    @abstractmethod
    def get_optuna_params(self, trial) -> dict:
        pass

    @abstractmethod
    def evaluate(self, model, X_test, y_test) -> float:
        pass

    def run_process(self, preprocessor, X_train, y_train, X_test, y_test):
        mlflow.set_experiment(self.EXPERIMENT_NAME)

        with mlflow.start_run(run_name=self.RUN_NAME) as parent_run:

            def objective(trial):
                params = self.get_optuna_params(trial)
                model = self.build_model(preprocessor, **params)
                model.train(X_train, y_train)
                return self.evaluate(model, X_test, y_test)

            study = optuna.create_study(direction='maximize')
            study.optimize(objective, n_trials=100)

            best_trial = study.best_trial
            best_model = self.build_model(preprocessor, **best_trial.params)
            best_model.train(X_train, y_train)

            y_pred = best_model.predict(X_test)
            mlflow_logs(best_trial, y_test, y_pred)
            model_info = mlflow.sklearn.log_model(
                best_model.get_pipeline(),
                artifact_path=self.MODEL_NAME
            )

        return parent_run.info.run_id, model_info.model_uri
    
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

    def evaluate(self, model, X_test, y_test) -> float:
        y_pred = model.predict(X_test)
        return recall_score(y_test, y_pred)