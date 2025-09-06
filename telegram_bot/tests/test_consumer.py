from unittest.mock import AsyncMock

import pytest

from app.consumer import OrderConsumer
from app.tg_client import TelegramClient


@pytest.mark.asyncio
async def test_process_order():
    mock_telegram = AsyncMock(spec=TelegramClient)
    consumer = OrderConsumer(mock_telegram)

    order_data = {
        "order_id": "test-123",
        "product_name": "Test Product",
        "quantity": 3,
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "status": "created",
        "created_at": "2023-01-01T00:00:00"
    }

    await consumer.process_order(order_data)

    mock_telegram.send_message.assert_called_once()
    message = mock_telegram.send_message.call_args[0][0]
    assert "Новый заказ" in message
    assert "test-123" in message
    assert "Test Product" in message
