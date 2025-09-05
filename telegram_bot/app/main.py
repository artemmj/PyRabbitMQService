import os
import asyncio

from dotenv import load_dotenv

from app.consumer import OrderConsumer
from app.tg_client import TelegramClient

load_dotenv()


async def main():
    telegram_client = TelegramClient(
        bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ''),
        chat_id=os.getenv("TELEGRAM_CHAT_ID", '')
    )
    consumer = OrderConsumer(telegram_client)
    rabbitmq_url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
    await consumer.connect(rabbitmq_url)

    print("Телеграм-бот успешно установил соединение с RabbitMQ...")
    print("Слушаю сообщения о новых заказах...")

    try:
        await consumer.consume_orders()
    except KeyboardInterrupt:
        print("Выключение...")
    except Exception as e:
        print(f"Ошибка: {e}")


if __name__ == "__main__":
    asyncio.run(main())
