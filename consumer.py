import json
import time

import pika
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic

from config import Config
from models import SessionLocal, Order, OrderStatus


class OrderConsumer:
    """
    Класс для потребления сообщений из RabbitMQ.
    Обрабатывает заказы и отвечает на RPC запросы статуса.
    Поддерживает многопоточную работу нескольких воркеров.
    """
    def __init__(self, worker_id: int):
        """
        Инициализация консьюмера с указанием ID воркера.
        """
        self.worker_id = worker_id
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=Config.RABBITMQ_HOST,
                port=Config.RABBITMQ_PORT,
                credentials=pika.PlainCredentials(Config.RABBITMQ_USER, Config.RABBITMQ_PASS)
            )
        )
        self.channel = self.connection.channel()

        # Объявляем очереди (обеспечиваем их существование)
        self.channel.queue_declare(queue=Config.ORDER_QUEUE, durable=True)
        self.channel.queue_declare(queue=Config.STATUS_QUEUE, durable=True)

        # Настраиваем fair dispatch - каждый воркер получает по одному сообщению
        self.channel.basic_qos(prefetch_count=1)

        # Подписываемся на очередь заказов для обработки
        self.channel.basic_consume(
            queue=Config.ORDER_QUEUE,
            on_message_callback=self.process_order
        )

        # Подписываемся на очередь статусов для RPC ответов
        self.channel.basic_consume(
            queue=Config.STATUS_QUEUE,
            on_message_callback=self.handle_status_request
        )

    def process_order(self, ch: BlockingChannel, method, properties, body):
        """
        Обрабатывает сообщение о новом заказе из очереди.
        Обновляет статус заказа и имитирует обработку.
        
        Args:
            ch: Канал RabbitMQ
            method: Метод доставки сообщения
            properties: Свойства сообщения
            body: Тело сообщения (JSON с order_id)
        """
        try:
            message = json.loads(body)
            order_id = message['order_id']

            session = SessionLocal()
            order = session.query(Order).get(order_id)

            if not order:
                print(f"Order {order_id} not found")
                ch.basic_ack(delivery_tag=method.delivery_tag)  # Подтверждаем обработку
                return

            # Обновляем статус заказа на "в обработке"
            order.status = OrderStatus.PROCESSING
            session.commit()

            print(f"Worker {self.worker_id} processing order {order_id}")

            # Имитация времени обработки заказа
            time.sleep(Config.PROCESSING_TIME)

            # Симулируем случайные ошибки для тестирования механизма повторов
            if order.retries < Config.MAX_RETRIES and order_id % 10 == 0:
                order.retries += 1
                session.commit()
                raise Exception("Simulated processing error")

            # Успешная обработка заказа
            order.status = OrderStatus.COMPLETED
            session.commit()

            print(f"Worker {self.worker_id} completed order {order_id}")
            ch.basic_ack(delivery_tag=method.delivery_tag)  # Подтверждаем успешную обработку

        except Exception as e:
            print(f"Error processing order {order_id}: {e}")
            session.rollback()

            # Повторная отправка в очередь при ошибке (если есть попытки)
            if order and order.retries < Config.MAX_RETRIES:
                order.retries += 1
                session.commit()
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)  # Возврат в очередь
            else:
                # Если попытки исчерпаны - отмечаем как failed
                if order:
                    order.status = OrderStatus.FAILED
                    session.commit()
                ch.basic_ack(delivery_tag=method.delivery_tag)  # Подтверждаем окончательную обработку
        finally:
            if 'session' in locals():
                session.close()

    def handle_status_request(self, ch: BlockingChannel, method, properties, body):
        """
        Обрабатывает RPC запросы статуса заказа.
        Отправляет ответ с текущим статусом заказа.

        Args:
            ch: Канал RabbitMQ
            method: Метод доставки сообщения
            properties: Свойства сообщения (включая reply_to и correlation_id)
            body: Тело сообщения (JSON с order_id)
        """
        try:
            message = json.loads(body)
            order_id = message['order_id']

            session = SessionLocal()
            order = session.query(Order).get(order_id)

            response = {'status': 'not_found'}
            if order:
                response = {
                    'status': order.status.value,
                    'order': order.to_dict()
                }

            # Отправляем ответ через RPC механизм
            ch.basic_publish(
                exchange='',
                routing_key=properties.reply_to,  # Очередь указанная в запросе
                properties=pika.BasicProperties(
                    correlation_id=properties.correlation_id  # Сохраняем correlation_id
                ),
                body=json.dumps(response)
            )

            ch.basic_ack(delivery_tag=method.delivery_tag)  # Подтверждаем обработку запроса

        except Exception as e:
            print(f"Error handling status request: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)  # Не возвращаем в очередь
        finally:
            session.close()

    def start_consuming(self):
        """Запускает бесконечный цикл потребления сообщений"""
        print(f"Worker {self.worker_id} started consuming...")
        self.channel.start_consuming()

    def close(self):
        """Закрывает соединение с RabbitMQ"""
        self.connection.close()
