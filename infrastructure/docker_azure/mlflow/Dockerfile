FROM python:3.11-slim

WORKDIR /mlflow

RUN pip install --no-cache-dir \
    mlflow==3.13.0 \
    psycopg2-binary \
    azure-storage-blob

EXPOSE 5000

CMD ["sh", "-c", "mlflow server \
    --backend-store-uri \"$MLFLOW_BACKEND_STORE_URI\" \
    --default-artifact-root \"$MLFLOW_ARTIFACT_ROOT\" \
    --serve-artifacts \
    --host 0.0.0.0 \
    --port 5000 \
    --allowed-hosts '*'"]