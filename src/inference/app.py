from fastapi import FastAPI
from config import MODEL_NAME, DB_CONFIG
import pandas as pd
from inference import load_prod_model, predict as run_inference
from pydantic import BaseModel
import psycopg2
import sys
import os
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
app = FastAPI()


@app.on_event("startup")
def startup():
    global model
    model = load_prod_model("Fraud_Detection_Model")


class PredictRequest(BaseModel):
    features: dict
    true_value: int


def save_to_db(features: dict, prediction: int, true_value: int, probability: float):
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cur:
            columns = list(features.keys()) + ["prediction", "true_value", "probability"]
            values = list(features.values()) + [prediction, true_value, probability]

            columns_sql = ", ".join(columns)
            placeholders = ", ".join(["%s"] * len(values))

            query = f"""
                INSERT INTO predictions ({columns_sql})
                VALUES ({placeholders})
                RETURNING id
            """
            cur.execute(query, values)
            new_id = cur.fetchone()[0]
        conn.commit()
        return new_id
    finally:
        conn.close()


@app.post("/predict")
def predict_endpoint(request: PredictRequest):
    df = pd.DataFrame([request.features])
    prediction, proba = run_inference(model, df)

    record_id = save_to_db(request.features, prediction, request.true_value, proba)

    return {
        "id": record_id,
        "features": request.features,
        "prediction": prediction,
        "probability": proba,
        "true_value": request.true_value,
    }