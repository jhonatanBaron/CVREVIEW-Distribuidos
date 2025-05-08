import pika, json, time
import psycopg2

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


def callback(ch, method, properties, body):
    data = json.loads(body)
    cv_id = data["cv_id"]
    print(f"Procesando CV {cv_id}...")

    # Simula tiempo de procesamiento
    time.sleep(3)

    # Actualizar estado en PostgreSQL
    conn = psycopg2.connect(
        dbname="cvflow", user="cvuser", password="cvpass", host="postgres"
    )
    cur = conn.cursor()
    cur.execute("UPDATE cvs SET status='procesado' WHERE id=%s", (cv_id,))
    conn.commit()
    cur.close()
    conn.close()
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
channel = connection.channel()
channel.queue_declare(queue="parser_queue", durable=True)
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue="parser_queue", on_message_callback=callback)
print("Esperando mensajes...")
channel.start_consuming()
