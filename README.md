# PyRabbitMQService
Микросервисы на RabbitMQ, демонстрация возможностей

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![RabbitMQ](https://img.shields.io/badge/RabbitMQ-4.1%2B-green)](https://rabbitmq.com)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen)](tests/)

Микросервисная система для обработки заказов с использованием RabbitMQ в качестве message broker. Проект демонстрирует асинхронную коммуникацию между сервисами через брокер сообщений.

### Диаграмма взаимодействия сервисов

```mermaid
graph TD
    A[Клиент] -->|HTTP POST /orders| B[Order Service]
    B -->|Сохраняет заказ| C[Локальная память]
    B -->|Publish message| D[RabbitMQ]
    D -->|Consume messages| E[Telegram Bot]
    D -->|Consume messages| G[Python Service]
    E -->|Send notification| F[Telegram Chat]
    
    subgraph "Микросервисная система"
        B
        C
        G
        E
    end
    
    subgraph "Инфраструктура"
        D[RabbitMQ Broker]
    end
```

### Поток данных:
1. **Client** → **Order Service**: HTTP запрос на создание заказа
2. **Order Service** → **RabbitMQ**: Публикация сообщения в очередь `orders_queue`
3. **RabbitMQ** → **Telegram Bot**: Доставка сообщения consumer'у
4. **Telegram Bot** → **Telegram**: Отправка уведомления в чат

## 🚀 Запуск

### Предварительные требования

- Docker и Docker Compose
- Python 3.11+ (для локального запуска)
- Telegram Bot Token (получить у [@BotFather](https://t.me/BotFather))

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd <repo>
```

### 2. Настройка переменных окружения

Создайте файл `.env` в корневой директории:

```env
# RabbitMQ
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here
```

### 3. Запуск через Docker Compose

```bash
docker-compose up -d
```

Сервисы будут доступны:
- **Order Service**: http://localhost:8000
- **RabbitMQ Management**: http://localhost:15672 (guest/guest)
- **Telegram Bot**: запущен в фоне

### 4. Проверка работы

```bash
# Создание тестового заказа
curl -X POST "http://localhost:8000/orders" \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Test Product",
    "quantity": 2,
    "customer_name": "John Doe",
    "customer_email": "john@example.com"
  }'
```
