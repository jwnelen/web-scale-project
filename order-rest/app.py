import os
import threading

from flask import Flask, make_response, jsonify
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
        if data['message_type'] == "create_order":
            pass


if isinstance(connector, Eventbus_Connector):
    connector.consumer.subscribe('orders')

    consume_thread = threading.Thread(target=consume_messages)
    consume_thread.daemon = True  # Allow program to exit even if thread is still running
    consume_thread.start()

app = Flask("order-rest-service")


@app.post('/create/<user_id>')
def response_create_order(user_id):
    data = create_order(user_id)
    if not data:
        return make_response(jsonify({}), 400)

    return make_response(jsonify(data), 200)


@app.delete('/remove/<order_id>')
def response_remove_order(order_id):
    succeeded = remove_order(order_id)

    if not succeeded:
        return make_response(jsonify({}), 400)

    return make_response(jsonify({}), 200)


@app.post('/addItem/<order_id>/<item_id>')
def response_add_item(order_id, item_id):
    data = add_item(order_id, item_id)

    if not data:
        return make_response(jsonify({}), 404)

    return make_response(jsonify(data), 200)


@app.delete('/removeItem/<order_id>/<item_id>')
def response_remove_item(order_id, item_id):
    data = remove_item(order_id, item_id)
    return make_response(jsonify(data), 200)


@app.get('/find/<order_id>')
def response_find_order(order_id):
    data = find_order(order_id)

    if not data:
        return make_response(jsonify({}), 400)

    return make_response(jsonify(data), 200)


@app.post('/checkout/<order_id>')
def response_checkout(order_id):
    succeeded = checkout(order_id)

    if not succeeded:
        return make_response(jsonify({}), 400)

    return make_response(jsonify({}), 200)

