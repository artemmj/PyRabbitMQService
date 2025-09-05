import pika

from config import connection_params


# Установка соединения
connection = pika.BlockingConnection(connection_params)

# Создание канала
channel = connection.channel()

# Имя очереди
queue_name = 'hello'

# Функция, которая будет вызвана при получении сообщения
def callback(ch, method, properties, body):
    print(f"Received: '{body}'")

# Подписка на очередь и установка обработчика сообщений
channel.basic_consume(
    queue=queue_name,
    on_message_callback=callback,
    auto_ack=True  # Автоматическое подтверждение обработки сообщений
)

print('Жду сообщения из очереди. Для выхода нажми Ctrl+C...')
channel.start_consuming()
