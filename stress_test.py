import time
import threading
from queue import Queue
from producer import OrderProducer
from consumer import OrderConsumer
from models import SessionLocal, Order, OrderStatus
from config import Config

class StressTester:
    """
    Класс для нагрузочного тестирования системы.
    Создает большое количество заказов и измеряет производительность.
    """
    
    def __init__(self, num_orders=1000, num_workers=5):
        self.num_orders = num_orders
        self.num_workers = num_workers
        self.results = Queue()
        self.completed_orders = 0

    def producer_worker(self, worker_id, num_orders):
        """
        Воркер для генерации заказов в нагрузочном тесте.
        
        Args:
            worker_id: ID воркера для логирования
            num_orders: Количество заказов для генерации
        """
        producer = OrderProducer()
        start_time = time.time()

        for i in range(num_orders):
            order_data = {
                'customer_name': f'Stress Customer {worker_id}-{i}',
                'product': f'Product {i % 100}',
                'quantity': (i % 5) + 1,
                'amount': ((i % 5) + 1) * 10.0
            }

            try:
                producer.create_order(order_data)
                self.results.put(('produced', worker_id, i, time.time()))
            except Exception as e:
                print(f"Producer {worker_id} error: {e}")

        producer.close()
        print(f"Producer {worker_id} finished in {time.time() - start_time:.2f}s")

    def consumer_worker(self, worker_id):
        """
        Воркер для обработки заказов в нагрузочном тесте.
        
        Args:
            worker_id: ID воркера для логирования
        """
        consumer = OrderConsumer(worker_id)
        start_time = time.time()
        processed = 0

        try:
            end_time = time.time() + 60  # Ограничение времени выполнения
            
            while time.time() < end_time and processed < self.num_orders // self.num_workers:
                consumer.connection.process_data_events(time_limit=1)
                processed += 1
                self.completed_orders += 1
                self.results.put(('consumed', worker_id, processed, time.time()))
        finally:
            consumer.close()
            print(f"Consumer {worker_id} processed {processed} orders in {time.time() - start_time:.2f}s")

    def run_stress_test(self):
        """Запускает полный цикл нагрузочного тестирования"""
        print(f"Starting stress test: {self.num_orders} orders, {self.num_workers} workers")

        start_time = time.time()

        # Запуск producers в отдельных потоках
        producer_threads = []
        orders_per_producer = self.num_orders // self.num_workers

        for i in range(self.num_workers):
            thread = threading.Thread(
                target=self.producer_worker,
                args=(i, orders_per_producer)
            )
            producer_threads.append(thread)
            thread.start()

        for thread in producer_threads:
            thread.join()

        production_time = time.time() - start_time
        print(f"Production completed in {production_time:.2f}s")

        time.sleep(2)  # Пауза для доставки сообщений

        # Запуск consumers в отдельных потоках
        consumer_threads = []
        consumption_start = time.time()

        for i in range(self.num_workers):
            thread = threading.Thread(
                target=self.consumer_worker,
                args=(i,)
            )
            consumer_threads.append(thread)
            thread.start()

        for thread in consumer_threads:
            thread.join(timeout=30)

        consumption_time = time.time() - consumption_start
        total_time = time.time() - start_time

        self.print_statistics(production_time, consumption_time, total_time)

    def print_statistics(self, production_time, consumption_time, total_time):
        """
        Выводит подробную статистику нагрузочного теста.
        
        Args:
            production_time: Время генерации заказов
            consumption_time: Время обработки заказов
            total_time: Общее время теста
        """
        session = SessionLocal()
        total_orders = session.query(Order).count()
        completed_orders = session.query(Order).filter_by(status=OrderStatus.COMPLETED).count()
        failed_orders = session.query(Order).filter_by(status=OrderStatus.FAILED).count()

        print("\n" + "="*50)
        print("STRESS TEST RESULTS")
        print("="*50)
        print(f"Total orders in DB: {total_orders}")
        print(f"Completed orders: {completed_orders}")
        print(f"Failed orders: {failed_orders}")
        print(f"Production rate: {self.num_orders/production_time:.2f} orders/sec")
        print(f"Consumption rate: {self.completed_orders/consumption_time:.2f} orders/sec")
        print(f"Total processing rate: {self.num_orders/total_time:.2f} orders/sec")
        print(f"Production time: {production_time:.2f}s")
        print(f"Consumption time: {consumption_time:.2f}s")
        print(f"Total time: {total_time:.2f}s")

        # Проверки целостности данных
        assert total_orders == self.num_orders, f"Expected {self.num_orders}, got {total_orders}"
        assert completed_orders + failed_orders == total_orders, "Orders count mismatch"

        print("✅ All checks passed!")


if __name__ == '__main__':
    tester = StressTester(num_orders=1000, num_workers=5)
    tester.run_stress_test()
