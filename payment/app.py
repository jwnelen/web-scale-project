import os
import atexit
from dotenv import load_dotenv
from flask import Flask, jsonify
import pymongo as mongo

if os.environ.get("FLASK_DEBUG"):
    print('loading local env')
    load_dotenv("../env/payment_mongo.env")
else:
    print('loading prod env')

app = Flask("payment-service")

client: mongo.MongoClient = mongo.MongoClient(
    host=os.environ['MONGO_HOST'],
    port=int(os.environ['MONGO_PORT']),
    username=os.environ['MONGO_USERNAME'],
    password=os.environ['MONGO_PASSWORD'],
)

db = client[os.environ['MONGO_DB']]
collection_payments = db["payments"]
collection_users = db["users"]


def close_db_connection():
    client.close()


atexit.register(close_db_connection)


@app.route("/")
def hello():
    return "Hello World!"


@app.post('/create_user')
def create_user():
    u = {
        "first_name": "John",
        "last_name": "Doe",
    }
    res = collection_users.insert_one(u)
    u.update({"_id": str(res.inserted_id)})
    return u


@app.get('/find_user/<user_id>')
def find_user(user_id: str):
    return jsonify({
        "user_id": user_id,
        "credit": 0
    })
    # result = list(collection.find({}, {"_id": 0}))
    # return result


@app.post('/add_funds/<user_id>/<amount>')
def add_credit(user_id: str, amount: int):
    pass


@app.post('/pay/<user_id>/<order_id>/<amount>')
def remove_credit(user_id: str, order_id: str, amount: int):
    pass


@app.post('/cancel/<user_id>/<order_id>')
def cancel_payment(user_id: str, order_id: str):
    pass


@app.post('/status/<user_id>/<order_id>')
def payment_status(user_id: str, order_id: str):
    pass
