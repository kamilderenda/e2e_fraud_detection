import time
import requests
import pandas as pd

API_URL = "http://localhost:8000/predict"

def stream_records(df, target_col, interval=3):
    for record in df.to_dict(orient="records"):
        features = {k: v for k, v in record.items() if k != target_col}
        true_value = record[target_col]
        yield features, true_value
        time.sleep(interval)


def send_records(df, target_col, interval=3):
    for features, true_value in stream_records(df, target_col, interval):
        payload = {"features": features, "true_value": int(true_value)}
        try:
            response = requests.post(API_URL, json=payload, timeout=5)
            response.raise_for_status()
            print(response.json())
        except requests.exceptions.RequestException as e:
            print(f"Błąd wysyłki: {e}")


if __name__ == "__main__":
    df = pd.read_csv("twoje_dane.csv") 
    send_records(df, target_col="Class", interval=3)