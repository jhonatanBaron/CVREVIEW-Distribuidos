import pika
import json
import os
import time
import spacy

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")

# Cargar modelo de spaCy
nlp = spacy.load("en_core_web_sm")

# Reintento de conexión a RabbitMQ
while True:
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
        break
    except Exception as e:
        print("Esperando RabbitMQ...", e)
        time.sleep(5)

channel = connection.channel()
channel.queue_declare(queue="keyword_queue", durable=True)
channel.queue_declare(queue="analysis_queue", durable=True)
channel.queue_declare(queue="analysis_queue", durable=True)


# Función para extraer palabras clave (sustantivos propios, organizaciones, etc.)
def extract_keywords(text: str):
    doc = nlp(text)
    keywords = set()

    for ent in doc.ents:
        if ent.label_ in ("PERSON", "ORG", "GPE", "NORP", "SKILL", "JOB_TITLE"):
            keywords.add(ent.text.strip())

    for token in doc:
        if token.pos_ in ("NOUN", "PROPN") and len(token.text.strip()) > 3:
            keywords.add(token.text.strip())

    return list(keywords)

# Callback de RabbitMQ
def callback(ch, method, properties, body):
    data = json.loads(body)
    cv_id = data["cv_id"]
    text = data["text"]

    print(f"Procesando palabras clave para CV ID: {cv_id}")

    try:
        keywords = extract_keywords(text)

        result = {
            "cv_id": cv_id,
            "keywords": keywords
        }

        channel.basic_publish(
            exchange="",
            routing_key="analysis_queue",
            body=json.dumps(result),
            properties=pika.BasicProperties(delivery_mode=2)
        )

        print(f"Palabras clave enviadas a analysis_queue (CV ID: {cv_id})")

    except Exception as e:
        print(f"Error procesando texto: {e}")

    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue="keyword_queue", on_message_callback=callback)

print("KeywordWorker escuchando keyword_queue...")
channel.start_consuming()
