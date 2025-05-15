import pika
import json
import time
import os
from pdfminer.high_level import extract_text
import docx2txt

# Esperar que RabbitMQ esté listo
while True:
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
        break
    except Exception as e:
        print("Esperando RabbitMQ...", e)
        time.sleep(5)

channel = connection.channel()
channel.queue_declare(queue="parser_queue", durable=True)
channel.queue_declare(queue="keyword_queue", durable=True)  
channel.queue_declare(queue="analysis_queue", durable=True)


def extract_text_from_file(filepath: str) -> str:
    if filepath.endswith(".pdf"):
        return extract_text(filepath)
    elif filepath.endswith(".docx"):
        return docx2txt.process(filepath)
    else:
        raise ValueError("Formato de archivo no soportado")

def callback(ch, method, properties, body):
    data = json.loads(body)
    cv_id = data["cv_id"]
    filename = data["filename"]
    filepath = f"/files/{filename}"

    print(f"Procesando archivo: {filepath} (CV ID: {cv_id})")

    try:
        text = extract_text_from_file(filepath)

        message_out = {
            "cv_id": cv_id,
            "text": text
        }

        channel.basic_publish(
            exchange="",
            routing_key="keyword_queue",
            body=json.dumps(message_out),
            properties=pika.BasicProperties(delivery_mode=2)
        )

        print(f"Texto extraído y enviado a keyword_queue (CV ID: {cv_id})")

    except Exception as e:
        print(f"Error al procesar el archivo: {e}")

    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue="parser_queue", on_message_callback=callback)

print("ParserWorker en espera de mensajes en parser_queue...")
channel.start_consuming()
