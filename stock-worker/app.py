import json
import os
import threading
import logging

from uuid import uuid4
from backend.kafka_connectior import KafkaConnector
from database import SpannerDB


def create_item(payload, db):
    data = payload['data']
    destination = payload['destination']

    item_id = str(uuid4())
    price = float(data['price'])

    data = db.create_item(item_id, price)

    response = {'data': data,
                'destination': destination}

    return response


def find(payload, db):
    data = payload['data']
    destination = payload['destination']

    item_id = data['item_id']

    data = db.find_item(item_id)

    response = {'data': data,
                'destination': destination}

    return response


def add(payload, db):
    data = payload['data']
    destination = payload['destination']

    item_id = data['item_id']
    amount = int(data['amount'])

    data = db.add_stock(item_id, amount)

    response = {'data': data,
                'destination': destination}

    return response


def subtract(payload, db):
    data = payload['data']
    destination = payload['destination']

    item_id = data['item_id']
    amount = int(data['amount'])

    data = db.remove_stock(item_id, amount)

    response = {'data': data,
                'destination': destination}

    return response


def process_message(message, connector, db):
    payload = json.loads(message.value.decode('utf-8'))
    message_type = payload['message_type']
    print(payload)
    if message_type == "item_create":
        response = create_item(payload, db)
        connector.deliver_response('stock-rest', response)
    if message_type == "find":
        response = find(payload, db)
        connector.deliver_response('stock-rest', response)
    if message_type == "add":
        response = add(payload, db)
        connector.deliver_response('stock-rest', response)
    if message_type == "subtract":
        response = subtract(payload, db)
        connector.deliver_response('stock-rest', response)


def consume_messages(connector, db):
    for message in connector.consumer:
        threading.Thread(target=process_message, args=(message, connector, db)).start()


def main():
    logging.basicConfig(level=logging.INFO)
    bootstrap_servers = ""

    if 'BOOTSTRAP_SERVERS' in os.environ:
        bootstrap_servers = os.environ['BOOTSTRAP_SERVERS']

    connector = KafkaConnector(bootstrap_servers, 'stock', 'stock-worker')

    db = SpannerDB()

    consume_messages(connector, db)


if __name__ == "__main__":
    main()
