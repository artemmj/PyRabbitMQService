from datetime import datetime, UTC
from unittest.mock import AsyncMock

import pytest

from app.rabbit_client import RabbitMQClient
from app.models import Order, OrderStatus


@pytest.mark.asyncio
async def test_publish_order_created():
    mock_channel = AsyncMock()
    mock_connection = AsyncMock()
    mock_connection.channel.return_value = mock_channel

    rabbitmq_client = RabbitMQClient()
    rabbitmq_client.connection = mock_connection
    rabbitmq_client.channel = mock_channel

    order = Order(
        id="test-id",
        product_name="Test Product",
        quantity=2,
        customer_name="Test Customer",
        customer_email="test@example.com",
        status=OrderStatus.CREATED,
        created_at=datetime.now(UTC)
    )

    await rabbitmq_client.publish_order_created(order)

    mock_channel.default_exchange.publish.assert_called_once()
    args = mock_channel.default_exchange.publish.call_args
    message = args[0][0]

    assert message.delivery_mode == 2
    assert "test-id" in message.body.decode()
