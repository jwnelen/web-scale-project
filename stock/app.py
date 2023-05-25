import os
import atexit
import threading

from flask import Flask, jsonify, make_response
import redis
import uuid

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
#connector = K8sConnector()


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

def close_db_connection():
    db.close()


atexit.register(close_db_connection)


@app.route("/")
def hello():
    return "Hello World!"


@app.post('/item/create/<price>')
def create_item(price: int):
    with db.pipeline() as pipe:
        item_id = uuid.uuid4()
        pipe.hset(f'item_id:{item_id}', 'price', round(float(price)))
        pipe.hset(f'item_id:{item_id}', 'stock', 0)
        pipe.execute()
    data = {'item_id': item_id}
    return make_response(jsonify(data), 200)


@app.get('/find/<item_id>')
def find_item(item_id: str):
    item = db.hgetall(f'item_id:{item_id}')
    if item is None:
        return make_response(jsonify({}), 400)
    items = {}
    for k, v in item.items():
        items[k.decode('utf-8')] = round(float(v.decode('utf-8')))
    return make_response(jsonify(items), 200)


@app.post('/add/<item_id>/<amount>')
def add_stock(item_id: str, amount: int):
    with db.pipeline() as pipe:
        pipe.exists(f'item_id:{item_id}')
        exists = pipe.execute()[0]
        if exists:
            pipe.hincrby(f'item_id:{item_id}', 'stock', int(amount))
            pipe.execute()
            return make_response(jsonify({}), 200)
        else:
            return make_response(jsonify({}), 400)


@app.post('/subtract/<item_id>/<amount>')
def remove_stock(item_id: str, amount: int):
    data = {}
    with db.pipeline() as pipe:
        pipe.exists(f'item_id:{item_id}')
        exists = pipe.execute()[0]

        if not exists:
            return data, 400
        pipe.hget(f'item_id:{item_id}', 'stock')
        stock = int(pipe.execute()[0].decode('utf-8'))

        if stock < int(amount):
            return make_response(jsonify({}), 400)

        pipe.hincrby(f'item_id:{item_id}', 'stock', -int(amount))
        stock -= int(amount)
        pipe.execute()
    data = {'stock': stock}
    return make_response(jsonify(data), 200)
