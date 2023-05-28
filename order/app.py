import os
import threading

from flask import Flask, g

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

    r = spanner_db.create_order(user_id)

    if "error" in r:
        return {"error": r["error"]}, 400
    return r, 200


@app.delete('/remove/<order_id>')
def remove_order(order_id):
    r = spanner_db.remove_order(order_id)

    if r:
        return {"r": r}, 200
    return {}, 400


@app.post('/addItem/<order_id>/<item_id>')
def response_add_item(order_id, item_id):
    result = connector.stock_find(item_id)
    if not result:
        return {"error": "Could not find item"}, 404

    data = spanner_db.add_item_to_order(order_id, item_id, result['price'])
    if "error" in data:
        return {"error": data["error"]}, 400

    return data, 200


@app.delete('/removeItem/<order_id>/<item_id>')
def response_remove_item(order_id, item_id):
    result = connector.stock_find(item_id)
    if not result:
        return {"error": "Could not find item"}, 404

    data = spanner_db.remove_item_from_order(order_id, item_id, result['price'])
    if "error" in data:
        return {"error": data["error"]}, 400

    return data, 200


@app.get('/find/<order_id>')
def find_order(order_id):
    res = spanner_db.find_order(order_id)
    if res:
        return res, 200

    return {}, 400


def checkout(order_id):
    pass
    # order = g.db.hgetall(f'order_id:{order_id}')
    # items = order[b'items'].decode("utf-8")
    #
    # total_cost = 0.0
    # for item in items.split(","):
    #     if item == '':
    #         continue
    #     result = connector.stock_find(item)
    #
    #     if result is not None:
    #         total_cost += float(result['price'])
    #
    # payment = connector.payment_pay(order[b'user_id'].decode('utf-8'), order_id, total_cost)
    #
    # if payment.status_code != 200:
    #     return False
    # for item in items.split(","):
    #     if item == '':
    #         continue
    #     subtract = connector.stock_subtract(item, 1)
    #     if subtract.status_code != 200:
    #         return False
    #
    # return True
