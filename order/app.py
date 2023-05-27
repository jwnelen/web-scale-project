import os
import atexit
import threading
import uuid

from flask import Flask, make_response, jsonify, g
from backend.docker_connector import DockerConnector
from backend.eventbus_connectior import Eventbus_Connector
from backend.k8s_connector import K8sConnector
from db import OrderDatabase
from redis import Redis, BlockingConnectionPool

gateway_url = ""
bootstrap_servers = ""
spanner_db = OrderDatabase()

if 'GATEWAY_URL' in os.environ:
    gateway_url = os.environ['GATEWAY_URL']

if 'BOOTSTRAP_SERVERS' in os.environ:
    bootstrap_servers = os.environ['BOOTSTRAP_SERVERS']

# db: Redis = Redis(host=os.environ['REDIS_HOST'],
#                   port=int(os.environ['REDIS_PORT']),
#                   password=os.environ['REDIS_PASSWORD'],
#                   db=int(os.environ['REDIS_DB']))

pool = BlockingConnectionPool(
    host=os.environ['REDIS_HOST'],
    port=int(os.environ['REDIS_PORT']),
    password=os.environ['REDIS_PASSWORD'],
    db=int(os.environ['REDIS_DB']),
    timeout=10
)

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


@app.before_request
def before_request():
    db: Redis = Redis(connection_pool=pool)
    g.db = db


@app.after_request
def after_request(response):
    if g.db is not None:
        g.db.close()
    return response


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
    data = add_item(order_id, item_id)

    if not data:
        return make_response(jsonify({}), 404)

    return make_response(jsonify(data), 200)


def add_item(order_id, item_id):
    # Check the price of the item
    result = connector.stock_find(item_id)

    if result is None:
        return {}

    with g.db.pipeline(transaction=True) as pipe:
        # Get information
        order_items = g.db.hget(f'order_id:{order_id}', 'items').decode("utf-8")
        total_cost = g.db.hget(f'order_id:{order_id}', 'total_cost').decode("utf-8")

        order_items += str(item_id) + ","
        total_cost = float(total_cost) + float(result['price'])

        # Update information
        pipe.hset(f'order_id:{order_id}', 'items', order_items)
        pipe.hset(f'order_id:{order_id}', 'total_cost', total_cost)
        pipe.execute()

    data = {"new_total_cost": total_cost}

    return data


@app.delete('/removeItem/<order_id>/<item_id>')
def response_remove_item(order_id, item_id):
    data = remove_item(order_id, item_id)
    return make_response(jsonify(data), 200)


def remove_item(order_id, item_id):
    order_items = g.db.hget(f'order_id:{order_id}', 'items').decode("utf-8")
    order_items = str.replace(order_items, str(item_id) + ",", "")
    g.db.hset(f'order_id:{order_id}', 'items', order_items)
    data = {}
    return data


@app.get('/find/<order_id>')
def find_order(order_id):
    res = spanner_db.find_order(order_id)
    if res:
        return res, 200

    return {}, 400


def checkout(order_id):
    order = g.db.hgetall(f'order_id:{order_id}')
    items = order[b'items'].decode("utf-8")

    total_cost = 0.0
    for item in items.split(","):
        if item == '':
            continue
        result = connector.stock_find(item)

        if result is not None:
            total_cost += float(result['price'])

    payment = connector.payment_pay(order[b'user_id'].decode('utf-8'), order_id, total_cost)

    if payment.status_code != 200:
        return False
    for item in items.split(","):
        if item == '':
            continue
        subtract = connector.stock_subtract(item, 1)
        if subtract.status_code != 200:
            return False

    return True
