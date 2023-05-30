import json
import os
import threading
import logging

from uuid import uuid4
from redis import Redis, BlockingConnectionPool
from backend.kafka_connectior import KafkaConnector


def open_connection(db_pool):
    return Redis(connection_pool=db_pool)


def create(payload, db_pool):
    data = payload['data']
    destination = payload['destination']

    user_id = data['user_id']
    order_id = str(uuid4())

    conn = open_connection(db_pool)

    with conn.pipeline(transaction=True) as pipe:
        pipe.hset(f'order_id:{order_id}', 'user_id', user_id)
        pipe.hset(f'order_id:{order_id}', 'paid', 0)
        pipe.hset(f'order_id:{order_id}', 'items', "")
        pipe.hset(f'order_id:{order_id}', 'total_cost', 0.0)
        pipe.execute()

    conn.close()

    data = {"order_id": order_id}

    response = {'data': data,
                'destination': destination}

    return response


def find(payload, db_pool):
    data = payload['data']
    destination = payload['destination']

    order_id = data['order_id']

    conn = open_connection(db_pool)

    query_result = conn.hgetall(f'order_id:{order_id}')

    conn.close()

    if not query_result:
        data = {}
    else:
        data = {
            'order_id': order_id,
            'user_id': query_result[b'user_id'].decode("utf-8"),
            'paid': query_result[b'paid'].decode("utf-8"),
            'items': query_result[b'items'].decode("utf-8"),
            'total_cost': query_result[b'total_cost'].decode("utf-8")
        }

    response = {'data': data,
                'destination': destination}

    return response


def remove(payload, db_pool):
    data = payload['data']
    destination = payload['destination']

    order_id = data['order_id']

    conn = open_connection(db_pool)

    result = conn.hdel(f"order_id:{order_id}", "user_id")

    conn.close()

    if not result:
        data = {'success': False}
    else:
        data = {'success': True}

    response = {'data': data,
                'destination': destination}

    return response


def add_item(payload, db_pool):
    data = payload['data']
    destination = payload['destination']

    order_id = data['order_id']
    item_id = data['item_id']

    result = {'price': 1}  # TODO: Placeholder, but will be fixed with spanner

    conn = open_connection(db_pool)

    with conn.pipeline(transaction=True) as pipe:
        # Get information
        order_items = conn.hget(f'order_id:{order_id}', 'items').decode("utf-8")
        total_cost = conn.hget(f'order_id:{order_id}', 'total_cost').decode("utf-8")

        order_items += str(item_id) + ","
        total_cost = float(total_cost) + float(result['price'])

        # Update information
        pipe.hset(f'order_id:{order_id}', 'items', order_items)
        pipe.hset(f'order_id:{order_id}', 'total_cost', total_cost)
        pipe.execute()

    conn.close()

    data = {"success": True}

    response = {'data': data,
                'destination': destination}

    return response


def remove_item(payload, db_pool):
    data = payload['data']
    destination = payload['destination']

    order_id = data['order_id']
    item_id = data['item_id']

    conn = open_connection(db_pool)

    order_items = conn.hget(f'order_id:{order_id}', 'items').decode("utf-8")
    order_items = str.replace(order_items, str(item_id) + ",", "")
    conn.hset(f'order_id:{order_id}', 'items', order_items)

    conn.close()

    data = {"success": True}

    response = {'data': data,
                'destination': destination}

    return response


def checkout(payload, db_pool):
    data = payload['data']
    destination = payload['destination']

    order_id = data['order_id']

    conn = open_connection(db_pool)

    # TODO: Fix checkout (in spanner)

    #     order = g.db.hgetall(f'order_id:{order_id}')
    #     items = order[b'items'].decode("utf-8")
    #
    #     total_cost = 0.0
    #     for item in items.split(","):
    #         if item == '':
    #             continue
    #         result = connector.stock_find(item)
    #
    #         if result is not None:
    #             total_cost += float(result['price'])
    #
    #     payment = connector.payment_pay(order[b'user_id'].decode('utf-8'), order_id, total_cost)
    #
    #     if payment.status_code != 200:
    #         return False
    #     for item in items.split(","):
    #         if item == '':
    #             continue
    #         subtract = connector.stock_subtract(item, 1)
    #         if subtract.status_code != 200:
    #             return False
    #
    #     return True

    conn.close()

    data = {"success": True}

    response = {'data': data,
                'destination': destination}

    return response


def process_message(message, connector, db_pool):
    payload = json.loads(message.value.decode('utf-8'))
    message_type = payload['message_type']

    if message_type == "create_user":
        response = create(payload, db_pool)
        connector.deliver_response('order-rest', response)
    if message_type == "remove":
        response = remove(payload, db_pool)
        connector.deliver_response('order-rest', response)
    if message_type == "addItem":
        response = add_item(payload, db_pool)
        connector.deliver_response('order-rest', response)
    if message_type == "removeItem":
        response = remove_item(payload, db_pool)
        connector.deliver_response('order-rest', response)
    if message_type == "find":
        response = find(payload, db_pool)
        connector.deliver_response('order-rest', response)
    if message_type == "checkout":
        response = checkout(payload, db_pool)
        connector.deliver_response('order-rest', response)


def consume_messages(connector, db_pool):
    for message in connector.consumer:
        threading.Thread(target=process_message, args=(message, connector, db_pool)).start()


def main():
    logging.basicConfig(level=logging.INFO)
    bootstrap_servers = ""

    if 'BOOTSTRAP_SERVERS' in os.environ:
        bootstrap_servers = os.environ['BOOTSTRAP_SERVERS']

    connector = KafkaConnector(bootstrap_servers, 'order', 'order-worker')

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
