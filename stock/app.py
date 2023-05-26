import os
import atexit
import threading
import uuid

from flask import Flask, jsonify, make_response, g
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

app = Flask("stock-service")


@app.before_request
def before_request():
    db: Redis = Redis(connection_pool=pool)
    g.db = db


@app.after_request
def after_request(response):
    if g.db is not None:
        g.db.close()
    return response


@app.post('/item/create/<price>')
def response_create_item(price: float):
    data = create_item(price)
    return make_response(jsonify(data), 200)


def create_item(price: float):
    item_id = str(uuid.uuid4())
    with g.db.pipeline(transaction=True) as pipe:
        pipe.hset(f'item_id:{item_id}', 'price', float(price))
        pipe.hset(f'item_id:{item_id}', 'stock', 0)
        pipe.execute()
    data = {'item_id': item_id}
    return data


@app.get('/find/<item_id>')
def response_find_item(item_id: str):
    data = find_item(item_id)
    if not data:
        return make_response(jsonify({}), 400)

    return make_response(jsonify(data), 200)


def find_item(item_id: str):
    item = g.db.hgetall(f'item_id:{item_id}')
    if item is None:
        return {}
    price = float(g.db.hget(f'item_id:{item_id}', 'price').decode("utf-8"))
    stock = int(g.db.hget(f'item_id:{item_id}', 'stock').decode("utf-8"))

    data = {'price': price, 'stock': stock}
    return data


@app.post('/add/<item_id>/<amount>')
def response_add_stock(item_id: str, amount: int):
    succeeded = add_stock(item_id, amount)
    if succeeded:
        return make_response(jsonify({}), 200)
    else:
        return make_response(jsonify({}), 400)


def add_stock(item_id: str, amount: int):
    with g.db.pipeline(transaction=True) as pipe:
        pipe.exists(f'item_id:{item_id}')
        exists = pipe.execute()[0]
        if exists:
            pipe.hincrby(f'item_id:{item_id}', 'stock', int(amount))
            pipe.execute()
            return True
        else:
            return False


@app.post('/subtract/<item_id>/<amount>')
def response_remove_stock(item_id: str, amount: int):
    data = remove_stock(item_id, amount)
    if not data:
        return make_response(jsonify({}), 400)

    return make_response(jsonify(data), 200)


def remove_stock(item_id: str, amount: int):
    with g.db.pipeline(transaction=True) as pipe:
        pipe.exists(f'item_id:{item_id}')
        exists = pipe.execute()[0]

        if not exists:
            return {}
        pipe.hget(f'item_id:{item_id}', 'stock')
        stock = int(pipe.execute()[0].decode('utf-8'))

        if stock < int(amount):
            return {}

        pipe.hincrby(f'item_id:{item_id}', 'stock', -int(amount))
        stock -= int(amount)
        pipe.execute()
    data = {'stock': stock}
    return data
