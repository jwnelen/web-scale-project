import os
import atexit
from flask import Flask, jsonify, make_response
import redis
import sys

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
        pipe.incr('item_id')
        pipe.get('item_id')
        item_id = pipe.execute()[1].decode('utf-8')
        pipe.hset(f'item_id:{item_id}', 'price', round(float(price)))
        pipe.hset(f'item_id:{item_id}', 'stock', 0)
        result = pipe.execute()
    return jsonify({'item_id': item_id})

@app.get('/find/<item_id>')
def find_item(item_id: str):
    item = db.hgetall(f'item_id:{item_id}')
    items = {}
    for k, v in item.items():
        items[k.decode('utf-8')] = round(float(v.decode('utf-8')))
    return jsonify(items)

@app.post('/add/<item_id>/<amount>')
def add_stock(item_id: str, amount: int):
    response = make_response("")
    db.hincrby(f'item_id:{item_id}', 'stock', int(amount))
    response.status_code = 200
    return response


@app.post('/subtract/<item_id>/<amount>')
def remove_stock(item_id: str, amount: int):
    response = make_response("")
    with db.pipeline() as pipe:
        pipe.hget(f'item_id:{item_id}', 'stock')
        exists = pipe.execute()[0].decode('utf-8')

        if exists == None:
            response.status_code = 400
            return response
        
        pipe.hget(f'item_id:{item_id}', 'stock')
        stock = pipe.execute()[0].decode('utf-8')
        if int(stock) < int(amount):
            response.status_code = 400
            return response
        
        pipe.hincrby(f'item_id:{item_id}', 'stock', -int(amount))
        pipe.hget(f'item_id:{item_id}', 'stock')
        result = pipe.execute()
        stock = result[1].decode('utf-8')
    return jsonify({'stock': stock})
