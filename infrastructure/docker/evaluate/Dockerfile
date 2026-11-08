FROM python:3.11-slim

WORKDIR /app

RUN pip install mlflow==3.13.0 scikit-learn==1.9.0 psycopg2-binary==2.9.12 pandas==2.3.3

COPY scripts/ /app/scripts/
COPY src/ /app/src/

CMD ["python", "scripts/evaluate_pipeline.py"]