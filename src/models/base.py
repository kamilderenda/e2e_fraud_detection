from abc import ABC, abstractmethod

class ModelStrategy(ABC):
    @abstractmethod
    def train(self, X_train, y_train):
        pass
    
    @abstractmethod
    def predict(self, X):
        pass

    @abstractmethod
    def predict_proba(self, X):
        pass
    @abstractmethod
    def get_pipeline(self):
        pass