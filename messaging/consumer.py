import json
from messaging.rabbitmq_connection import get_connection
from remediation_engine.remediator import handle_drift

def start_consumer():
    connection = get_connection()
    channel = connection.channel()

    channel.queue_declare(queue="drift_queue", durable=True)

    def callback(ch, method, properties, body):
        drift = json.loads(body)
        print("Drift received from queue")
        handle_drift(drift)

    channel.basic_consume(
        queue="drift_queue",
        on_message_callback=callback,
        auto_ack=True
    )

    print("Waiting for drifts...")
    channel.start_consuming()