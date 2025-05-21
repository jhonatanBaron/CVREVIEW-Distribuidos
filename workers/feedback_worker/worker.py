import pika
import json
from sqlalchemy.orm import sessionmaker
from api.database.database import engine
from api.models.cv_model import CVRequest, Base
from api.config import settings

# Asegura que las tablas existan
Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def generate_feedback(text: str, keywords: list):
    """
    Aquí conectarías con GPT-4 u otro LLM.
    Para demo, devolvemos un feedback simulado.
    """
    sugerencias = [
        "Mejora la sección de experiencia con más verbos de acción.",
        "Añade logros cuantificables en cada puesto.",
        "Revisa la ortografía y consistencia de formato."
    ]
    # Simula una puntuación de 0 a 10
    puntuacion = round(5 + len(keywords)*0.5, 1)
    return sugerencias, puntuacion

def process_feedback_message(body: bytes):
    data = json.loads(body)
    cv_id = data.get("cv_id")
    keywords = data.get("keywords", [])

    print(f"[FeedbackWorker] Generando feedback para CV ID: {cv_id}")

    # En la práctica extraerías texto real del CV; aquí demo:
    texto = "Texto completo del CV..."  

    sugerencias, puntuacion = generate_feedback(texto, keywords)

    db = SessionLocal()
    try:
        cv_req = db.query(CVRequest).filter(CVRequest.cv_id == cv_id).first()
        if not cv_req:
            print(f"[FeedbackWorker] CV no encontrado: {cv_id}")
            return

        # Guardar feedback y score
        cv_req.feedback = json.dumps(sugerencias, ensure_ascii=False)
        cv_req.score = puntuacion
        cv_req.estado = "feedback_generado"
        db.commit()
        print(f"[FeedbackWorker] Feedback guardado para {cv_id}: score={puntuacion}")

        # Reencolar para job matching
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=settings.RABBITMQ_HOST)
        )
        channel = connection.channel()
        channel.queue_declare(queue=settings.JOBMATCH_QUEUE, durable=True)
        payload = {"cv_id": cv_id, "keywords": keywords}
        channel.basic_publish(
            exchange='',
            routing_key=settings.JOBMATCH_QUEUE,
            body=json.dumps(payload),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        connection.close()
    except Exception as e:
        db.rollback()
        print(f"[FeedbackWorker] Error al guardar feedback: {e}")
    finally:
        db.close()

def callback(ch, method, properties, body):
    print(f"[FeedbackWorker] Mensaje recibido: {body}")
    process_feedback_message(body)
    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=settings.RABBITMQ_HOST)
    )
    channel = connection.channel()
    channel.queue_declare(queue=settings.FEEDBACK_QUEUE, durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(
        queue=settings.FEEDBACK_QUEUE,
        on_message_callback=callback
    )
    print("[FeedbackWorker] Esperando mensajes en 'feedback_queue'... CTRL+C para salir")
    channel.start_consuming()

if __name__ == "__main__":
    main()
