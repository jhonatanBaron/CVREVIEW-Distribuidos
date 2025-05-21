# api/Dockerfile
FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copiar e instalar dependencias
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . /app

# Arrancar Uvicorn apuntando al módulo api.main
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]