FROM python:3.11-slim

WORKDIR /app

COPY infrastructure/docker_azure/monitoring/requirements_monitoring.txt .
RUN pip install --no-cache-dir -r requirements_monitoring.txt

COPY scripts/ /app/scripts/
COPY src/ /app/src/

CMD ["python", "scripts/monitoring_pipeline.py"]