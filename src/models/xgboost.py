from models.base import BaseModel
from xgboost import XGBClassifier

class XGBoostModel(BaseModel):
    def __init__(self, **params):
        self.model = XGBClassifier(**params)
        
    def train(self, X_train, y_train):
        self.model.fit(X_train, y_train)
    
    def predict(self, X):
        return self.model.predict(X)
    
    def predict_proba(self, X):
        return self.model.predict_proba(X)