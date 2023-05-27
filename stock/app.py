import os
import atexit
from flask import Flask
import redis
from db import StockDatabase
import threading
import uuid

from flask import Flask, jsonify, make_response, g
from backend.docker_connector import DockerConnector
from backend.eventbus_connectior import Eventbus_Connector
from backend.k8s_connector import K8sConnector
from redis import Redis, BlockingConnectionPool

gateway_url = ""
bootstrap_servers = ""

spanner_db = StockDatabase()

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
def create_item(price: int):
    r = spanner_db.create_item(price)

    if "error" in r:
        return {"error": r["error"]}, 400
    return r, 200


@app.get('/find/<item_id>')
def response_find_item(item_id: str):
    data = find_item(item_id)
    if not data:
        return make_response(jsonify({}), 400)

    return make_response(jsonify(data), 200)


def find_item(item_id: str):
    r = spanner_db.find_item(item_id)

    if "error" in r:
        return {"error": r["error"]}, 400
    return r, 200


@app.post('/add/<item_id>/<amount>')
def response_add_stock(item_id: str, amount: int):
    succeeded = add_stock(item_id, amount)
    if succeeded:
        return make_response(jsonify({}), 200)
    else:
        return make_response(jsonify({}), 400)


def add_stock(item_id: str, amount: int):
    r = spanner_db.add_stock(item_id, amount)

    if "error" in r:
        return {"error": r["error"]}, 400
    return r, 200


@app.post('/subtract/<item_id>/<amount>')
def response_remove_stock(item_id: str, amount: int):
    data = remove_stock(item_id, amount)
    if not data:
        return make_response(jsonify({}), 400)

    return make_response(jsonify(data), 200)


def remove_stock(item_id: str, amount: int):
    r = spanner_db.remove_stock(item_id, amount)

    if "error" in r:
        return {"error": r["error"]}, 400
    return r, 200
