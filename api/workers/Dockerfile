# api/workers/Dockerfile
FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential gcc libpq-dev libffi-dev musl-dev libxml2-dev libxslt-dev zlib1g-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar e instalar dependencias Python\COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Instalar modelo spaCy si lo usa alguno de los workers
RUN python -m spacy download en_core_web_sm

# Copiar todos los scripts de los workers al directorio de trabajo
COPY api/workers/*.py /app/

# Variable de entorno para indicar host de RabbitMQ
ENV RABBITMQ_HOST=rabbitmq

# Comando de arranque: ejecuta el worker según WORKER_TYPE, e.g., parser, keyword, cv_evaluator
CMD ["sh", "-c", "python /app/${WORKER_TYPE}_worker.py"]