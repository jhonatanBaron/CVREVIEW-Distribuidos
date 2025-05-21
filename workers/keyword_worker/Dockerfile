# En workers/keyword_worker/Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY api/requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

COPY api /app/api
COPY workers/keyword_worker/worker.py /app/worker.py

CMD ["python", "worker.py"]
