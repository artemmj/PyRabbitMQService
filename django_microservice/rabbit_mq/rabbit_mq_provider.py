import json
import logging
from typing import Dict

import pika

logger = logging.getLogger('django')


def publish(q_name: str, body: Dict):
    connection_params = pika.ConnectionParameters()
    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel(1)
    queue_name = q_name
    channel.queue_declare(queue=queue_name)

    channel.basic_publish(
        exchange='',
        routing_key=queue_name,
        body=json.dumps(body)
    )
    logger.info(f"\r\nСообщение успешно отправлено в RabbitMQ ({body})\r\n")
    connection.close()
