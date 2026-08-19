from fastapi import FastAPI
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from api.routes import predictions

app = FastAPI(
    title="Fraud Detection API",
    version="1.0.0"
)

app.include_router(predictions.router)