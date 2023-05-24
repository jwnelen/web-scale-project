import os
import atexit
import uuid
import redis

from flask import Flask, make_response

from docker_connector import DockerConnector

app = Flask("order-service")

gateway_url = os.environ['GATEWAY_URL']

db: redis.Redis = redis.Redis(host=os.environ['REDIS_HOST'],
                              port=int(os.environ['REDIS_PORT']),
                              password=os.environ['REDIS_PASSWORD'],
                              db=int(os.environ['REDIS_DB']))

connector = DockerConnector(gateway_url)


def close_db_connection():
    db.close()


atexit.register(close_db_connection)


def status_code_is_success(status_code: int) -> bool:
    return 200 <= status_code < 300


@app.post('/create/<user_id>')
def create_order(user_id):
    user_data = connector.payment_find_user(user_id)

    if not status_code_is_success(user_data.status_code):
        data = {}
        return data, 400

    with db.pipeline() as pipe:
        order_id = str(uuid.uuid4())
        pipe.hset(f'order_id:{order_id}', 'user_id', user_id)
        pipe.hset(f'order_id:{order_id}', 'paid', 0)
        pipe.hset(f'order_id:{order_id}', 'items', "")
        pipe.hset(f'order_id:{order_id}', 'total_cost', 0)
        pipe.execute()

    data = {"order_id": order_id}

    return data, 200


@app.delete('/remove/<order_id>')
def remove_order(order_id):
    result = db.hdel(f"order_id:{order_id}", "user_id")

    data = {}

    if not result:
        return data, 400

    return data, 200


@app.post('/addItem/<order_id>/<item_id>')
def add_item(order_id, item_id):
    response = make_response("")
    order_items = db.hget(f'order_id:{order_id}', 'items').decode("utf-8")
    order_items += str(item_id) + ","
    db.hset(f'order_id:{order_id}', 'items', order_items)

    response.status_code = 200
    return response


@app.delete('/removeItem/<order_id>/<item_id>')
def remove_item(order_id, item_id):
    response = make_response("")
    order_items = db.hget(f'order_id:{order_id}', 'items').decode("utf-8")
    order_items = str.replace(order_items, str(item_id) + ",", "")
    db.hset(f'order_id:{order_id}', 'items', order_items)

    response.status_code = 200
    return response


@app.get('/find/<order_id>')
def find_order(order_id):
    query_result = db.hgetall(f'order_id:{order_id}')

    result = {}

    if not query_result:
        return result, 400

    result['order_id'] = order_id
    result['user_id'] = query_result['user_id'].decode("utf-8")
    result['paid'] = query_result['paid'].decode("utf-8")
    result['items'] = query_result['items'].decode("utf-8")
    result['total_cost'] = query_result['total_cost'].decode("utf-8")

    return result, 200


@app.post('/checkout/<order_id>')
def checkout(order_id):
    response = make_response("")

    order = db.hgetall(f'order_id:{order_id}')
    items = order[b'items'].decode("utf-8")

    total_cost = 0
    for item in items.split(","):
        if item == '':
            continue
        result = connector.stock_find(item)

        if result != None:
            total_cost += int(result['price'])

    payment = connector.payment_pay(order[b'user_id'].decode('utf-8'), order_id, total_cost)

    if payment.status_code != 200:
        response.status_code = payment.status_code
        return response
    for item in items.split(","):
        if item == '':
            continue
        subtract = connector.stock_subtract(item, 1)
        if subtract.status_code != 200:
            response.status_code = subtract.status_code
            return response
    response.status_code = 200
    return response
