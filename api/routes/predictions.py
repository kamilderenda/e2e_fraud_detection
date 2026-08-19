from fastapi import APIRouter
import pandas as pd

from src.database.repository import save_to_db
from api.dependencies import  predict, load_prod_model
from api.schemas import PredictRequest
from src.config.config import MODEL_NAME

router = APIRouter(
    prefix="/predictions",
    tags=["predictions"]
)


@router.post("/predict")
def predict_endpoint(request: PredictRequest):
    df = pd.DataFrame([request.features])

    model = load_prod_model(MODEL_NAME)

    prediction, proba = predict(model, df)

    record_id = save_to_db(
        request.features,
        prediction,
        request.true_value,
        proba
    )

    return {
        "id": record_id,
        "features": request.features,
        "prediction": prediction,
        "probability": proba,
        "true_value": request.true_value,
    }