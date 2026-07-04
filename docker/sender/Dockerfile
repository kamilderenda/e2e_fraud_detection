FROM python:3.11-slim

WORKDIR /app

COPY docker/sender/requirements_sender.txt .
RUN pip install --no-cache-dir -r requirements_sender.txt

COPY src/ ./src/
COPY data/ ./data/

CMD ["python", "-m", "src.utils.data_sender"]