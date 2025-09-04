import json
import uuid
from typing import Dict

import pika

from config import Config
from models import SessionLocal, Order


class OrderProducer:
    """
    Класс для отправки сообщений в RabbitMQ.
    Отвечает за создание заказов и отправку их в очередь на обработку.
    Также реализует RPC для запросов статуса заказов.
    """
    def __init__(self, session = SessionLocal()):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=Config.RABBITMQ_HOST,
                port=Config.RABBITMQ_PORT,
                credentials=pika.PlainCredentials(Config.RABBITMQ_USER, Config.RABBITMQ_PASS)
            )
        )
        self.channel = self.connection.channel()
        self.session = session

        # Объявляем очередь для заказов
        self.channel.queue_declare(
            queue=Config.ORDER_QUEUE,
            durable=True  # Сохраняет очередь при перезапуске RabbitMQ
        )
        # Объявляем очередь для статусов (RPC)
        self.channel.queue_declare(queue=Config.STATUS_QUEUE, durable=True)

    def create_order(self, order_data: Dict) -> Dict:
        """
        Создает заказ в базе данных и отправляет сообщение в очередь на обработку.
        """
        try:
            # Сохраняем заказ в базу
            order = Order(**order_data)
            self.session.add(order)
            self.session.commit()
            self.session.refresh(order)

            # Формируем сообщение для очереди
            message = {
                'order_id': order.id,
                'action': 'process_order'
            }
            # Отправляем в очередь
            self.channel.basic_publish(
                exchange='',                          # Используем default exchange
                routing_key=Config.ORDER_QUEUE,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,                  # Сохраняет сообщение при перезапуске RabbitMQ
                    correlation_id=str(uuid.uuid4())  # Уникальный ID для отслеживания
                )
            )
            print(f"Заказ № {order.id} отправлен в очередь...")
            return order.to_dict()
        except Exception as e:
            self.session.rollback()
            raise e
        finally:
            self.session.close()

    def get_order_status(self, order_id: int) -> Dict:
        """
        Реализация RPC (Remote Procedure Call) для запроса статуса заказа.
        Отправляет запрос и ожидает ответа через callback очередь.
        """
        # Создаем временную очередь для ответа
        result = self.channel.queue_declare(queue='', exclusive=True)
        callback_queue = result.method.queue
        
        response = None
        correlation_id = str(uuid.uuid4())  # Уникальный ID для сопоставления запроса-ответа
        
        def on_response(ch, method, props, body):
            """Callback функция для обработки ответа"""
            if correlation_id == props.correlation_id:
                nonlocal response
                response = json.loads(body)

        # Подписываемся на временную очередь для получения ответа
        self.channel.basic_consume(
            queue=callback_queue,
            on_message_callback=on_response,
            auto_ack=True
        )

        # Отправляем запрос статуса
        self.channel.basic_publish(
            exchange='',
            routing_key=Config.STATUS_QUEUE,
            properties=pika.BasicProperties(
                reply_to=callback_queue,        # Очередь для ответа
                correlation_id=correlation_id,  # ID для сопоставления
            ),
            body=json.dumps({'order_id': order_id})
        )

        # Ожидаем ответа (неблокирующее ожидание)
        while response is None:
            self.connection.process_data_events()
        return response

    def close(self):
        self.connection.close()
