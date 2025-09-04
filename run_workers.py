import sys
import signal
import threading

from consumer import OrderConsumer

workers = []


def start_worker(worker_id):
    """Запускает воркер в отдельном потоке."""
    consumer = OrderConsumer(worker_id)
    workers.append(consumer)
    consumer.start_consuming()


def signal_handler(sig, frame):
    """
    Обработчик сигналов для graceful shutdown.
    Закрывает все соединения при остановке приложения.
    """
    print("Shutting down workers...")
    for worker in workers:
        worker.close()
    sys.exit(0)


if __name__ == '__main__':
    # Запускаем несколько воркеров для демонстрации распределения нагрузки
    for i in range(3):
        thread = threading.Thread(target=start_worker, args=(i+1,))
        thread.daemon = True
        thread.start()

    # Регистрируем обработчик для Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    print("Workers started. Press Ctrl+C to stop.")
    signal.pause()
