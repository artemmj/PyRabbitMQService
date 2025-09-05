import os
import uuid
from contextlib import asynccontextmanager
from pydantic import BaseModel
from datetime import datetime, UTC

from fastapi import FastAPI

from app.rabbit_client import RabbitMQClient
from app.models import CreateOrderRequest, Order, OrderStatus

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Инициализация RabbitMQ клиента
    rabbitmq_client = RabbitMQClient()
    await rabbitmq_client.connect(os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/"))
    app.state.rabbitmq_client = rabbitmq_client
    yield
    await rabbitmq_client.close()

app = FastAPI(title="Order Service", lifespan=lifespan)


@app.post("/orders", response_model=Order)
async def create_order(order_data: CreateOrderRequest):
    order_id = str(uuid.uuid4())
    order = Order(
        id=order_id,
        product_name=order_data.product_name,
        quantity=order_data.quantity,
        customer_name=order_data.customer_name,
        customer_email=order_data.customer_email,
        status=OrderStatus.CREATED,
        created_at=datetime.now(UTC)
    )
    await app.state.rabbitmq_client.publish_order_created(order)
    return order
