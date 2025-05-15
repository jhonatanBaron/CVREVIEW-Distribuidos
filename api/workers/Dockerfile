FROM python:3.11-slim

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

COPY parser_worker.py .

RUN pip install --no-cache-dir pdfminer.six docx2txt pika psycopg2-binary spacy
RUN python -m spacy download en_core_web_sm

CMD ["python", "parser_worker.py"]
