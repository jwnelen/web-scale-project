import os
import atexit
import threading
import uuid

from flask import Flask, make_response, jsonify, g
from backend.docker_connector import DockerConnector
from backend.eventbus_connectior import Eventbus_Connector
from backend.k8s_connector import K8sConnector
from redis import Redis, BlockingConnectionPool

gateway_url = ""
bootstrap_servers = ""

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
#connector = DockerConnector(gateway_url)
connector = K8sConnector()


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

app = Flask("order-worker-service")


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
def response_create_order(user_id):
    data = create_order(user_id)
    if not data:
        return make_response(jsonify({}), 400)

    return make_response(jsonify(data), 200)


def create_order(user_id):
    user_data = connector.payment_find_user(user_id)

    if not user_data:
        return {}

    order_id = str(uuid.uuid4())

    with g.db.pipeline(transaction=True) as pipe:
        pipe.hset(f'order_id:{order_id}', 'user_id', user_id)
        pipe.hset(f'order_id:{order_id}', 'paid', 0)
        pipe.hset(f'order_id:{order_id}', 'items', "")
        pipe.hset(f'order_id:{order_id}', 'total_cost', 0.0)
        pipe.execute()

    data = {"order_id": order_id}

    return data


@app.delete('/remove/<order_id>')
def response_remove_order(order_id):
    succeeded = remove_order(order_id)

    if not succeeded:
        return make_response(jsonify({}), 400)

    return make_response(jsonify({}), 200)


def remove_order(order_id):
    result = g.db.hdel(f"order_id:{order_id}", "user_id")
    if not result:
        return False
    return True


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
def response_find_order(order_id):
    data = find_order(order_id)

    if not data:
        return make_response(jsonify({}), 400)

    return make_response(jsonify(data), 200)


def find_order(order_id):
    query_result = g.db.hgetall(f'order_id:{order_id}')

    if not query_result:
        return {}

    result = {
        'order_id': order_id,
        'user_id': query_result[b'user_id'].decode("utf-8"),
        'paid': query_result[b'paid'].decode("utf-8"),
        'items': query_result[b'items'].decode("utf-8"),
        'total_cost': query_result[b'total_cost'].decode("utf-8")
    }

    return result


@app.post('/checkout/<order_id>')
def response_checkout(order_id):
    succeeded = checkout(order_id)

    if not succeeded:
        return make_response(jsonify({}), 400)

    return make_response(jsonify({}), 200)


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
