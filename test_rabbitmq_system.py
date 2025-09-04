import os
import time
import pytest
from threading import Thread

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from producer import OrderProducer
from consumer import OrderConsumer
from models import Base, Order, OrderStatus

# Тестовая конфигурация
TEST_DB_URL = 'sqlite:///orders_test.db'


@pytest.fixture
def test_session():
    """Создает тестовую сессию БД"""
    engine = create_engine(TEST_DB_URL)
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()

    yield session

    # Очищаем БД после каждого теста
    # for table in reversed(Base.metadata.sorted_tables):
    #     session.execute(table.delete())
    # session.commit()
    # session.close()


def test_order_creation_and_processing(test_session):
    """Тест создания заказов и их обработки"""
    producer = OrderProducer(test_session)
    # Создаем тестовые заказы
    for i in range(1, 6):
        order_data = {
            'customer_name': f'Тестовый клиент {i}',
            'product': f'Тестовый продукт {i}',
            'quantity': i + 2,
            'amount': i * 10.4
        }
        order = producer.create_order(order_data)
        assert order['status'] == 'pending'

    # Запускаем воркер в отдельном потоке
    consumer = OrderConsumer(1, test_session)

    def consume_with_timeout():
        try:
            consumer.connection.process_data_events(time_limit=1)
        except:
            pass

    thread = Thread(target=consume_with_timeout)
    thread.start()
    thread.join(timeout=10)

    # Проверяем, что заказ обработан
    processed_order = test_session.query(Order).all()
    for order in processed_order:
        assert order.status == OrderStatus.COMPLETED

    # test_session.delete(processed_order)
    # test_session.commit()

    producer.close()
    consumer.close()


# def test_message_persistence(test_session):
#     """Тест сохранения сообщений при перезапуске"""
#     producer = OrderProducer(test_session)

#     # Создаем несколько заказов
#     for i in range(1, 6):
#         order_data = {
#             'customer_name': f'Клиент {i}',
#             'product': f'Продукт {i}',
#             'quantity': i,
#             'amount': i * 10.0
#         }
#         producer.create_order(order_data)

#     # Закрываем producer (имитируем перезапуск)
#     producer.close()

#     # Запускаем нового consumer
#     consumer = OrderConsumer(i, test_session)
#     # Обрабатываем сообщения
#     thread = Thread(target=consumer.connection.process_data_events, args=(10,))
#     thread.start()
#     thread.join(timeout=15)

#     # Проверяем, что все заказы обработаны
#     orders = test_session.query(Order).all()
#     assert len(orders) == 5
#     for order in orders:
#         assert order.status == OrderStatus.COMPLETED

#     consumer.close()


# def test_load_balancing():
#     """Тест распределения нагрузки между воркерами"""
#     producers = [OrderProducer() for _ in range(3)]
#     consumers = [OrderConsumer(i) for i in range(1, 4)]
    
#     # Создаем много заказов
#     num_orders = 50
#     for i in range(num_orders):
#         producer = producers[i % len(producers)]
#         order_data = {
#             'customer_name': f'Load Customer {i}',
#             'product': f'Load Product {i}',
#             'quantity': (i % 5) + 1,
#             'amount': ((i % 5) + 1) * 10.0
#         }
#         producer.create_order(order_data)
    
#     # Запускаем воркеров в отдельных потоках
#     threads = []
#     for consumer in consumers:
#         thread = Thread(target=lambda c: c.connection.process_data_events(time_limit=15), args=(consumer,))
#         threads.append(thread)
#         thread.start()
    
#     # Ждем завершения
#     for thread in threads:
#         thread.join(timeout=20)
    
#     # Проверяем распределение
#     session = SessionLocal()
#     orders = session.query(Order).all()
#     assert len(orders) == num_orders
    
#     for producer in producers:
#         producer.close()
#     for consumer in consumers:
#         consumer.close()

# def test_error_handling_and_retries(test_session):
#     """Тест обработки ошибок и повторных попыток"""
#     producer = OrderProducer()
    
#     # Создаем заказ, который будет вызывать ошибку (id кратный 10)
#     order_data = {
#         'customer_name': 'Error Customer',
#         'product': 'Error Product',
#         'quantity': 1,
#         'amount': 100.0
#     }
    
#     order = producer.create_order(order_data)
    
#     # Меняем ID на кратный 10 для симуляции ошибки
#     session = SessionLocal()
#     error_order = session.query(Order).get(order['id'])
#     error_order.id = 100  # Делаем ID кратным 10
#     session.commit()
    
#     # Обрабатываем
#     consumer = OrderConsumer(1)
    
#     def process_with_retries():
#         try:
#             consumer.connection.process_data_events(time_limit=10)
#         except:
#             pass
    
#     thread = Thread(target=process_with_retries)
#     thread.start()
#     thread.join(timeout=15)
    
#     # Проверяем, что были попытки повтора
#     final_order = session.query(Order).get(100)
#     assert final_order.retries > 0
#     assert final_order.status == OrderStatus.FAILED
    
#     producer.close()
#     consumer.close()

# def test_rpc_status_requests():
#     """Тест RPC запросов статуса"""
#     producer = OrderProducer()
    
#     # Создаем заказ
#     order_data = {
#         'customer_name': 'RPC Customer',
#         'product': 'RPC Product',
#         'quantity': 1,
#         'amount': 100.0
#     }
    
#     order = producer.create_order(order_data)
    
#     # Запрашиваем статус через RPC
#     status = producer.get_order_status(order['id'])
#     assert status['status'] == 'pending'
    
#     # Обрабатываем заказ
#     consumer = OrderConsumer(1)
#     consumer.connection.process_data_events(time_limit=5)
    
#     # Снова запрашиваем статус
#     status = producer.get_order_status(order['id'])
#     assert status['status'] == 'completed'
    
#     producer.close()
#     consumer.close()
