import os
import atexit
from flask import Flask, jsonify, make_response
import redis
import uuid
from db import UserDatabase
import threading

from flask import Flask, jsonify, make_response, g
from uuid import uuid4
from backend.docker_connector import DockerConnector
from backend.eventbus_connectior import Eventbus_Connector
from backend.k8s_connector import K8sConnector
from redis import BlockingConnectionPool
from redis import Redis

gateway_url = ""
bootstrap_servers = ""

spanner_db = UserDatabase()

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
        if data['message_type'] == "pay":
            pass


if isinstance(connector, Eventbus_Connector):
    connector.consumer.subscribe('orders')

    consume_thread = threading.Thread(target=consume_messages)
    consume_thread.daemon = True  # Allow program to exit even if thread is still running
    consume_thread.start()

app = Flask("payment-service")


@app.before_request
def before_request():
    db: Redis = Redis(connection_pool=pool)
    g.db = db


@app.after_request
def after_request(response):
    if g.db is not None:
        g.db.close()
    return response


@app.post('/create_user')
def response_create_user():
    data = create_user()
    return make_response(jsonify(data), 200)


def create_user():
    r = spanner_db.create_user()

    if "error" in r:
        return {"error": r["error"]}, 400
    return r, 200


def find_user(user_id: str):
    r = spanner_db.find_user(user_id)

    if "error" in r:
        return {"error": r["error"]}, 400
    return r, 200


@app.post('/add_funds/<user_id>/<amount>')
def add_credit(user_id: str, amount: int):
    r = spanner_db.add_credit_to_user(user_id, amount)
    return r, 200


# What is this doing anyway??
@app.post('/pay/<user_id>/<order_id>/<amount>')
def response_remove_credit(user_id: str, order_id: str, amount: float):
    succeeded = remove_credit(user_id, order_id, amount)

    if not succeeded:
        return make_response(jsonify({}), 400)

    return make_response(jsonify({}), 200)


def remove_credit(user_id: str, order_id: str, amount: float):
    with g.db.pipeline(transaction=True) as pipe:
        pipe.hget(f'user_id:{user_id}', 'credit')
        credit = float(pipe.execute()[0].decode('utf-8'))

        if credit < float(amount):
            return False

        credit -= float(amount)
        pipe.hset(f'user_id:{user_id}', 'credit', credit)
        pipe.execute()

    return True


@app.post('/cancel/<user_id>/<order_id>')
def response_cancel_payment(user_id: str, order_id: str):
    succeeded = cancel_payment(user_id, order_id)

    if not succeeded:
        return make_response(jsonify({}), 400)

    return make_response(jsonify({}), 200)


def cancel_payment(user_id: str, order_id: str):
    with g.db.pipeline(transaction=True) as pipe:
        pipe.hget(f'order_id:{order_id}', 'paid')
        status = pipe.execute()[0].decode('utf-8')
        if status == 1:
            pipe.hset(f'order_id:{order_id}', 'paid', 0)
            pipe.execute()
            return True

    # return failure if we try to cancel payment for order which is not yet paid ?
    return False


@app.get('/status/<user_id>/<order_id>')
def response_payment_status(user_id: str, order_id: str):
    data = payment_status(user_id, order_id)

    if not data:
        return make_response(jsonify({}), 400)

    return make_response(jsonify(data), 200)


def payment_status(user_id: str, order_id: str):
    status = g.db.hget(f'order_id:{order_id}', 'paid').decode('utf-8')

    if not status:
        return {}

    data = {"paid": status}
    return data
