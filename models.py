import enum
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Enum
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime, UTC

from config import Config

# Базовый класс для SQLAlchemy моделей
Base = declarative_base()


class OrderStatus(enum.Enum):
    """
    Перечисление статусов заказа.
    Обеспечивает типобезопасность и предотвращает ошибки в статусах.
    """
    PENDING = "pending"        # Заказ создан, ожидает обработки
    PROCESSING = "processing"  # Заказ в процессе обработки
    COMPLETED = "completed"    # Заказ успешно обработан
    FAILED = "failed"          # Заказ не удалось обработать


class Order(Base):
    """
    Модель заказа для хранения в базе данных.
    Отслеживает состояние заказа и историю обработки.
    """
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True)
    customer_name = Column(String(100), nullable=False)
    product = Column(String(100), nullable=False)
    quantity = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    created_at = Column(DateTime, default=datetime.now(UTC))
    updated_at = Column(DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))
    retries = Column(Integer, default=0)  # Счетчик попыток обработки
    
    def to_dict(self):
        """
        Преобразует объект заказа в словарь для сериализации.
        Используется для API responses и логирования.
        """
        return {
            'id': self.id,
            'customer_name': self.customer_name,
            'product': self.product,
            'quantity': self.quantity,
            'amount': self.amount,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


# Инициализация базы данных
engine = create_engine(Config.DATABASE_URL)
Base.metadata.create_all(engine)             # Создает таблицы если они не существуют
SessionLocal = sessionmaker(bind=engine)     # Фабрика сессий для работы с БД
