import json
import os
import threading

from uuid import uuid4
from flask import Flask, jsonify, make_response
from backend.kafka_connectior import KafkaConnector

connector = None
app = Flask("stock-rest-service")

messages = {}
waiting = {}


def start():
    global connector
    connector = KafkaConnector(os.environ['BOOTSTRAP_SERVERS'], None, 'stock-rest')
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


@app.post('/item/create/<price>')
async def create_item(price: float):
    destination = f'stock-{str(uuid4())}'
    waiting[destination] = True

    payload = {'data': {'price': float(price)},
               'destination': destination}

    connector.stock_item_create(payload)

    response = get_response(destination)

    return make_response(jsonify(response), 200)


@app.get('/find/<item_id>')
async def find_item(item_id: str):
    destination = f'stock-{str(uuid4())}'
    waiting[destination] = True

    payload = {'data': {'item_id': item_id},
               'destination': destination}

    connector.stock_find(payload)

    response = get_response(destination)

    if not response:
        return make_response(jsonify({}), 400)

    return make_response(jsonify(response), 200)


@app.post('/add/<item_id>/<amount>')
async def add_stock(item_id: str, amount: int):
    destination = f'stock-{str(uuid4())}'
    waiting[destination] = True

    payload = {'data': {'item_id': item_id, 'amount': amount},
               'destination': destination}

    connector.stock_add(payload)

    response = get_response(destination)

    if not response['success']:
        return make_response(jsonify({}), 400)

    return make_response(jsonify(response), 200)


@app.post('/subtract/<item_id>/<amount>')
async def response_remove_stock(item_id: str, amount: int):
    destination = f'stock-{str(uuid4())}'
    waiting[destination] = True

    payload = {'data': {'item_id': item_id, 'amount': amount},
               'destination': destination}

    connector.stock_subtract(payload)

    response = get_response(destination)

    if not response['success']:
        return make_response(jsonify({}), 400)

    return make_response(jsonify(response), 200)
