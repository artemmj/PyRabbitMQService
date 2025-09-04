from flask import Flask, request, jsonify

from producer import OrderProducer
from models import SessionLocal, Order

app = Flask(__name__)
producer = OrderProducer()


@app.route('/orders', methods=['POST'])
def create_order():
    """
    Endpoint для создания нового заказа.
    Принимает JSON с данными заказа, сохраняет в БД и отправляет в очередь.
    """
    try:
        data = request.get_json()
        required_fields = ['customer_name', 'product', 'quantity', 'amount']
        
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        order = producer.create_order(data)
        return jsonify(order), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/orders/<int:order_id>', methods=['GET'])
def get_order_status(order_id):
    """
    Endpoint для получения статуса заказа.
    Использует RPC механизм для запроса статуса через RabbitMQ.
    """
    try:
        status = producer.get_order_status(order_id)
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/orders', methods=['GET'])
def list_orders():
    """
    Endpoint для получения списка всех заказов.
    Прямой запрос к базе данных, минуя RabbitMQ.
    """
    session = SessionLocal()
    try:
        orders = session.query(Order).all()
        return jsonify([order.to_dict() for order in orders])
    finally:
        session.close()


if __name__ == '__main__':
    app.run(debug=True, port=5000)
