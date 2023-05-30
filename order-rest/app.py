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


# @app.post('/create/<user_id>')
# def response_create_order(user_id):
#     data = create_order(user_id)
#     if not data:
#         return make_response(jsonify({}), 400)
#
#     return make_response(jsonify(data), 200)
#
#
# @app.delete('/remove/<order_id>')
# def response_remove_order(order_id):
#     succeeded = remove_order(order_id)
#
#     if not succeeded:
#         return make_response(jsonify({}), 400)
#
#     return make_response(jsonify({}), 200)
#
#
# @app.post('/addItem/<order_id>/<item_id>')
# def response_add_item(order_id, item_id):
#     data = add_item(order_id, item_id)
#
#     if not data:
#         return make_response(jsonify({}), 404)
#
#     return make_response(jsonify(data), 200)
#
#
# @app.delete('/removeItem/<order_id>/<item_id>')
# def response_remove_item(order_id, item_id):
#     data = remove_item(order_id, item_id)
#     return make_response(jsonify(data), 200)
#
#
# @app.get('/find/<order_id>')
# def response_find_order(order_id):
#     data = find_order(order_id)
#
#     if not data:
#         return make_response(jsonify({}), 400)
#
#     return make_response(jsonify(data), 200)
#
#
# @app.post('/checkout/<order_id>')
# def response_checkout(order_id):
#     succeeded = checkout(order_id)
#
#     if not succeeded:
#         return make_response(jsonify({}), 400)
#
#     return make_response(jsonify({}), 200)
#
