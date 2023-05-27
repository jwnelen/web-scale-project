import os
import atexit
import sys
import uuid
import redis

from flask import Flask, make_response, jsonify
from backend.docker_connector import DockerConnector
from backend.k8s_connector import K8sConnector
from db import OrderDatabase

app = Flask("order-service")
gateway_url = ""
spanner_db = OrderDatabase()

if 'GATEWAY_URL' in os.environ:
    gateway_url = os.environ['GATEWAY_URL']

db: redis.Redis = redis.Redis(host=os.environ['REDIS_HOST'],
                              port=int(os.environ['REDIS_PORT']),
                              password=os.environ['REDIS_PASSWORD'],
                              db=int(os.environ['REDIS_DB']))

connector = DockerConnector(gateway_url)


# connector = K8sConnector()


def close_db_connection():
    db.close()


def status_code_is_success(status_code: int) -> bool:
    return 200 <= status_code < 300


@app.post('/create/<user_id>')
def create_order(user_id):
    # This is not needed anymore, because the constaints will take care of this
    # user_data = connector.payment_find_user(user_id)

    r = spanner_db.create_order(user_id)
    if "error" in r:
        return {"error": r["error"]}, 400
    return r, 200


@app.delete('/remove/<order_id>')
def remove_order(order_id):
    r = spanner_db.remove_order(order_id)
    if r:
        return {"r": r}, 200
    return {}, 400


@app.post('/addItem/<order_id>/<item_id>')
def add_item(order_id, item_id):
    order_items = db.hget(f'order_id:{order_id}', 'items').decode("utf-8")
    order_items += str(item_id) + ","
    db.hset(f'order_id:{order_id}', 'items', order_items)
    data = {}
    return make_response(jsonify(data), 200)


@app.delete('/removeItem/<order_id>/<item_id>')
def remove_item(order_id, item_id):
    order_items = db.hget(f'order_id:{order_id}', 'items').decode("utf-8")
    order_items = str.replace(order_items, str(item_id) + ",", "")
    db.hset(f'order_id:{order_id}', 'items', order_items)
    return make_response(jsonify({}), 200)


@app.get('/find/<order_id>')
def find_order(order_id):
    res = spanner_db.find_order(order_id)
    if res:
        return res, 200

    return {}, 400


@app.post('/checkout/<order_id>')
def checkout(order_id):
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
        return make_response(jsonify({}), payment.status_code)
    for item in items.split(","):
        if item == '':
            continue
        subtract = connector.stock_subtract(item, 1)
        if subtract.status_code != 200:
            return make_response(jsonify({}), subtract.status_code)

    return make_response(jsonify({}), 200)
