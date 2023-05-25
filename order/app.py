import os
import atexit
import threading
import uuid
import redis

from flask import Flask, make_response, jsonify

from backend.docker_connector import DockerConnector
from backend.eventbus_connectior import Eventbus_Connector
from backend.k8s_connector import K8sConnector

gateway_url = ""
bootstrap_servers = ""

if 'GATEWAY_URL' in os.environ:
    gateway_url = os.environ['GATEWAY_URL']

if 'BOOTSTRAP_SERVERS' in os.environ:
    bootstrap_servers = os.environ['BOOTSTRAP_SERVERS']

db: redis.Redis = redis.Redis(host=os.environ['REDIS_HOST'],
                              port=int(os.environ['REDIS_PORT']),
                              password=os.environ['REDIS_PASSWORD'],
                              db=int(os.environ['REDIS_DB']))

#connector = Eventbus_Connector(bootstrap_servers)
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


def close_db_connection():
    db.close()


atexit.register(close_db_connection)


def status_code_is_success(status_code: int) -> bool:
    return 200 <= status_code < 300


@app.route("/")
def hello():
    return "Hello World!"


@app.post('/create/<user_id>')
def create_order(user_id):
    user_data = connector.payment_find_user(user_id)

    if not user_data:
        return make_response(jsonify({}), 400)

    with db.pipeline() as pipe:
        order_id = str(uuid.uuid4())
        pipe.hset(f'order_id:{order_id}', 'user_id', user_id)
        pipe.hset(f'order_id:{order_id}', 'paid', 0)
        pipe.hset(f'order_id:{order_id}', 'items', "")
        pipe.hset(f'order_id:{order_id}', 'total_cost', 0)
        pipe.execute()

    data = {"order_id": order_id}

    return make_response(jsonify(data), 200)


@app.delete('/remove/<order_id>')
def remove_order(order_id):
    result = db.hdel(f"order_id:{order_id}", "user_id")

    if not result:
        return make_response(jsonify({}), 400)

    return make_response(jsonify({}), 200)


@app.post('/addItem/<order_id>/<item_id>')
def add_item(order_id, item_id):
    order_items = db.hget(f'order_id:{order_id}', 'items').decode("utf-8")
    order_items += str(item_id) + ","
    db.hset(f'order_id:{order_id}', 'items', order_items)
    data = {}
    return make_response(jsonify(data), 200)


@app.delete('/removeItem/<order_id>/<item_id>')
def remove_item(order_id, item_id):
    order_items = db.hget(f'order_id:{order_id}', 'items').decode("utf-8")
    order_items = str.replace(order_items, str(item_id) + ",", "")
    db.hset(f'order_id:{order_id}', 'items', order_items)
    return make_response(jsonify({}), 200)


@app.get('/find/<order_id>')
def find_order(order_id):
    query_result = db.hgetall(f'order_id:{order_id}')

    if not query_result:
        return make_response(jsonify({}), 400)

    result = {}
    result['order_id'] = order_id
    result['user_id'] = query_result[b'user_id'].decode("utf-8")
    result['paid'] = query_result[b'paid'].decode("utf-8")
    result['items'] = query_result[b'items'].decode("utf-8")
    result['total_cost'] = query_result[b'total_cost'].decode("utf-8")

    return make_response(jsonify(result), 200)


@app.post('/checkout/<order_id>')
def checkout(order_id):
    order = db.hgetall(f'order_id:{order_id}')
    items = order[b'items'].decode("utf-8")

    total_cost = 0
    for item in items.split(","):
        if item == '':
            continue
        result = connector.stock_find(item)

        if result != None:
            total_cost += int(result['price'])

    payment = connector.payment_pay(order[b'user_id'].decode('utf-8'), order_id, total_cost)

    if payment.status_code != 200:
        return make_response(jsonify({}), payment.status_code)
    for item in items.split(","):
        if item == '':
            continue
        subtract = connector.stock_subtract(item, 1)
        if subtract.status_code != 200:
            return make_response(jsonify({}), subtract.status_code)

    return make_response(jsonify({}), 200)
