import os
import threading

from flask import Flask

from backend.docker_connector import DockerConnector
from backend.eventbus_connectior import Eventbus_Connector
from db import StockDatabase

gateway_url = ""
bootstrap_servers = ""

spanner_db = StockDatabase()

if 'GATEWAY_URL' in os.environ:
    gateway_url = os.environ['GATEWAY_URL']

if 'BOOTSTRAP_SERVERS' in os.environ:
    bootstrap_servers = os.environ['BOOTSTRAP_SERVERS']

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


@app.post('/item/create/<price>')
def create_item(price: int):
    r = spanner_db.create_item(price)

    if "error" in r:
        return {"error": r["error"]}, 400
    return r, 200


@app.get('/find/<item_id>')
def find_item(item_id: str):
    r = spanner_db.find_item(item_id)

    if "error" in r:
        return {"error": r["error"]}, 400
    return r, 200


@app.post('/add/<item_id>/<amount>')
def add_stock(item_id: str, amount: int):
    r = spanner_db.add_stock(item_id, amount)

    if "error" in r:
        return {"error": r["error"]}, 400
    return r, 200


@app.post('/subtract/<item_id>/<amount>')
def remove_stock(item_id: str, amount: int):
    r = spanner_db.remove_stock(item_id, amount)

    if "error" in r:
        return {"error": r["error"]}, 400
    return r, 200
