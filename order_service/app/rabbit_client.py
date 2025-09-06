import aio_pika
import json

from app.models import Order


class RabbitMQClient:
    def __init__(self):
        self.connection = None
        self.channel = None

    async def connect(self, rabbitmq_url: str):
        self.connection = await aio_pika.connect_robust(rabbitmq_url)
        self.channel = await self.connection.channel()
        await self.channel.declare_queue("orders_queue", durable=True)

    async def publish_order_created(self, order: Order):
        if self.channel is None:
            raise Exception("Не удалось подключиться к каналу RabbitMQ...")

        message_body = json.dumps({
            "order_id": order.id,
            "product_name": order.product_name,
            "quantity": order.quantity,
            "customer_name": order.customer_name,
            "customer_email": order.customer_email,
            "status": order.status.value,
            "created_at": order.created_at.isoformat()
        })

        message = aio_pika.Message(
            body=message_body.encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT
        )
        await self.channel.default_exchange.publish(message, routing_key="orders_queue")

    async def close(self):
        if self.connection:
            await self.connection.close()
