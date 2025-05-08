import pika
import os
import json

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")

def publish_to_parser_queue(message: dict):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST)
    )
    channel = connection.channel()
    channel.queue_declare(queue="parser_queue", durable=True)
    channel.basic_publish(
        exchange="",
        routing_key="parser_queue",
        body=json.dumps(message),
        properties=pika.BasicProperties(delivery_mode=2)
    )
    connection.close()
