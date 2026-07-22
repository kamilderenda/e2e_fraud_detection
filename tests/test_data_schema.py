import pandas as pd
import pytest
from unittest.mock import MagicMock, patch
from src.inference.config import EXPECTED_COLUMNS


def make_valid_features():
    return {col: 0.0 for col in EXPECTED_COLUMNS}

def test_required_columns():
    features = make_valid_features()
    for col in EXPECTED_COLUMNS:
        assert col in features, f"Brakuje kolumny: {col}"

def test_lack_required_column():
    features = make_valid_features()
    del features["V1"]
    missing = [col for col in EXPECTED_COLUMNS if col not in features]
    assert len(missing) > 0

def test_numeric_values():
    features = make_valid_features()
    for col, val in features.items():
        assert isinstance(val, (int, float)), f"Kolumna {col} ma nieoczekiwany typ: {type(val)}"

def test_lack_of_na():
    import math
    features = make_valid_features()
    for col, val in features.items():
        assert not math.isnan(float(val)), f"Kolumna {col} zawiera NaN"

def test_one_row_input():
    features = make_valid_features()
    df = pd.DataFrame([features])
    assert len(df) == 1
    assert list(df.columns) == EXPECTED_COLUMNS