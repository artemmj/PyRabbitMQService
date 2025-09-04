import os


class Config:
    """
    Класс конфигурации для централизованного управления настройками системы.
    Позволяет легко изменять параметры без модификации кода в других файлах.
    """
    
    # Настройки RabbitMQ - подключение к брокеру сообщений
    RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
    RABBITMQ_PORT = int(os.getenv('RABBITMQ_PORT', 5672))
    RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'guest')
    RABBITMQ_PASS = os.getenv('RABBITMQ_PASS', 'guest')
    
    # Очереди - имена очередей для различных типов сообщений
    ORDER_QUEUE = 'order_queue'        # Для обработки заказов
    STATUS_QUEUE = 'status_queue'      # Для запросов статуса (RPC)
    
    # Настройки базы данных - подключение к хранилищу заказов
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///orders.db')
    
    # Настройки воркеров - параметры обработки сообщений
    MAX_RETRIES = 3                    # Максимальное количество повторных попыток
    PROCESSING_TIME = .1               # Время обработки заказа в секундах (для симуляции)
