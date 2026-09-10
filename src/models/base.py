from abc import ABC, abstractmethod

class ModelStrategy(ABC):
    @abstractmethod
    def train(self, data):
        pass

    @abstractmethod
    def predict(self, input_data):
        pass
    
    @abstractmethod
    def predict_proba(self, input_data):
        pass