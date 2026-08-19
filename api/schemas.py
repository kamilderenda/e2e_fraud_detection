from pydantic import BaseModel

class PredictRequest(BaseModel):
    features: dict
    true_value: int