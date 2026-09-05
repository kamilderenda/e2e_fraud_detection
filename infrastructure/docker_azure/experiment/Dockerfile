FROM python:3.11-slim

WORKDIR /app

COPY infrastructure/docker_azure/experiment/requirements_training.txt .
RUN pip install --no-cache-dir -r requirements_training.txt --break-system-packages || pip install --no-cache-dir -r requirements_training.txt

COPY scripts/ /app/scripts/
COPY src/ /app/src/
COPY data/ /app/data/

CMD ["python", "scripts/experiment_pipeline.py"]