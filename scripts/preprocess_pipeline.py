import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.data.ingestion import load_data
from src.data.validation import check_missing_values
from src.data.preprocessing import set_columns, save_train_data
from src.config.config import DB_RAW_TABLE

def run_preprocessing_pipeline():
    df=load_data(DB_RAW_TABLE)
    check_missing_values(df)
    df=set_columns(df)
    save_train_data(df)

if __name__ == "__main__":
    run_preprocessing_pipeline()