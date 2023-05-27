import os
import threading

from uuid import uuid4
from backend.eventbus_connectior import Eventbus_Connector
from backend.k8s_connector import K8sConnector
from redis import BlockingConnectionPool

bootstrap_servers = ""

if 'BOOTSTRAP_SERVERS' in os.environ:
    bootstrap_servers = os.environ['BOOTSTRAP_SERVERS']

pool = BlockingConnectionPool(
    host=os.environ['REDIS_HOST'],
    port=int(os.environ['REDIS_PORT']),
    password=os.environ['REDIS_PASSWORD'],
    db=int(os.environ['REDIS_DB']),
    timeout=10
)

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


def create_user():
    user_id = str(uuid4())
    with g.db.pipeline(transaction=True) as pipe:
        key = f"user_id:{user_id}"

        pipe.hset(key, "credit", 0.0)
        pipe.execute()

    data = {"user_id": user_id}
    return data


def find_user(user_id: str):
    user_credit = g.db.hget(f"user_id:{user_id}", "credit")

    if not user_credit:
        return {}

    user_credit = float(user_credit.decode('utf-8'))
    data = {"user_id": user_id, "credit": user_credit}

    return data


def add_credit(user_id: str, amount: float):
    data = {'done': False}

    with g.db.pipeline(transaction=True) as pipe:
        pipe.exists(f'user_id:{user_id}')
        exists = pipe.execute()[0]
        if exists:
            pipe.hget(f'user_id:{user_id}', 'credit')
            credit = float(pipe.execute()[0].decode('utf-8'))

            credit += float(amount)
            pipe.hset(f"user_id:{user_id}", "credit", credit)
            pipe.execute()
            data['done'] = True
            return data
        else:
            return data


def remove_credit(user_id: str, order_id: str, amount: float):
    with g.db.pipeline(transaction=True) as pipe:
        pipe.hget(f'user_id:{user_id}', 'credit')
        credit = float(pipe.execute()[0].decode('utf-8'))

        if credit < float(amount):
            return False

        credit -= float(amount)
        pipe.hset(f'user_id:{user_id}', 'credit', credit)
        pipe.execute()

    return True


def cancel_payment(user_id: str, order_id: str):
    with g.db.pipeline(transaction=True) as pipe:
        pipe.hget(f'order_id:{order_id}', 'paid')
        status = pipe.execute()[0].decode('utf-8')
        if status == 1:
            pipe.hset(f'order_id:{order_id}', 'paid', 0)
            pipe.execute()
            return True

    # return failure if we try to cancel payment for order which is not yet paid ?
    return False


def payment_status(user_id: str, order_id: str):
    status = g.db.hget(f'order_id:{order_id}', 'paid').decode('utf-8')

    if not status:
        return {}

    data = {"paid": status}
    return data
