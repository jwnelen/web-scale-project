import os
import threading

from flask import Flask

from backend.docker_connector import DockerConnector
from backend.eventbus_connectior import Eventbus_Connector
from db import OrderDatabase

gateway_url = ""
bootstrap_servers = ""

spanner_db = OrderDatabase()

if 'GATEWAY_URL' in os.environ:
    gateway_url = os.environ['GATEWAY_URL']

if 'BOOTSTRAP_SERVERS' in os.environ:
    bootstrap_servers = os.environ['BOOTSTRAP_SERVERS']
# connector = Eventbus_Connector(bootstrap_servers)
connector = DockerConnector(gateway_url)


# connector = K8sConnector()

def consume_messages():
    for message in connector.consumer:
        data = message.value
        if data['message_type'] == "create_order":
            pass


if isinstance(connector, Eventbus_Connector):
    connector.consumer.subscribe('orders')

    consume_thread = threading.Thread(target=consume_messages)
    consume_thread.daemon = True  # Allow program to exit even if thread is still running
    consume_thread.start()

app = Flask("order-service")


@app.post('/create/<user_id>')
def create_order(user_id):
    # This is not needed anymore, because the constaints will take care of this
    # user_data = connector.payment_find_user(user_id)

    result = spanner_db.create_order(user_id)

    if "error" in result:
        return result, 400

    return result, 200


@app.delete('/remove/<order_id>')
def remove_order(order_id):
    result = spanner_db.remove_order(order_id)

    if "error" in result:
        return result, 400

    return result, 200


@app.post('/addItem/<order_id>/<item_id>')
def response_add_item(order_id, item_id):
    data = connector.stock_find(item_id)
    if "error" in data:
        return {"error": "Could not find item"}, 400

    result = spanner_db.add_item_to_order(order_id, item_id, data['price'])
    if "error" in result:
        return result, 400

    return result, 200


@app.delete('/removeItem/<order_id>/<item_id>')
def response_remove_item(order_id, item_id):
    data = connector.stock_find(item_id)
    if not data:
        return {"error": "Could not find item"}, 404

    result = spanner_db.remove_item_from_order(order_id, item_id, data['price'])
    if "error" in result:
        return result, 400

    return result, 200


@app.get('/find/<order_id>')
def find_order(order_id):
    result = spanner_db.find_order(order_id)
    if "error" in result:
        return result, 400

    return result, 200


@app.post('/checkout/<order_id>')
def checkout(order_id):
    result = spanner_db.pay_order(order_id)
    print("PAY ORDER RESULT", result)
    if "error" in result:
        return {"succeeded": False}, 400

    return result, 200
