import pika
import json
from sqlalchemy.orm import sessionmaker
from api.database.database import engine
from api.models.cv_model import CVRequest, Base
from api.config import settings

# Asegurar tablas
Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def extract_keywords_from_text(text: str):
    """
    Aquí iría tu lógica real (distilbert, TF-IDF, etc.).
    De momento simularemos devolviendo las primeras palabras únicas.
    """
    palabras = text.replace('\n', ' ').split()
    unique = []
    for w in palabras:
        w_clean = w.strip('.,()').lower()
        if w_clean and w_clean not in unique:
            unique.append(w_clean)
        if len(unique) >= 10:
            break
    return unique

def process_keyword_message(body: bytes):
    data = json.loads(body)
    cv_id = data.get("cv_id")
    # Normalmente recibirías también el texto ya parseado.
    # Para demo simulamos cargando un texto dummy:
    texto = "Este es un texto de ejemplo para simular extracción de palabras clave del CV."

    print(f"[KeywordWorker] Extrayendo keywords para CV ID: {cv_id}")
    keywords_list = extract_keywords_from_text(texto)

    db = SessionLocal()
    try:
        cv_req = db.query(CVRequest).filter(CVRequest.cv_id == cv_id).first()
        if not cv_req:
            print(f"[KeywordWorker] CV no encontrado: {cv_id}")
            return
        # Almacenar las keywords y actualizar estado
        cv_req.keywords = json.dumps(keywords_list, ensure_ascii=False)
        cv_req.estado = "keywords_extraidos"
        db.commit()
        print(f"[KeywordWorker] Keywords ({keywords_list}) guardadas para {cv_id}")
        # Reencolar para feedback
        channel, conn = pika.BlockingConnection(
            pika.ConnectionParameters(host=settings.RABBITMQ_HOST)
        ), None
        try:
            channel = channel.channel()
            channel.queue_declare(queue=settings.FEEDBACK_QUEUE, durable=True)
            payload = {"cv_id": cv_id, "keywords": keywords_list}
            channel.basic_publish(
                exchange='',
                routing_key=settings.FEEDBACK_QUEUE,
                body=json.dumps(payload),
                properties=pika.BasicProperties(delivery_mode=2)
            )
        finally:
            if channel and channel.connection:
                channel.connection.close()
    except Exception as e:
        db.rollback()
        print(f"[KeywordWorker] Error al guardar keywords: {e}")
    finally:
        db.close()

def callback(ch, method, properties, body):
    print(f"[KeywordWorker] Mensaje recibido: {body}")
    process_keyword_message(body)
    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=settings.RABBITMQ_HOST)
    )
    channel = connection.channel()
    channel.queue_declare(queue=settings.KEYWORD_QUEUE, durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(
        queue=settings.KEYWORD_QUEUE,
        on_message_callback=callback
    )
    print("[KeywordWorker] Esperando mensajes en 'keyword_queue'... CTRL+C para salir")
    channel.start_consuming()

if __name__ == "__main__":
    main()
