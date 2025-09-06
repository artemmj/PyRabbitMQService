import json

import aio_pika

from tg_client import TelegramClient


class OrderConsumer:
    def __init__(self, telegram_client: TelegramClient):
        self.telegram_client = telegram_client
        self.connection = None
        self.channel = None

    async def connect(self, rabbitmq_url: str):
        self.connection = await aio_pika.connect_robust(rabbitmq_url)
        self.channel = await self.connection.channel()
        await self.channel.set_qos(prefetch_count=1)

    async def consume_orders(self):
        queue = await self.channel.declare_queue("orders_queue", durable=True)

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    try:
                        order_data = json.loads(message.body.decode())
                        await self.process_order(order_data)
                    except Exception as e:
                        print(f"Error processing message: {e}")

    async def process_order(self, order_data: dict):
        message = (
            "Новый заказ!\n\n"
            f"ID: {order_data['order_id']}\n"
            f"Товар: {order_data['product_name']}\n"
            f"Количество: {order_data['quantity']}\n"
            f"Клиент: {order_data['customer_name']}\n"
            f"Email: {order_data['customer_email']}\n"
            f"Статус: {order_data['status']}\n"
            f"Создан: {order_data['created_at']}"
        )
        print(message)
        await self.telegram_client.send_message(message)

    async def close(self):
        await self.connection.close()
