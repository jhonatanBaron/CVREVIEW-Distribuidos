FROM python:alpine

WORKDIR /app

COPY parser_worker.py .

RUN pip install pika psycopg2-binary

CMD ["python", "parser_worker.py"]
