
# api/workers/parser_worker.py
import pika
import json
import time
import os
from pdfminer.high_level import extract_text
import docx2txt

# Esperar a que RabbitMQ esté disponible
while True:
    try:
        rabbit_host = os.getenv("RABBITMQ_HOST", "rabbitmq")
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=rabbit_host)
        )
        print(f" Conectado a RabbitMQ en {rabbit_host}")
        break
    except Exception as e:
        print("⏳ Esperando RabbitMQ...", e)
        time.sleep(5)

channel = connection.channel()
# Declaración de colas necesarias
channel.queue_declare(queue="parser_queue", durable=True)
channel.queue_declare(queue="keyword_queue", durable=True)
print(" Colas parser_queue y keyword_queue declaradas")

# Función para extraer texto de PDF o DOCX
def extract_text_from_file(filepath: str) -> str:
    if filepath.lower().endswith(".pdf"):
        return extract_text(filepath)
    elif filepath.lower().endswith(".docx"):
        return docx2txt.process(filepath)
    else:
        raise ValueError(f"Formato no soportado: {filepath}")

# Callback para procesar mensajes de parser_queue
def callback(ch, method, properties, body):
    print(" Mensaje recibido en parser_queue:", body)
    data = json.loads(body)
    cv_id = data.get("cv_id")
    filename = data.get("filename")
    filepath = f"/files/{filename}"

    print(f"🔍 Procesando archivo: {filepath} (CV ID: {cv_id})")
    try:
        text = extract_text_from_file(filepath)
        message_out = {"cv_id": cv_id, "text": text}

        channel.basic_publish(
            exchange="",
            routing_key="keyword_queue",
            body=json.dumps(message_out),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        print(f"✅ Texto enviado a keyword_queue (CV ID: {cv_id})")
    except Exception as e:
        print(f"❌ Error al procesar el archivo: {e}")

    ch.basic_ack(delivery_tag=method.delivery_tag)

# Configuración de consumo
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue="parser_queue", on_message_callback=callback)

print("▶️ ParserWorker listo y a la espera de mensajes en parser_queue...")
channel.start_consuming()

