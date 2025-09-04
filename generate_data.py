from faker import Faker
from producer import OrderProducer
import random

fake = Faker()


def generate_orders(num_orders: int = 100):
    """
    Генерирует тестовые заказы для наполнения системы данными.
    Для демонстрации и тестирования.
    """
    producer = OrderProducer()
    products = [
        'Laptop', 'Phone', 'Tablet', 'Headphones', 'Monitor',
        'Keyboard', 'Mouse', 'Printer', 'Camera', 'Speaker',
    ]

    for i in range(num_orders):
        order_data = {
            'customer_name': fake.name(),
            'product': random.choice(products),
            'quantity': random.randint(1, 5),
            'amount': round(random.uniform(50, 2000), 2)
        }

        try:
            producer.create_order(order_data)
            print(f"Generated order {i+1}/{num_orders}")
        except Exception as e:
            print(f"Error generating order: {e}")

    producer.close()


if __name__ == '__main__':
    generate_orders()
