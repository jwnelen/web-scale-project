import os
import atexit
from flask import Flask, jsonify, make_response
import redis
import sys
import uuid

app = Flask("stock-service")

db: redis.Redis = redis.Redis(host=os.environ['REDIS_HOST'],
                              port=int(os.environ['REDIS_PORT']),
                              password=os.environ['REDIS_PASSWORD'],
                              db=int(os.environ['REDIS_DB']))


def close_db_connection():
    db.close()


atexit.register(close_db_connection)


@app.route("/")
def hello():
    return "Hello World!"


@app.post('/item/create/<price>')
def create_item(price: int):
    with db.pipeline() as pipe:
        item_id = uuid.uuid4()
        pipe.hset(f'item_id:{item_id}', 'price', round(float(price)))
        pipe.hset(f'item_id:{item_id}', 'stock', 0)
        pipe.execute()
    data = {'item_id': item_id}
    return data, 200


@app.get('/find/<item_id>')
def find_item(item_id: str):
    item = db.hgetall(f'item_id:{item_id}')
    if item is None:
        return {}, 400
    items = {}
    for k, v in item.items():
        items[k.decode('utf-8')] = round(float(v.decode('utf-8')))
    return items, 200


@app.post('/add/<item_id>/<amount>')
def add_stock(item_id: str, amount: int):
    with db.pipeline() as pipe:
        pipe.exists(f'item_id:{item_id}')
        exists = int(pipe.execute()[0])
        if exists:     
            pipe.hincrby(f'item_id:{item_id}', 'stock', int(amount))
            return {}, 200
        else:
            return {}, 400


@app.post('/subtract/<item_id>/<amount>')
def remove_stock(item_id: str, amount: int):
    response = make_response("")
    data = {}
    with db.pipeline() as pipe:
        pipe.exists(f'item_id:{item_id}')
        exists = int(pipe.execute()[0])

        if not exists:
            return data, 400
        pipe.hget(f'item_id:{item_id}', 'stock')
        stock = int(pipe.execute()[0].decode('utf-8'))

        if stock < int(amount):
            response.status_code = 400
            return response
        
        pipe.hincrby(f'item_id:{item_id}', 'stock', -int(amount))
        stock -= int(amount)
        pipe.execute()
    data = {'stock': stock}
    return data, 200
