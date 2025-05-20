import pika
import json
import os
from sqlalchemy.orm import sessionmaker
from api.database.database import engine
from api.models.cv_model import CVRequest, Base
from api.config import settings

# Inicializar DB (asegura que las tablas existan)
Base.metadata.create_all(bind=engine)

# Crear sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def process_cv_message(body: bytes):
    """
    Lógica de procesamiento de CV:
    - Parsear el archivo (a implementar con Tika/pdfplumber).
    - Luego actualizar estado en la BD.
    """
    data = json.loads(body)
    cv_id = data.get("cv_id")
    print(f"[ParserWorker] Procesando CV ID: {cv_id}")

    db = SessionLocal()
    try:
        cv_req = db.query(CVRequest).filter(CVRequest.cv_id == cv_id).first()
        if not cv_req:
            print(f"[ParserWorker] No se encontró CV con id {cv_id}")
            return

        # Aquí iría la lógica real de extracción de texto...
        # texto = parse_pdf(cv_req.filename)
        # guardarlo en una tabla o en un archivo, etc.

        # Actualizar estado
        cv_req.estado = "parseado"
        db.commit()
        print(f"[ParserWorker] CV {cv_id} marcado como 'parseado'")
    except Exception as e:
        db.rollback()
        print(f"[ParserWorker] Error al procesar CV {cv_id}: {e}")
    finally:
        db.close()

def callback(ch, method, properties, body):
    print(f"[ParserWorker] Mensaje recibido: {body}")
    process_cv_message(body)
    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    # Conexión a RabbitMQ
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=settings.RABBITMQ_HOST)
    )
    channel = connection.channel()
    channel.queue_declare(queue=settings.PARSER_QUEUE, durable=True)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(
        queue=settings.PARSER_QUEUE,
        on_message_callback=callback
    )

    print("[ParserWorker] Esperando mensajes en 'parser_queue'... CTRL+C para salir")
    channel.start_consuming()

if __name__ == "__main__":
    main()
