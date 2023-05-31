import json
import os
import threading
import logging

from uuid import uuid4
from backend.kafka_connectior import KafkaConnector
from database import SpannerDB


def create_user(payload, db):
    destination = payload['destination']

    user_id = str(uuid4())

    data = db.create_user(user_id)

    response = {'data': data,
                'destination': destination}
    return response


def find_user(payload, db):
    data = payload['data']
    destination = payload['destination']

    user_id = data['user_id']

    data = db.find_user(user_id)

    response = {'data': data,
                'destination': destination}

    return response


def add_funds(payload, db):
    data = payload['data']
    destination = payload['destination']

    user_id = data['user_id']
    amount = float(data['amount'])

    data = db.add_credit_to_user(user_id, amount)

    response = {'data': data,
                'destination': destination}

    return response


def status(payload, db):
    data = payload['data']
    destination = payload['destination']

    order_id = data['order_id']

    data = db.get_payment_status(order_id)

    response = {'data': data,
                'destination': destination}

    return response


def process_message(message, connector, db):
    payload = json.loads(message.value.decode('utf-8'))
    message_type = payload['message_type']

    if message_type == "create_user":
        response = create_user(payload, db)
        connector.deliver_response('payment-rest', response)
    if message_type == "find_user":
        response = find_user(payload, db)
        connector.deliver_response('payment-rest', response)
    if message_type == "status":
        response = status(payload, db)
        connector.deliver_response('payment-rest', response)
    if message_type == "add_funds":
        response = add_funds(payload, db)
        connector.deliver_response('payment-rest', response)


def consume_messages(connector, db):
    for message in connector.consumer:
        threading.Thread(target=process_message, args=(message, connector, db)).start()


def main():
    logging.basicConfig(level=logging.INFO)
    bootstrap_servers = ""

    if 'BOOTSTRAP_SERVERS' in os.environ:
        bootstrap_servers = os.environ['BOOTSTRAP_SERVERS']

    connector = KafkaConnector(bootstrap_servers, 'payment', 'payment-worker')

    db = SpannerDB()

    consume_messages(connector, db)


if __name__ == "__main__":
    main()
