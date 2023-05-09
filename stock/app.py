import os
import atexit
from dotenv import load_dotenv
from flask import Flask, jsonify
import pymongo as mongo

if os.environ.get("FLASK_DEBUG"):
    print('loading local env')
    load_dotenv("../env/stock_mongo.env")
else:
    print('loading prod env')

app = Flask("stock-service")

client: mongo.MongoClient = mongo.MongoClient(
    host=os.environ['MONGO_HOST'],
    port=int(os.environ['MONGO_PORT']),
    username=os.environ['MONGO_USERNAME'],
    password=os.environ['MONGO_PASSWORD'],
)

db = client[os.environ['MONGO_DB']]
collection = db["items"]


def close_db_connection():
    client.close()


atexit.register(close_db_connection)

@app.route("/")
def hello():
    return "Hello World!"

@app.post('/item/create/<price>')
def create_item(price: int):
    pass


@app.get('/find/<item_id>')
def find_item(item_id: str):
    return jsonify({
        "stock": 0,
        "price": 0
    })
    # result = list(collection.find({}, {"_id": 0}))
    # return result


@app.post('/add/<item_id>/<amount>')
def add_stock(item_id: str, amount: int):
    pass


@app.post('/subtract/<item_id>/<amount>')
def remove_stock(item_id: str, amount: int):
    pass
