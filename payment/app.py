import os
import threading

from flask import Flask

from backend.docker_connector import DockerConnector
from backend.eventbus_connectior import Eventbus_Connector
from db import UserDatabase

gateway_url = ""
bootstrap_servers = ""

spanner_db = UserDatabase()

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
        if data['message_type'] == "pay":
            pass


if isinstance(connector, Eventbus_Connector):
    connector.consumer.subscribe('orders')

    consume_thread = threading.Thread(target=consume_messages)
    consume_thread.daemon = True  # Allow program to exit even if thread is still running
    consume_thread.start()

app = Flask("payment-service")


@app.post('/create_user')
def create_user():
    result = spanner_db.create_user()

    if "error" in result:
        return result, 400

    return result, 200


@app.get('/find_user/<user_id>')
def find_user(user_id: str):
    result = spanner_db.find_user(user_id)

    if "error" in result:
        return result, 400

    return result, 200


@app.post('/add_funds/<user_id>/<amount>')
def add_credit(user_id: str, amount: int):
    result = spanner_db.add_credit_to_user(user_id, amount)

    if "error" in result:
        return result, 400

    return result, 200


@app.post('/pay/<user_id>/<order_id>/<amount>')
def response_remove_credit(user_id: str, order_id: str, amount: float):
    pass


def remove_credit(user_id: str, order_id: str, amount: float):
    pass


@app.post('/cancel/<user_id>/<order_id>')
def response_cancel_payment(user_id: str, order_id: str):
    pass


def cancel_payment(user_id: str, order_id: str):
    pass


@app.get('/status/<user_id>/<order_id>')
def response_payment_status(user_id: str, order_id: str):
    result = spanner_db.get_payment_status(order_id)
    if "error" in result:
        return result, 400

    return result, 200
