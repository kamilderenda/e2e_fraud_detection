FROM python:3.11-slim

WORKDIR /app

RUN pip install pandas==3.1.1 SQLAlchemy==2.1.8 dotenv==0.9.9 psycopg2-binary==2.9.12

COPY scripts/ /app/scripts/
COPY src/ /app/src/

CMD ["python", "scripts/preprocess_pipeline.py"]