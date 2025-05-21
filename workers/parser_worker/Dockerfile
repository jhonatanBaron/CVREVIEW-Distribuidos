# workers/parser_worker/Dockerfile
FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copia las dependencias y el código de la API
COPY api/requirements.txt /app/requirements.txt
RUN apt-get update && apt-get install -y build-essential && \
    pip install --upgrade pip && \
    pip install -r requirements.txt && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copia el código de la API y del worker
COPY api /app/api
COPY workers/parser_worker/worker.py /app/worker.py

CMD ["python", "worker.py"]
