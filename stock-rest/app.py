import os

from uuid import uuid4
from flask import Flask, jsonify, make_response
from backend.kafka_connectior import KafkaConnector

bootstrap_servers = ""

if 'BOOTSTRAP_SERVERS' in os.environ:
    bootstrap_servers = os.environ['BOOTSTRAP_SERVERS']

connector = KafkaConnector(bootstrap_servers, '', 'stock')

app = Flask("stock-rest-service")


@app.post('/item/create/<price>')
async def create_item(price: float):
    dest = f'stock-{uuid4}'

    payload = {'data': {'price': float(price)},
               'destination': dest}

    connector.stock_item_create(payload)

    data = {}
    waiting = True

    while waiting:
        message = await connector.consumer.poll(1.0)

        if message is None:
            continue
        if message.error():
            print("Consumer error: {}".format(message.error()))
            continue

        data = message.value
        waiting = False

    return make_response(jsonify(data), 200)

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
