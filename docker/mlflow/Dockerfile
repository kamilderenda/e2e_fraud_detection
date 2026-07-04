FROM python:3.11-slim

WORKDIR /mlflow

RUN pip install --no-cache-dir mlflow==3.13.0 psycopg2-binary

EXPOSE 5000

CMD mlflow server \
    --backend-store-uri postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/${DB_NAME} \
    --default-artifact-root file:///mlflow/data/mlruns \
    --serve-artifacts \
    --host 0.0.0.0 \
    --port 5000 \
    --allowed-hosts "*"