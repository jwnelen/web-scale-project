import os
import atexit
from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, url_for
import redis
import sys
import requests
import socket


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

    response = jsonify({"order_id": order_id})
    response.status_code = 200
    return response


@app.delete('/remove/<order_id>')
def remove_order(order_id):
    response = make_response("")
    db.hdel(f"order_id:{order_id}", "user_id")
    response.status_code = 200
    return response


@app.post('/addItem/<order_id>/<item_id>')
def add_item(order_id, item_id):
    response = make_response("")
    order_items = db.hget(f'order_id:{order_id}', 'items').decode("utf-8")
    order_items += str(item_id)+","
    db.hset(f'order_id:{order_id}', 'items', order_items)

    response.status_code = 200
    return response


@app.delete('/removeItem/<order_id>/<item_id>')
def remove_item(order_id, item_id):
    response = make_response("")
    order_items = db.hget(f'order_id:{order_id}', 'items').decode("utf-8")
    order_items = str.replace(order_items, str(item_id)+",", "")
    db.hset(f'order_id:{order_id}', 'items', order_items)

    response.status_code = 200
    return response

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
    response = make_response("")

    order = db.hgetall(f'order_id:{order_id}')
    items = order[b'items'].decode("utf-8")

    total_cost = 0
    for item in items.split(","):
        if item == '':
            continue
        result = requests.get(f"{gateway_url}/stock/find/{item}").json()

        if result != None:
            total_cost += int(result['price'])

    payment = requests.post(f"{gateway_url}/payment/pay/{order[b'user_id'].decode('utf-8')}/{order_id}/{total_cost}", json={"total_cost": total_cost, "order_id": order_id})

    if payment.status_code != 200:
        response.status_code = payment.status_code
        return response
    
    for item in items.split(","):
        if item == '':
            continue
        subtract = requests.post(f"{gateway_url}/stock/subtract/{item}/1")
        if subtract.status_code != 200:
            response.status_code = subtract.status_code
            return response
        
    response.status_code = 200
    return response