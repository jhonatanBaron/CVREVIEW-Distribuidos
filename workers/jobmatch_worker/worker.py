import pika
import json
from sqlalchemy.orm import sessionmaker
from api.database.database import engine
from api.models.cv_model import CVRequest, Base
from api.config import settings

# Aseguramos que las tablas existan
Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def find_job_matches(keywords: list):
    """
    Simula consulta a APIs externas de empleo.
    """
    matches = []
    for i, kw in enumerate(keywords, start=1):
        matches.append({
            "job_id": f"job_{i}",
            "titulo": f"Especialista en {kw.capitalize()}",
            "empresa": f"Empresa {i}",
            "enlace": f"https://jobs.example.com/{i}",
            "score": round(100 - i*5, 1)
        })
    return matches

def process_jobmatch_message(body: bytes):
    data = json.loads(body)
    cv_id = data.get("cv_id")
    keywords = data.get("keywords", [])

    print(f"[JobMatchWorker] Buscando vacantes para CV ID: {cv_id}")

    job_list = find_job_matches(keywords)

    db = SessionLocal()
    try:
        cv_req = db.query(CVRequest).filter(CVRequest.cv_id == cv_id).first()
        if not cv_req:
            print(f"[JobMatchWorker] CV no encontrado: {cv_id}")
            return

        cv_req.job_matches = json.dumps(job_list, ensure_ascii=False)
        cv_req.estado = "jobmatch_completado"
        db.commit()
        print(f"[JobMatchWorker] {len(job_list)} vacantes guardadas para {cv_id}")

        # Encolamos notificación
        conn = pika.BlockingConnection(
            pika.ConnectionParameters(host=settings.RABBITMQ_HOST)
        )
        ch = conn.channel()
        ch.queue_declare(queue=settings.NOTIFICATION_QUEUE, durable=True)
        ch.basic_publish(
            exchange='',
            routing_key=settings.NOTIFICATION_QUEUE,
            body=json.dumps({"cv_id": cv_id}),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        conn.close()

    except Exception as e:
        db.rollback()
        print(f"[JobMatchWorker] Error: {e}")
    finally:
        db.close()

def callback(ch, method, properties, body):
    print(f"[JobMatchWorker] Mensaje recibido: {body}")
    process_jobmatch_message(body)
    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=settings.RABBITMQ_HOST)
    )
    channel = connection.channel()
    channel.queue_declare(queue=settings.JOBMATCH_QUEUE, durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(
        queue=settings.JOBMATCH_QUEUE,
        on_message_callback=callback
    )
    print("[JobMatchWorker] Esperando en 'jobmatch_queue'... CTRL+C para salir")
    channel.start_consuming()

if __name__ == "__main__":
    main()
