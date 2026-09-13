from models.base import ModelStrategy
from catboost import CatBoostClassifier
from sklearn.pipeline import Pipeline
from sklearn.base import clone

class CatBoostModel(ModelStrategy):
    def __init__(self,preprocessor, **params):
        self.preprocessor = preprocessor
        self.params = params
        self.pipeline = Pipeline(steps=[
            ('preprocessor', clone(self.preprocessor)),
            ('model', CatBoostClassifier(**params))
        ])

    def train(self, X_train, y_train):
        self.pipeline.fit(X_train, y_train)

    def predict(self, X):
        return self.pipeline.predict(X)

    def predict_proba(self, X):
        return self.pipeline.predict_proba(X)

    def get_pipeline(self):
        return self.pipeline