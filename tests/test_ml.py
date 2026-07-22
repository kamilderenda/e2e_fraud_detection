# tests/test_inference.py
import pytest
import pandas as pd
import numpy as np
from unittest.mock import MagicMock
from src.inference.config import EXPECTED_COLUMNS
from src.inference.inference import predict

def make_sample_df():
    return pd.DataFrame([EXPECTED_COLUMNS], columns=EXPECTED_COLUMNS)

def test_predict_return_tuple():
    mock_model = MagicMock()
    mock_model.predict.return_value = np.array([0])
    mock_model.predict_proba.return_value = np.array([[1.0, 0.0]])
    df = make_sample_df()
    result = predict(mock_model, df)
    assert isinstance(result, tuple)
    assert len(result) == 2

def test_predict_struct_return():
    mock_model = MagicMock()
    mock_model.predict.return_value = np.array([1])
    mock_model.predict_proba.return_value = np.array([[0.0, 1.0]])
    prediction, proba = predict(mock_model, make_sample_df())
    assert isinstance(prediction, int)
    assert isinstance(proba, float)

def test_predict_probability_01range():
    mock_model = MagicMock()
    mock_model.predict.return_value = np.array([0])
    mock_model.predict_proba.return_value = np.array([[1.0, 0.0]])
    _, proba = predict(mock_model, make_sample_df())
    assert 0.0 <= proba <= 1.0

def test_predict_class_0():
    mock_model = MagicMock()
    mock_model.predict.return_value = np.array([0])
    mock_model.predict_proba.return_value = np.array([[0.5, 0.0]])
    prediction, _ = predict(mock_model, make_sample_df())
    assert prediction == 0

def test_predict_class_1():
    mock_model = MagicMock()
    mock_model.predict.return_value = np.array([1])
    mock_model.predict_proba.return_value = np.array([[0.0, 1.0]])
    prediction, _ = predict(mock_model, make_sample_df())
    assert prediction == 1