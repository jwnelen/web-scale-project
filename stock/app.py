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
    item_id = db.incr('item_id')
    db.hset(f'item_id:{item_id}', 'price', price)
    db.hset(f'item_id:{item_id}', 'stock', 0)
    print("CREATED ITEM:", item_id, price, file=sys.stderr)
    return jsonify({'item_id': item_id})

@app.get('/find/<item_id>')
def find_item(item_id: str):
    item = db.hgetall(f'item_id:{item_id}')
    items = {}
    for k, v in item.items():
        items[k.decode('utf-8')] = int(v.decode('utf-8'))
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
    exists = db.hget(f'item_id:{item_id}', 'stock')
    
    if exists == None:
        response.status_code = 400
        return response
    
    stock = db.hget(f'item_id:{item_id}', 'stock').decode("utf-8")
    if int(stock) < int(amount):
        response.status_code = 400
        return response
    
    db.hincrby(f'item_id:{item_id}', 'stock', -int(amount))
    response.status_code = 200
    return response
