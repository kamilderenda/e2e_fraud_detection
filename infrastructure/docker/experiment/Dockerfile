FROM python:3.11-slim

WORKDIR /app

COPY infrastructure/docker/experiment/requirements_training.txt .
RUN apt-get update && apt-get install -y \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r requirements_training.txt --break-system-packages || pip install --no-cache-dir -r requirements_training.txt

COPY scripts/ /app/scripts/
COPY src/ /app/src/

CMD ["python", "scripts/experiment_pipeline.py"]