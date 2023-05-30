import json
import os
import threading
import logging

from uuid import uuid4
from redis import Redis, BlockingConnectionPool
from backend.kafka_connectior import KafkaConnector


def open_connection(db_pool):
    return Redis(connection_pool=db_pool)


def process_message(message, connector, db_pool):
    payload = json.loads(message.value.decode('utf-8'))
    message_type = payload['message_type']

    # if message_type == "item_create":
    #     response = create_item(payload, db_pool)
    #     connector.deliver_response('stock-rest', response)
    # if message_type == "find":
    #     response = find(payload, db_pool)
    #     connector.deliver_response('stock-rest', response)
    # if message_type == "add":
    #     response = add(payload, db_pool)
    #     connector.deliver_response('stock-rest', response)
    # if message_type == "subtract":
    #     response = subtract(payload, db_pool)
    #     connector.deliver_response('stock-rest', response)


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

# def create_order(user_id):
#     user_data = connector.payment_find_user(user_id)
#
#     if not user_data:
#         return {}
#
#     order_id = str(uuid.uuid4())
#
#     with g.db.pipeline(transaction=True) as pipe:
#         pipe.hset(f'order_id:{order_id}', 'user_id', user_id)
#         pipe.hset(f'order_id:{order_id}', 'paid', 0)
#         pipe.hset(f'order_id:{order_id}', 'items', "")
#         pipe.hset(f'order_id:{order_id}', 'total_cost', 0.0)
#         pipe.execute()
#
#     data = {"order_id": order_id}
#
#     return data
#
#
# def remove_order(order_id):
#     result = g.db.hdel(f"order_id:{order_id}", "user_id")
#     if not result:
#         return False
#     return True
#
#
# def add_item(order_id, item_id):
#     # Check the price of the item
#     result = connector.stock_find(item_id)
#
#     if result is None:
#         return {}
#
#     with g.db.pipeline(transaction=True) as pipe:
#         # Get information
#         order_items = g.db.hget(f'order_id:{order_id}', 'items').decode("utf-8")
#         total_cost = g.db.hget(f'order_id:{order_id}', 'total_cost').decode("utf-8")
#
#         order_items += str(item_id) + ","
#         total_cost = float(total_cost) + float(result['price'])
#
#         # Update information
#         pipe.hset(f'order_id:{order_id}', 'items', order_items)
#         pipe.hset(f'order_id:{order_id}', 'total_cost', total_cost)
#         pipe.execute()
#
#     data = {"new_total_cost": total_cost}
#
#     return data
#
#
# def remove_item(order_id, item_id):
#     order_items = g.db.hget(f'order_id:{order_id}', 'items').decode("utf-8")
#     order_items = str.replace(order_items, str(item_id) + ",", "")
#     g.db.hset(f'order_id:{order_id}', 'items', order_items)
#     data = {}
#     return data
#
#
# def find_order(order_id):
#     query_result = g.db.hgetall(f'order_id:{order_id}')
#
#     if not query_result:
#         return {}
#
#     result = {
#         'order_id': order_id,
#         'user_id': query_result[b'user_id'].decode("utf-8"),
#         'paid': query_result[b'paid'].decode("utf-8"),
#         'items': query_result[b'items'].decode("utf-8"),
#         'total_cost': query_result[b'total_cost'].decode("utf-8")
#     }
#
#     return result
#
#
# def checkout(order_id):
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
