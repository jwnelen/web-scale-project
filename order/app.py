import os
import atexit

import requests as requests
from bson import ObjectId
from dotenv import load_dotenv
from flask import Flask, jsonify
import pymongo as mongo

app = Flask("order-service")

if os.environ.get("FLASK_DEBUG"):
    print('loading local env')
    load_dotenv("../env/order_mongo.env")
else:
    print('loading prod env')

gateway_url = os.environ['GATEWAY_URL']
stock_url = os.environ["STOCK_SERVICE_URL"]

client: mongo.MongoClient = mongo.MongoClient(
    host=os.environ['MONGO_HOST'],
    port=int(os.environ['MONGO_PORT']),
    username=os.environ['MONGO_USERNAME'],
    password=os.environ['MONGO_PASSWORD'],
)

db = client[os.environ['MONGO_DB']]
orders_collection = db["orders"]


def close_db_connection():
    client.close()


atexit.register(close_db_connection)


@app.post('/create/<user_id>')
def create_order(user_id):
    new_order = {
        "paid": False,
        "items": [],
        "user_id": user_id,
        "total_cost": 0
    }
    result = orders_collection.insert_one(new_order)
    new_order["_id"] = str(result.inserted_id)
    return new_order


@app.delete('/remove/<order_id>')
def remove_order(order_id):
    r = orders_collection.delete_one({"_id": ObjectId(order_id)})
    return {"success": r.acknowledged}


@app.post('/addItem/<order_id>/<item_id>')
def add_item(order_id, item_id):
    orders_update = orders_collection.update_one({"_id": ObjectId(order_id)}, {"$push": {"items": item_id}})
    stock_update = requests.post(f'{stock_url}/subtract/{item_id}/1')
    result = orders_update.acknowledged & stock_update.json()["success"]
    return {"success": result}


@app.delete('/removeItem/<order_id>/<item_id>')
def remove_item(order_id, item_id):
    orders_update = orders_collection.update_one({"_id": ObjectId(order_id)}, {"$pull": {"items": item_id}})
    stock_update = requests.post(f'{stock_url}/add/{item_id}/1')
    result = orders_update.acknowledged & stock_update.json()["success"]
    return {"success": result}


@app.get('/find/<order_id>')
def find_order(order_id):
    return orders_collection.find({"_id": ObjectId(order_id)}, {"_id": 0})


@app.post('/checkout/<order_id>')
def checkout(order_id):
    pass
