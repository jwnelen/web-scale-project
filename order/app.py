import os
import atexit
from dotenv import load_dotenv
from flask import Flask, jsonify
import pymongo as mongo

if os.environ.get("FLASK_DEBUG"):
    print('loading local env')
    load_dotenv("../env/order_mongo.env")
else:
    print('loading prod env')

gateway_url = os.environ['GATEWAY_URL']

app = Flask("order-service")

client: mongo.MongoClient = mongo.MongoClient(
    host=os.environ['MONGO_HOST'],
    port=int(os.environ['MONGO_PORT']),
    username=os.environ['MONGO_USERNAME'],
    password=os.environ['MONGO_PASSWORD'],
)

db = client[os.environ['MONGO_DB']]
orders_collection = db["orders"]
users_collection = db["users"]

def close_db_connection():
    client.close()


atexit.register(close_db_connection)


@app.route("/")
def hello():
    return "Hello World!"


@app.post('/create/<user_id>')
def create_order(user_id):
    pass


@app.delete('/remove/<order_id>')
def remove_order(order_id):
    pass


@app.post('/addItem/<order_id>/<item_id>')
def add_item(order_id, item_id):
    pass


@app.delete('/removeItem/<order_id>/<item_id>')
def remove_item(order_id, item_id):
    pass


@app.get('/find/<order_id>')
def find_order(order_id):
    # return jsonify({
    #     "order_id": order_id,
    #     "paid": False,
    #     "items": [],
    #     "user_id": 1,
    #     "total_cost": 0
    # })
    result = list(users_collection.find({}, {"_id": 0}))
    return result


@app.post('/checkout/<order_id>')
def checkout(order_id):
    pass
