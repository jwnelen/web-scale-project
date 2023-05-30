import json
import os
import threading

from uuid import uuid4
from flask import Flask, jsonify, make_response
from backend.kafka_connectior import KafkaConnector

connector = None
app = Flask("payment-rest-service")

messages = {}
waiting = {}


def start():
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


@app.post('/create_user')
async def create_user():
    destination = f'payment-{str(uuid4())}'
    waiting[destination] = True

    payload = {'data': {},
               'destination': destination}

    connector.payment_create_user(payload)

    response = get_response(destination)

    return make_response(jsonify(response), 200)


@app.get('/find_user/<user_id>')
async def find_user(user_id: str):
    destination = f'payment-{str(uuid4())}'
    waiting[destination] = True

    payload = {'data': {'user_id': user_id},
               'destination': destination}

    connector.payment_find_user(payload)

    response = get_response(destination)

    if not response:
        return make_response(jsonify({}), 400)

    return make_response(jsonify(response), 200)


@app.post('/add_funds/<user_id>/<amount>')
async def add_credit(user_id: str, amount: float):
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


@app.post('/pay/<user_id>/<order_id>/<amount>')
async def remove_credit(user_id: str, order_id: str, amount: float):
    destination = f'payment-{str(uuid4())}'
    waiting[destination] = True

    payload = {'data': {'user_id': user_id,
                        'order_id': order_id,
                        'amount': float(amount)},
               'destination': destination}

    connector.payment_pay(payload)

    response = get_response(destination)

    if not response:
        return make_response(jsonify({}), 400)

    return make_response(jsonify({}), 200)


@app.post('/cancel/<user_id>/<order_id>')
async def cancel_payment(user_id: str, order_id: str):
    destination = f'payment-{str(uuid4())}'
    waiting[destination] = True

    payload = {'data': {'user_id': user_id,
                        'order_id': order_id},
               'destination': destination}

    connector.payment_cancel(payload)

    response = get_response(destination)

    if not response:
        return make_response(jsonify({}), 400)

    return make_response(jsonify({}), 200)


@app.get('/status/<user_id>/<order_id>')
async def payment_status(user_id: str, order_id: str):
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
