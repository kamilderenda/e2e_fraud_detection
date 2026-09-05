FROM python:3.11-slim

WORKDIR /app

COPY infrastructure/docker_azure/api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api/ ./api/
COPY src/config ./src/config/
COPY src/database ./src/database/

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]