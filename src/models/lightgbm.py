from src.models.base import ModelStrategy
from lightgbm import LGBMClassifier
from sklearn.pipeline import Pipeline
from sklearn.base import clone

class LightGBMModel(ModelStrategy):
    def __init__(self, preprocessor, **params):
        self.preprocessor = preprocessor
        self.params = params
        self.pipeline = Pipeline(steps=[
            ('preprocessor', clone(self.preprocessor)),
            ('model', LGBMClassifier(**params))
        ])

    def train(self, X_train, y_train):
        self.pipeline.fit(X_train, y_train)

    def predict(self, X):
        return self.pipeline.predict(X)

    def predict_proba(self, X):
        return self.pipeline.predict_proba(X)

    def get_pipeline(self):
        return self.pipeline