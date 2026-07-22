from fastapi import FastAPI
from src.inference.config import MODEL_NAME, DB_CONFIG, DB_PROD_TABLE
import pandas as pd
from src.inference.inference import load_prod_model, predict as run_inference
from pydantic import BaseModel
import psycopg2

model=None
app = FastAPI()

@app.on_event("startup")
def startup():
    global model
    model = load_prod_model(MODEL_NAME)


class PredictRequest(BaseModel):
    features: dict
    true_value: int


def save_to_db(features: dict, prediction: int, true_value: int, probability: float):
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cur:
            columns = list(features.keys()) + ["prediction", "true_value", "probability"]
            values = list(features.values()) + [prediction, true_value, probability]

            columns_sql = ", ".join(f'"{col}"' for col in columns)
            placeholders = ", ".join(["%s"] * len(values))

            query = f"""
                INSERT INTO {DB_PROD_TABLE} ({columns_sql})
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