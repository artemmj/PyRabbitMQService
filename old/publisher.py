from rabbitmq_provider import RabbitMQProvider


def publish_test_message():
    rabbitmq = RabbitMQProvider()
    try:
        rabbitmq.publish(queue_name='test_queue', message='test_message')
        print("(publish_test_message) Тестовое сообщение успешно доставлено.")
    except Exception as e:
        print(f"(publish_test_message) Ошибка при доставке тестового сообщения: {e}")
    finally:
        rabbitmq.close()


if __name__ == "__main__":
    publish_test_message()
