import json
import os
from asyncio import sleep

from uuid import uuid4
from flask import Flask, jsonify, make_response
from backend.kafka_connectior import KafkaConnector
import logging
logging.basicConfig(level=logging.INFO)

bootstrap_servers = ""

if 'BOOTSTRAP_SERVERS' in os.environ:
    bootstrap_servers = os.environ['BOOTSTRAP_SERVERS']

connector = KafkaConnector(bootstrap_servers, 'test2', 'stock-rest')

app = Flask("stock-rest-service")


def retrieve_response(destination):
    for message in connector.consumer:
        payload = json.loads(message.value.decode('utf-8'))
        #print(payload['destination'])
        #if payload['destination'] == destination:
        response = payload['data']
        return response


@app.post('/item/create/<price>')
def create_item(price: float):
    destination = f'stock-{str(uuid4())}'

    payload = {'data': {'price': float(price)},
               'destination': destination}
    print(payload)
    connector.stock_item_create(payload)

    response = retrieve_response(destination)

    return make_response(jsonify(response), 200)

#
# @app.get('/find/<item_id>')
# async def response_find_item(item_id: str):
#     data = await connector.stock_find(item_id)
#     if not data:
#         return make_response(jsonify({}), 400)
#
#     return make_response(jsonify(data), 200)
#
#
# @app.post('/add/<item_id>/<amount>')
# async def response_add_stock(item_id: str, amount: int):
#     succeeded = await connector.stock_add(item_id, amount)
#     if succeeded:
#         return make_response(jsonify({}), 200)
#     else:
#         return make_response(jsonify({}), 400)
#
#
# @app.post('/subtract/<item_id>/<amount>')
# async def response_remove_stock(item_id: str, amount: int):
#     data = await connector.stock_subtract(item_id, amount)
#     if not data:
#         return make_response(jsonify({}), 400)
#
#     return make_response(jsonify(data), 200)
