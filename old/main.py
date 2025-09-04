import sys

from rabbitmq_provider import RabbitMQProvider


def callback(ch, method, properties, body):
    print(f"(main) Получено сообщение: method: {method}\r\nproperties: {properties}\r\nbody: {body}\r\n")


def main():
    rabbitmq = RabbitMQProvider()
    print("(main) Соединение с RabbitMQ успешно установлено...")
    try:
        rabbitmq.consume(queue_name='test_queue', callback=callback)
    except Exception as e:
        print(f"(main) Ошибка при установке соединения с RabbitMQ: {e}")
        sys.exit(1)
    finally:
        rabbitmq.close()


if __name__ == "__main__":
    main()
