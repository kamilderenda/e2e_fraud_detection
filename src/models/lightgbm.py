from models.base import BaseModel
from lightgbm import LGBMClassifier
from sklearn.pipeline import Pipeline
from sklearn.base import clone

class LightGBMModel(BaseModel):
    def __init__(self,preprocessor, **params):
        self.model = LGBMClassifier(**params)
        self.preprocessor=preprocessor
        self.pipeline = Pipeline(steps=[
            ('preprocessor', clone(self.preprocessor)),
            ('model', self.model)
        ])
        
    def train(self, X_train, y_train):
        self.pipeline.fit(X_train, y_train)
    
    def predict(self, X):
        return self.model.predict(X)
    
    def predict_proba(self, X):
        return self.model.predict_proba(X)
    
    def score(self, X, y):
        return self.model.score(X, y)