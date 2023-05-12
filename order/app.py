import os
import atexit
from dotenv import load_dotenv
from flask import Flask, jsonify
import redis
import sys


gateway_url = os.environ['GATEWAY_URL']

app = Flask("order-service")

db: redis.Redis = redis.Redis(host=os.environ['REDIS_HOST'],
                              port=int(os.environ['REDIS_PORT']),
                              password=os.environ['REDIS_PASSWORD'],
                              db=int(os.environ['REDIS_DB']))


def close_db_connection():
    db.close()


atexit.register(close_db_connection)


@app.post('/create/<user_id>')
def create_order(user_id):
    order_id = db.incr('order_count')
    db.hset(f'order_id:{order_id}', 'user_id', user_id)
    db.hset(f'order_id:{order_id}', 'paid', 0)
    db.hset(f'order_id:{order_id}', 'items', "")
    db.hset(f'order_id:{order_id}', 'total_cost', 0)
    return jsonify({"order_id": order_id})


@app.delete('/remove/<order_id>')
def remove_order(order_id):
    db.hdel(f"order_id:{order_id}", "user_id")
    return jsonify({'status_code': 200})


@app.post('/addItem/<order_id>/<item_id>')
def add_item(order_id, item_id):
    order_items = db.hget(f'order_id:{order_id}', 'items').decode("utf-8")
    order_items += str(item_id)+","
    db.hset(f'order_id:{order_id}', 'items', order_items)

    total_cost = 0
    for item in order_items.split(","):
        result = db.hget(f'item_id:{item}', 'cost')
        if result != None:
            total_cost += int(result.decode("utf-8"))

    db.hset(f'order_id:{order_id}', 'total_cost', total_cost)

    return jsonify({'status_code': 200})


@app.delete('/removeItem/<order_id>/<item_id>')
def remove_item(order_id, item_id):
    order_items = db.hget(f'order_id:{order_id}', 'items').decode("utf-8")
    order_items = str.replace(order_items, str(item_id)+",", "")
    db.hset(f'order_id:{order_id}', 'items', order_items)

    total_cost = 0
    for item in order_items.split(","):
        result = db.hget(f'item_id:{item}', 'cost')
        if result != None:
            total_cost += int(result.decode("utf-8"))

    db.hset(f'order_id:{order_id}', 'total_cost', total_cost)

    return jsonify({'status_code': 200})

@app.get('/find/<order_id>')
def find_order(order_id):
    query_result = db.hgetall(f'order_id:{order_id}')
    result = {}
    result['order_id'] = order_id
    result['user_id'] = query_result['user_id'].decode("utf-8")
    result['paid'] = query_result['paid'].decode("utf-8")
    result['items'] = query_result['items'].decode("utf-8")
    result['total_cost'] = query_result['total_cost'].decode("utf-8")
    return result

@app.post('/checkout/<order_id>')
def checkout(order_id):
    return jsonify({'status_code': 400})