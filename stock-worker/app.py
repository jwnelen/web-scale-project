import os

from uuid import uuid4
from redis import Redis, BlockingConnectionPool

from backend.kafka_connectior import KafkaConnector

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

connector = KafkaConnector(bootstrap_servers, 'stock_workers', 'stock')


def open_connection():
    return Redis(connection_pool=pool)


async def create_item(payload):

    data = payload['data']
    destination = payload['destination']

    item_id = str(uuid4())
    price = data['price']

    conn = open_connection()

    async with conn.pipeline(transaction=True) as pipe:
        pipe.hset(f'item_id:{item_id}', 'price', float(price))
        pipe.hset(f'item_id:{item_id}', 'stock', 0)
        await pipe.execute()

    conn.close()

    data = {'item_id': item_id}

    response = {'data': data,
               'destination': destination}

    connector.deliver_response(response)


def process_message(message):
    payload = message.value().decode('utf-8')
    message_type = payload['message_type']

    if message_type == "item_create":
        create_item(payload)


def main():
    while True:
        message = connector.consumer.poll(1.0)

        if message is None:
            continue
        if message.error():
            print("Consumer error: {}".format(message.error()))
            continue

        process_message(message)


if __name__ == "__main__":
    main()

#
# def find_item(item_id: str):
#     item = g.db.hgetall(f'item_id:{item_id}')
#     if item is None:
#         return {}
#     price = float(g.db.hget(f'item_id:{item_id}', 'price').decode("utf-8"))
#     stock = int(g.db.hget(f'item_id:{item_id}', 'stock').decode("utf-8"))
#
#     data = {'price': price, 'stock': stock}
#     return data
#
#
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
