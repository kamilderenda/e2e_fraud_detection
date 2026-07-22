# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from src.inference.config import VALID_FEATURES
import numpy as np

with patch("src.inference.inference.mlflow"):
    from src.inference.app import app

@pytest.fixture
def client():
    mock_model = MagicMock()
    mock_model.predict.return_value = np.array([0])
    mock_model.predict_proba.return_value = np.array([[0.9, 0.1]])

    with patch("src.inference.app.model", mock_model):
        with patch("src.inference.app.save_to_db", return_value=1):
            yield TestClient(app)

def test_predict_endpoint(client):
    response = client.post("/predict", json={
        "features": VALID_FEATURES,
        "true_value": 0
    })
    assert response.status_code == 200

def test_predict_endpoint_json(client):
    response = client.post("/predict", json={
        "features": VALID_FEATURES,
        "true_value": 0
    })
    data = response.json()
    assert "id" in data
    assert "prediction" in data
    assert "probability" in data
    assert "true_value" in data

def test_predict_endpoint_prediction(client):
    response = client.post("/predict", json={
        "features": VALID_FEATURES,
        "true_value": 0
    })
    assert response.json()["prediction"] in [0, 1]

def test_predict_endpoint_probability(client):
    response = client.post("/predict", json={
        "features": VALID_FEATURES,
        "true_value": 0
    })
    proba = response.json()["probability"]
    assert 0.0 <= proba <= 1.0

def test_predict_endpoint_empty_request(client):
    response = client.post("/predict", json={})
    assert response.status_code == 422