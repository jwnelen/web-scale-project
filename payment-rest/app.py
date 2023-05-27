import os
import threading

from flask import Flask, jsonify, make_response
from backend.eventbus_connectior import Eventbus_Connector
from backend.k8s_connector import K8sConnector

bootstrap_servers = ""

if 'BOOTSTRAP_SERVERS' in os.environ:
    bootstrap_servers = os.environ['BOOTSTRAP_SERVERS']

# connector = Eventbus_Connector(bootstrap_servers)
connector = K8sConnector()


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

app = Flask("payment-rest-service")


@app.post('/create_user')
def response_create_user():
    data = create_user()
    return make_response(jsonify(data), 200)


@app.get('/find_user/<user_id>')
def response_find_user(user_id: str):
    data = find_user(user_id)
    if not data:
        return make_response(jsonify({}), 400)
    return make_response(jsonify(data), 200)


@app.post('/add_funds/<user_id>/<amount>')
def response_add_credit(user_id: str, amount: float):
    data = add_credit(user_id, amount)
    if data['done']:
        return make_response(jsonify(data), 200)
    else:
        return make_response(jsonify(data), 400)


@app.post('/pay/<user_id>/<order_id>/<amount>')
def response_remove_credit(user_id: str, order_id: str, amount: float):
    succeeded = remove_credit(user_id, order_id, amount)

    if not succeeded:
        return make_response(jsonify({}), 400)

    return make_response(jsonify({}), 200)


@app.post('/cancel/<user_id>/<order_id>')
def response_cancel_payment(user_id: str, order_id: str):
    succeeded = cancel_payment(user_id, order_id)

    if not succeeded:
        return make_response(jsonify({}), 400)

    return make_response(jsonify({}), 200)



@app.get('/status/<user_id>/<order_id>')
def response_payment_status(user_id: str, order_id: str):
    data = payment_status(user_id, order_id)

    if not data:
        return make_response(jsonify({}), 400)

    return make_response(jsonify(data), 200)
