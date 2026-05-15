import json
import pika
from messaging.rabbitmq_connection import get_connection


def send_to_queue(drift_record):
    print("Sending drift to queue...")
    send_drift(drift_record)

def send_drift(drift):
    connection = get_connection()
    channel = connection.channel()

    channel.queue_declare(queue="drift_queue", durable=True)

    channel.basic_publish(
        exchange="",
        routing_key="drift_queue",
        body=json.dumps(drift),
        properties=pika.BasicProperties(
        delivery_mode=2 
        )
    )

    print("Drift sent to queue")
    connection.close()