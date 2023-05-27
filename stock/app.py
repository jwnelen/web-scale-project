import os
import atexit
from flask import Flask, make_response, jsonify
import redis
import uuid
from db import StockDatabase
from backend.docker_connector import DockerConnector
from backend.k8s_connector import K8sConnector

app = Flask("stock-service")
gateway_url = ""

spanner_db = StockDatabase()

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


atexit.register(close_db_connection)


@app.route("/")
def hello():
    return "Hello World!"


@app.post('/item/create/<price>')
def create_item(price: int):
    r = spanner_db.create_item(price)
    if "error" in r:
        return {"error": r["error"]}, 400
    return r, 200


@app.get('/find/<item_id>')
def find_item(item_id: str):
    r = spanner_db.find_item(item_id)

    if "error" in r:
        return {"error": r["error"]}, 400
    return r, 200


@app.post('/add/<item_id>/<amount>')
def add_stock(item_id: str, amount: int):
    r = spanner_db.add_stock(item_id, amount)
    if "error" in r:
        return {"error": r["error"]}, 400
    return r, 200


@app.post('/subtract/<item_id>/<amount>')
def remove_stock(item_id: str, amount: int):
    r = spanner_db.remove_stock(item_id, amount)

    if "error" in r:
        return {"error": r["error"]}, 400
    return r, 200
