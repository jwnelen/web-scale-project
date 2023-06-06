import json
import os
import threading
import logging

from uuid import uuid4
from backend.kafka_connectior import KafkaConnector
from database import SpannerDB


def create(payload, db):
    data = payload['data']
    destination = payload['destination']

    user_id = data['user_id']
    order_id = str(uuid4())

    data = db.create_order(order_id, user_id)

    response = {'data': data,
                'destination': destination}

    return response


def find(payload, db):
    data = payload['data']
    destination = payload['destination']

    order_id = data['order_id']

    data = db.find_order(order_id)

    response = {'data': data,
                'destination': destination}

    return response


def remove(payload, db):
    data = payload['data']
    destination = payload['destination']

    order_id = data['order_id']

    data = db.remove_order(order_id)

    response = {'data': data,
                'destination': destination}

    return response


def add_item(payload, db):
    data = payload['data']
    destination = payload['destination']

    order_id = data['order_id']
    item_id = data['item_id']

    data = db.add_item_to_order(order_id, item_id)

    response = {'data': data,
                'destination': destination}

    return response


def remove_item(payload, db):
    data = payload['data']
    destination = payload['destination']

    order_id = data['order_id']
    item_id = data['item_id']

    data = db.remove_item_from_order(order_id, item_id)

    response = {'data': data,
                'destination': destination}

    return response


def checkout(payload, db):
    data = payload['data']
    destination = payload['destination']

    order_id = data['order_id']

    data = db.checkout(order_id)

    response = {'data': data,
                'destination': destination}

    return response


def process_message(message, connector, db):
    payload = json.loads(message.value.decode('utf-8'))
    message_type = payload['message_type']

    if message_type == "create_user":
        response = create(payload, db)
        connector.deliver_response('order-rest', response)
    if message_type == "remove":
        response = remove(payload, db)
        connector.deliver_response('order-rest', response)
    if message_type == "addItem":
        response = add_item(payload, db)
        connector.deliver_response('order-rest', response)
    if message_type == "removeItem":
        response = remove_item(payload, db)
        connector.deliver_response('order-rest', response)
    if message_type == "find":
        response = find(payload, db)
        connector.deliver_response('order-rest', response)
    if message_type == "checkout":
        response = checkout(payload, db)
        connector.deliver_response('order-rest', response)


def consume_messages(connector, db):
    for message in connector.consumer:
        threading.Thread(target=process_message, args=(message, connector, db)).start()


def main():
    logging.basicConfig(level=logging.INFO)
    bootstrap_servers = ""

    if 'BOOTSTRAP_SERVERS' in os.environ:
        bootstrap_servers = os.environ['BOOTSTRAP_SERVERS']

    connector = KafkaConnector(bootstrap_servers, 'order', 'order-worker')

    db = SpannerDB()

    consume_messages(connector, db)


if __name__ == "__main__":
    main()
