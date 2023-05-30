import json
import os
import threading
import logging

from uuid import uuid4
from redis import Redis, BlockingConnectionPool
from backend.kafka_connectior import KafkaConnector


def open_connection(db_pool):
    return Redis(connection_pool=db_pool)


def create_user(payload, db_pool):
    destination = payload['destination']

    user_id = str(uuid4())

    conn = open_connection(db_pool)

    with conn.pipeline(transaction=True) as pipe:
        key = f"user_id:{user_id}"
        pipe.hset(key, "credit", 0.0)
        pipe.execute()

    conn.close()

    data = {'user_id': user_id}

    response = {'data': data,
                'destination': destination}
    return response


def process_message(message, connector, db_pool):
    payload = json.loads(message.value.decode('utf-8'))
    message_type = payload['message_type']

    if message_type == "create_user":
        response = create_user(payload, db_pool)
        connector.deliver_response('payment-rest', response)


def consume_messages(connector, db_pool):
    for message in connector.consumer:
        threading.Thread(target=process_message, args=(message, connector, db_pool)).start()


def main():
    logging.basicConfig(level=logging.INFO)
    bootstrap_servers = ""

    if 'BOOTSTRAP_SERVERS' in os.environ:
        bootstrap_servers = os.environ['BOOTSTRAP_SERVERS']

    connector = KafkaConnector(bootstrap_servers, 'payment', 'payment-worker')

    db_pool = BlockingConnectionPool(
        host=os.environ['REDIS_HOST'],
        port=int(os.environ['REDIS_PORT']),
        password=os.environ['REDIS_PASSWORD'],
        db=int(os.environ['REDIS_DB']),
        timeout=10
    )

    consume_messages(connector, db_pool)


if __name__ == "__main__":
    main()

# def find_user(user_id: str):
#     user_credit = g.db.hget(f"user_id:{user_id}", "credit")
#
#     if not user_credit:
#         return {}
#
#     user_credit = float(user_credit.decode('utf-8'))
#     data = {"user_id": user_id, "credit": user_credit}
#
#     return data
#
#
# def add_credit(user_id: str, amount: float):
#     data = {'done': False}
#
#     with g.db.pipeline(transaction=True) as pipe:
#         pipe.exists(f'user_id:{user_id}')
#         exists = pipe.execute()[0]
#         if exists:
#             pipe.hget(f'user_id:{user_id}', 'credit')
#             credit = float(pipe.execute()[0].decode('utf-8'))
#
#             credit += float(amount)
#             pipe.hset(f"user_id:{user_id}", "credit", credit)
#             pipe.execute()
#             data['done'] = True
#             return data
#         else:
#             return data
#
#
# def remove_credit(user_id: str, order_id: str, amount: float):
#     with g.db.pipeline(transaction=True) as pipe:
#         pipe.hget(f'user_id:{user_id}', 'credit')
#         credit = float(pipe.execute()[0].decode('utf-8'))
#
#         if credit < float(amount):
#             return False
#
#         credit -= float(amount)
#         pipe.hset(f'user_id:{user_id}', 'credit', credit)
#         pipe.execute()
#
#     return True
#
#
# def cancel_payment(user_id: str, order_id: str):
#     with g.db.pipeline(transaction=True) as pipe:
#         pipe.hget(f'order_id:{order_id}', 'paid')
#         status = pipe.execute()[0].decode('utf-8')
#         if status == 1:
#             pipe.hset(f'order_id:{order_id}', 'paid', 0)
#             pipe.execute()
#             return True
#
#     # return failure if we try to cancel payment for order which is not yet paid ?
#     return False
#
#
# def payment_status(user_id: str, order_id: str):
#     status = g.db.hget(f'order_id:{order_id}', 'paid').decode('utf-8')
#
#     if not status:
#         return {}
#
#     data = {"paid": status}
#     return data
