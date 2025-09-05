from enum import Enum
from pydantic import BaseModel
from datetime import datetime


class CreateOrderRequest(BaseModel):
    product_name: str
    quantity: int
    customer_name: str
    customer_email: str


class OrderStatus(str, Enum):
    CREATED = "created"
    PROCESSING = "processing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Order(BaseModel):
    id: str
    product_name: str
    quantity: int
    customer_name: str
    customer_email: str
    status: OrderStatus
    created_at: datetime
