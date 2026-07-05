FROM python:3.11-slim

WORKDIR /app

COPY docker/monitoring/requirements_monitoring.txt .
RUN pip install --no-cache-dir -r requirements_monitoring.txt

COPY scripts/ /app/scripts/
COPY src/ /app/src/
COPY ml_flow/ /app/ml_flow/


CMD ["python", "scripts/monitoring_pipeline.py"]