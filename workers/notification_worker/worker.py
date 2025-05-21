import pika
import json
import os
import smtplib
from email.message import EmailMessage
from sqlalchemy.orm import sessionmaker
from api.database.database import engine
from api.models.cv_model import CVRequest, Base
from api.config import settings

# Asegurarnos de que la tabla existe
Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def send_email(to_email: str, subject: str, body: str):
    """
    Envía un email usando SMTP. 
    Aquí está configurado de forma muy básica; ajusta con credenciales reales.
    """
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = "no-reply@cvflow.local"
    msg["To"] = to_email
    msg.set_content(body)

    # SMTP local o externo (ajusta host/puerto)
    
    host = os.getenv("SMTP_HOST", "localhost")
    port = int(os.getenv("SMTP_PORT", 1025))
    with smtplib.SMTP(host, port) as server:
        server.send_message(msg)
        print(f"[NotificationWorker] Email enviado a {to_email}")

def process_notification_message(body: bytes):
    data = json.loads(body)
    cv_id = data.get("cv_id")
    print(f"[NotificationWorker] Procesando notificación para CV ID: {cv_id}")

    db = SessionLocal()
    try:
        cv_req = db.query(CVRequest).filter(CVRequest.cv_id == cv_id).first()
        if not cv_req:
            print(f"[NotificationWorker] CV no encontrado: {cv_id}")
            return

        # Componer cuerpo de notificación
        subject = f"Tu informe CVFlow está listo (ID: {cv_id})"
        body = (
            f"Hola {cv_req.nombre},\n\n"
            f"Tu CV (ID: {cv_id}) ha sido procesado con éxito.\n\n"
            f"Estado final: {cv_req.estado}\n"
            f"Puntuación: {cv_req.score}\n"
            f"Vacantes recomendadas: {len(json.loads(cv_req.job_matches) or [])}\n\n"
            "¡Gracias por usar CVFlow!"
        )
        # Enviar correo
        send_email(cv_req.email, subject, body)

        # Actualizar estado en DB
        cv_req.estado = "notificado"
        db.commit()
        print(f"[NotificationWorker] Estado 'notificado' guardado en BD para {cv_id}")

    except Exception as e:
        db.rollback()
        print(f"[NotificationWorker] Error al enviar notificación: {e}")
    finally:
        db.close()

def callback(ch, method, properties, body):
    print(f"[NotificationWorker] Mensaje recibido: {body}")
    process_notification_message(body)
    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=settings.RABBITMQ_HOST)
    )
    channel = connection.channel()
    # Consumimos de la cola de notificaciones
    channel.queue_declare(queue=settings.NOTIFICATION_QUEUE, durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(
        queue=settings.NOTIFICATION_QUEUE,
        on_message_callback=callback
    )
    print("[NotificationWorker] Esperando mensajes en 'notification_queue'... CTRL+C para salir")
    channel.start_consuming()

if __name__ == "__main__":
    main()
