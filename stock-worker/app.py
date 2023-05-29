import json
import os

from uuid import uuid4

from redis import Redis, BlockingConnectionPool

from backend.kafka_connectior import KafkaConnector
import logging


def open_connection(db_pool):
    return Redis(connection_pool=db_pool)


def create_item(payload, db_pool):
    data = payload['data']
    print(data)
    destination = payload['destination']

    item_id = str(uuid4())
    price = data['price']

    conn = open_connection(db_pool)

    with conn.pipeline(transaction=True) as pipe:
        pipe.hset(f'item_id:{item_id}', 'price', float(price))
        pipe.hset(f'item_id:{item_id}', 'stock', 0)
        pipe.execute()

    conn.close()

    data = {'item_id': item_id}

    response = {'data': data,
                'destination': destination}

    return response


def find_item(payload, db_pool):
    data = payload['data']
    print(data)
    destination = payload['destination']

    item_id = data['item_id']

    conn = open_connection(db_pool)

    item = conn.exists(f'item_id:{item_id}')

    if item == 0:
        data = {}
    else:
        price = float(conn.hget(f'item_id:{item_id}', 'price').decode("utf-8"))
        stock = int(conn.hget(f'item_id:{item_id}', 'stock').decode("utf-8"))

        data = {'price': price, 'stock': stock}

    conn.close()
    response = {'data': data,
                'destination': destination}

    return response


def process_message(message, connector, db_pool):
    payload = json.loads(message.value.decode('utf-8'))
    message_type = payload['message_type']

    if message_type == "item_create":
        response = create_item(payload, db_pool)
        connector.deliver_response('stock-rest', response)
    if message_type == "find":
        response = find_item(payload, db_pool)
        connector.deliver_response('stock-rest', response)


def consume_messages(connector, db_pool):
    print("Consuming")
    for message in connector.consumer:
        print("Message received")
        process_message(message, connector, db_pool)


def main():
    logging.basicConfig(level=logging.INFO)
    bootstrap_servers = ""

    if 'BOOTSTRAP_SERVERS' in os.environ:
        bootstrap_servers = os.environ['BOOTSTRAP_SERVERS']

    connector = KafkaConnector(bootstrap_servers, 'stock', 'stock-worker')

    db_pool = BlockingConnectionPool(
        host=os.environ['REDIS_HOST'],
        port=int(os.environ['REDIS_PORT']),
        password=os.environ['REDIS_PASSWORD'],
        db=int(os.environ['REDIS_DB']),
        timeout=10
    )

    consume_messages(connector, db_pool)


if __name__ == "__main__":
    # asyncio.run(main())
    main()


# def add_stock(item_id: str, amount: int):
#     with g.db.pipeline(transaction=True) as pipe:
#         pipe.exists(f'item_id:{item_id}')
#         exists = pipe.execute()[0]
#         if exists:
#             pipe.hincrby(f'item_id:{item_id}', 'stock', int(amount))
#             pipe.execute()
#             return True
#         else:
#             return False
#
#
# def remove_stock(item_id: str, amount: int):
#     with g.db.pipeline(transaction=True) as pipe:
#         pipe.exists(f'item_id:{item_id}')
#         exists = pipe.execute()[0]
#
#         if not exists:
#             return {}
#         pipe.hget(f'item_id:{item_id}', 'stock')
#         stock = int(pipe.execute()[0].decode('utf-8'))
#
#         if stock < int(amount):
#             return {}
#
#         pipe.hincrby(f'item_id:{item_id}', 'stock', -int(amount))
#         stock -= int(amount)
#         pipe.execute()
#     data = {'stock': stock}
#     return data
