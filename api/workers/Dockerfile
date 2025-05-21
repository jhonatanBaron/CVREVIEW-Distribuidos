FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    libpq-dev \
    libffi-dev \
    musl-dev \
    libxml2-dev \
    libxslt-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install spaCy model
RUN python -m spacy download en_core_web_sm

# Copy worker files to specific directory
COPY api/workers/*.py .

# Create a startup script
RUN echo '#!/bin/bash\npython /app/$WORKER_TYPE"_worker.py"' > /app/start.sh && \
    chmod +x /app/start.sh

CMD ["/app/start.sh"]