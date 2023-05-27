import os
import threading

from uuid import uuid4
from flask import Flask, jsonify, make_response
from backend.eventbus_connectior import Eventbus_Connector
from backend.k8s_connector import K8sConnector

bootstrap_servers = ""

if 'BOOTSTRAP_SERVERS' in os.environ:
    bootstrap_servers = os.environ['BOOTSTRAP_SERVERS']

# connector = Eventbus_Connector(bootstrap_servers)
connector = K8sConnector()

app = Flask("stock-rest-service")
ID = f'stock-{uuid4}'


def consume_messages():
    for message in connector.consumer:
        data = message.value
        if data['message_type'] == "create_order":
            pass


if isinstance(connector, Eventbus_Connector):
    connector.consumer.subscribe(ID)

    consume_thread = threading.Thread(target=consume_messages)
    consume_thread.daemon = True  # Allow program to exit even if thread is still running
    consume_thread.start()


@app.post('/item/create/<price>')
async def response_create_item(price: float):
    connector.stock_item_create(price)

    return make_response(jsonify(data), 200)


@app.get('/find/<item_id>')
async def response_find_item(item_id: str):
    data = await connector.stock_find(item_id)
    if not data:
        return make_response(jsonify({}), 400)

    return make_response(jsonify(data), 200)


@app.post('/add/<item_id>/<amount>')
async def response_add_stock(item_id: str, amount: int):
    succeeded = await connector.stock_add(item_id, amount)
    if succeeded:
        return make_response(jsonify({}), 200)
    else:
        return make_response(jsonify({}), 400)


@app.post('/subtract/<item_id>/<amount>')
async def response_remove_stock(item_id: str, amount: int):
    data = await connector.stock_subtract(item_id, amount)
    if not data:
        return make_response(jsonify({}), 400)

    return make_response(jsonify(data), 200)
