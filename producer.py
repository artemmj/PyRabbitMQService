import pika

from config import connection_params


# Установка соединения
connection = pika.BlockingConnection(connection_params)
# Создание канала
channel = connection.channel()
# Имя очереди
queue_name = 'orders_queue'
# Создание очереди (если не существует)
channel.queue_declare(queue='orders_queue', durable=True)

# Отправка сообщения
message = 'Hello, RabbitMQ!'
channel.basic_publish(
    exchange='',
    routing_key=queue_name,
    body=message
)

print(f"Отправлено в очередь: '{message}'")

print(f'Отправляю сообщения в рамках транзакции...')
channel.tx_select()
channel.basic_publish(exchange='', routing_key=queue_name, body='Transaction Message #1')
channel.basic_publish(exchange='', routing_key=queue_name, body='Transaction Message #2')
channel.tx_commit()
print(f'Завершаю транзакцию...')

# Закрытие соединения
connection.close()
