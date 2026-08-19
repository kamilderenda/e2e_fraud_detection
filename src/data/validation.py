import pandas as pd

def check_missing_values(data: pd.DataFrame):
    missing_values = data.isnull().sum()
    print("Missing values in each column:")
    print(missing_values)