import pika


# Параметры подключения
connection_params = pika.ConnectionParameters(
    host='localhost',      # Замените на адрес вашего RabbitMQ сервера
    port=5672,             # Порт по умолчанию для RabbitMQ
    virtual_host='/',      # Виртуальный хост (обычно '/')
    credentials=pika.PlainCredentials(
        username='guest',  # Имя пользователя по умолчанию
        password='guest',  # Пароль по умолчанию
    )
)
