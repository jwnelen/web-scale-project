import json
import os
import threading
from time import sleep

from uuid import uuid4
from flask import Flask, jsonify, make_response
from gevent import monkey

from backend.kafka_rest_connectior import KafkaRESTConnector

connector = None
app = Flask("payment-rest-service")

messages = {}
waiting = {}


def start():
    monkey.patch_all()
    global connector
    connector = KafkaConnector(os.environ['BOOTSTRAP_SERVERS'], None, 'payment-rest')
    threading.Thread(target=retrieve_response, daemon=True).start()
    return app


def retrieve_response():
    for message in connector.consumer:
        payload = json.loads(message.value.decode('utf-8'))
        destination = payload['destination']

        if destination in waiting:
            messages[destination] = payload['data']
            waiting.pop(destination)


def get_response(destination):
    while True:
        if destination in messages:
            response = messages[destination]
            messages.pop(destination)
            return response
        sleep(0.01)


@app.post('/payment/create_user')
def create_user():
    destination = f'payment-{str(uuid4())}'
    waiting[destination] = True

    payload = {'data': {},
               'destination': destination}

    connector.payment_create_user(payload)

    response = get_response(destination)

    if not response:
        return make_response(jsonify({}), 400)

    return make_response(jsonify(response), 200)


@app.get('/payment/find_user/<user_id>')
def find_user(user_id: str):
    destination = f'payment-{str(uuid4())}'
    waiting[destination] = True

    payload = {'data': {'user_id': user_id},
               'destination': destination}

    connector.payment_find_user(payload)

    response = get_response(destination)

    if not response:
        return make_response(jsonify({}), 400)

    return make_response(jsonify(response), 200)


@app.post('/payment/add_funds/<user_id>/<amount>')
def add_funds(user_id: str, amount: float):
    destination = f'payment-{str(uuid4())}'
    waiting[destination] = True

    payload = {'data': {'user_id': user_id,
                        'amount': float(amount)},
               'destination': destination}

    connector.payment_add_funds(payload)

    response = get_response(destination)

    if not response['done']:
        return make_response(jsonify(response), 400)

    return make_response(jsonify(response), 200)


@app.post('/payment/pay/<user_id>/<order_id>/<amount>')
def pay(user_id: str, order_id: str, amount: float):
    destination = f'payment-{str(uuid4())}'
    waiting[destination] = True

    payload = {'data': {'user_id': user_id,
                        'order_id': order_id,
                        'amount': float(amount)},
               'destination': destination}

    connector.payment_pay(payload)

    response = get_response(destination)

    if not response['success']:
        return make_response(jsonify({}), 400)

    return make_response(jsonify({}), 200)


@app.get('/payment/status/<user_id>/<order_id>')
def status(user_id: str, order_id: str):
    destination = f'payment-{str(uuid4())}'
    waiting[destination] = True

    payload = {'data': {'user_id': user_id,
                        'order_id': order_id},
               'destination': destination}

    connector.payment_status(payload)

    response = get_response(destination)

    if not response['paid']:
        return make_response(jsonify(response), 400)

    return make_response(jsonify(response), 200)
