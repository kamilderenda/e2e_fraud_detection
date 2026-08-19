import pandas as pd
# from src.config.loader import load_config

# config = load_config()
cols=['V1', 'V2', 'V3', 'V4', 'V5', 'V7', 'V9', 'V10', 'V11', 'V12', 'V14', 'V16', 'V17', 'V18', 'Class']

def set_columns(data: pd.DataFrame) -> pd.DataFrame:
    if all(col in data.columns for col in cols):
        data = data[cols]
        print("Columns set successfully.")
    else:
        print("Warning: Not all required columns are present in the DataFrame.")
    return data

def save_data(data: pd.DataFrame, file_path: str):
    try:
        data.to_csv(file_path, index=False)
        print(f"Data saved successfully to {file_path}")
    except Exception as e:
        print(f"Error saving data: {e}")