import os
import atexit
import threading

from flask import Flask, jsonify, make_response
from uuid import uuid4
from backend.docker_connector import DockerConnector
from backend.eventbus_connectior import Eventbus_Connector
from backend.k8s_connector import K8sConnector

from redis import Redis


gateway_url = ""
bootstrap_servers = ""

if 'GATEWAY_URL' in os.environ:
    gateway_url = os.environ['GATEWAY_URL']

if 'BOOTSTRAP_SERVERS' in os.environ:
    bootstrap_servers = os.environ['BOOTSTRAP_SERVERS']

db: Redis = Redis(host=os.environ['REDIS_HOST'],
                  port=int(os.environ['REDIS_PORT']),
                  password=os.environ['REDIS_PASSWORD'],
                  db=int(os.environ['REDIS_DB']))


# connector = Eventbus_Connector(bootstrap_servers)
connector = DockerConnector(gateway_url)
# connector = K8sConnector()


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


def close_db_connection():
    db.close()


atexit.register(close_db_connection)


@app.route("/")
def hello():
    return "Hello World!"


@app.post('/create_user')
def response_create_user():
    data = create_user()
    return make_response(jsonify(data), 200)


def create_user():
    with db.pipeline(transaction=True) as pipe:
        user_id = str(uuid4())

        key = f"user_id:{user_id}"

        pipe.hset(key, "credit", 0)
        pipe.execute()

    data = {"user_id": user_id}
    return data


@app.get('/find_user/<user_id>')
def response_find_user(user_id: str):
    data = find_user(user_id)
    if not data:
        return make_response(jsonify({}), 400)
    return make_response(jsonify(data), 200)


def find_user(user_id: str):
    user_credit = db.hget(f"user_id:{user_id}", "credit")

    if not user_credit:
        return {}

    user_credit = int(user_credit.decode('utf-8'))
    data = {"user_id": user_id, "credit": user_credit}

    return data


@app.post('/add_funds/<user_id>/<amount>')
def response_add_credit(user_id: str, amount: int):
    data = add_credit(user_id, amount)
    if data['done']:
        return make_response(jsonify(data), 200)
    else:
        return make_response(jsonify(data), 400)


def add_credit(user_id: str, amount: int):
    amount = round(float(amount))
    data = {'done': False}

    with db.pipeline(transaction=True) as pipe:
        pipe.exists(f'user_id:{user_id}')
        exists = pipe.execute()[0]
        if exists:
            pipe.hincrby(f"user_id:{user_id}", "credit", amount)
            pipe.execute()
            data['done'] = True
            return data
        else:
            return data


@app.post('/pay/<user_id>/<order_id>/<amount>')
def response_remove_credit(user_id: str, order_id: str, amount: int):
    succeeded = remove_credit(user_id, order_id, amount)

    if not succeeded:
        return make_response(jsonify({}), 400)

    return make_response(jsonify({}), 200)


def remove_credit(user_id: str, order_id: str, amount: int):
    amount = int(amount)
    with db.pipeline(transaction=True) as pipe:
        pipe.hget(f'user_id:{user_id}', 'credit')
        credit = int(pipe.execute()[0].decode('utf-8'))

        if credit < amount:
            return False

        credit -= amount
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
    with db.pipeline(transaction=True) as pipe:
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
    status = db.hget(f'order_id:{order_id}', 'paid').decode('utf-8')
    db.execute()

    if not status:
        return {}

    data = {"paid": status}
    return data
