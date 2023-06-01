import json
import os
import threading

from uuid import uuid4
from flask import Flask, jsonify, make_response
from backend.kafka_connectior import KafkaConnector

connector = None
app = Flask("order-rest-service")

messages = {}
waiting = {}


def start():
    global connector
    connector = KafkaConnector(os.environ['BOOTSTRAP_SERVERS'], None, 'order-rest')
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


@app.post('/create/<user_id>')
async def create(user_id):
    destination = f'order-{str(uuid4())}'
    waiting[destination] = True

    payload = {'data': {'user_id': user_id},
               'destination': destination}

    connector.order_create_user(payload)

    response = get_response(destination)

    if not response:
        return make_response(jsonify({}), 400)

    return make_response(jsonify(response), 200)


@app.delete('/remove/<order_id>')
async def remove(order_id):
    destination = f'order-{str(uuid4())}'
    waiting[destination] = True

    payload = {'data': {'order_id': order_id},
               'destination': destination}

    connector.order_remove(payload)

    response = get_response(destination)

    if not response['success']:
        return make_response(jsonify({}), 400)

    return make_response(jsonify(response), 200)


@app.post('/addItem/<order_id>/<item_id>')
async def add_item(order_id, item_id):
    destination = f'order-{str(uuid4())}'
    waiting[destination] = True

    payload = {'data': {'order_id': order_id,
                        'item_id': item_id},
               'destination': destination}

    connector.order_addItem(payload)

    response = get_response(destination)

    if not response['success']:
        return make_response(jsonify({}), 400)

    return make_response(jsonify(response), 200)


@app.delete('/removeItem/<order_id>/<item_id>')
async def remove_item(order_id, item_id):
    destination = f'order-{str(uuid4())}'
    waiting[destination] = True

    payload = {'data': {'order_id': order_id,
                        'item_id': item_id},
               'destination': destination}

    connector.order_removeItem(payload)

    response = get_response(destination)

    if not response['success']:
        return make_response(jsonify({}), 400)

    return make_response(jsonify(response), 200)


@app.get('/find/<order_id>')
async def find(order_id):
    destination = f'order-{str(uuid4())}'
    waiting[destination] = True

    payload = {'data': {'order_id': order_id},
               'destination': destination}

    connector.order_find(payload)

    response = get_response(destination)

    if not response:
        return make_response(jsonify({}), 400)

    return make_response(jsonify(response), 200)


@app.post('/checkout/<order_id>')
async def checkout(order_id):
    destination = f'order-{str(uuid4())}'
    waiting[destination] = True

    payload = {'data': {'order_id': order_id},
               'destination': destination}

    connector.order_checkout(payload)

    response = get_response(destination)

    if not response['success']:
        return make_response(jsonify({}), 400)

    return make_response(jsonify(response), 200)

