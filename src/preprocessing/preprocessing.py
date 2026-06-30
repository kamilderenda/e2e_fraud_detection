import pandas as pd

cols=['V1', 'V2', 'V3', 'V4', 'V5', 'V7', 'V9', 'V10', 'V11', 'V12', 'V14', 'V16', 'V17', 'V18', 'Class']

def load_data(file_path: str) -> pd.DataFrame:
    try:
        data = pd.read_csv(file_path)
        print(f"Data loaded successfully from {file_path}")
        return data
    except Exception as e:
        print(f"Error loading data: {e}")
        return None
    
def check_missing_values(data: pd.DataFrame):
    missing_values = data.isnull().sum()
    print("Missing values in each column:")
    print(missing_values)

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
    

def run_preprocessing_pipeline():
    df=load_data('data/raw/creditcard_model.csv')
    check_missing_values(df)
    df=set_columns(df)
    save_data(df,'data/processed/creditcard_model_preprocessed.csv')