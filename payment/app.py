import os
import atexit
from dotenv import load_dotenv
from flask import Flask, jsonify
import redis



app = Flask("payment-service")

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


@app.post('/create_user')
def create_user():
    user_id = db.incr('user_count')
    user = {"user_id": user_id}
    db.hset(f"user_id:{user_id}", "credit", 0)
    return jsonify(user)


@app.get('/find_user/<user_id>')
def find_user(user_id: str):
    user_credit = int(db.hget(f"user_id:{user_id}", "credit").decode("utf-8"))
    return jsonify({"user_id": user_id, "credit": user_credit})


@app.post('/add_funds/<user_id>/<amount>')
def add_credit(user_id: str, amount: int):
    db.hincrby(f"user_id:{user_id}", "credit", int(amount))
    return jsonify({"done": True})


@app.post('/pay/<user_id>/<order_id>/<amount>')
def remove_credit(user_id: str, order_id: str, amount: int):
    #TODO what is order_id used for???
    amount = int(amount)
    credit = int(db.hget(f'user_id:{user_id}', 'credit').decode('utf-8'))
    if credit < amount:
        return jsonify({"status_code": 400})
    credit -= amount
    db.hset(f'user_id:{user_id}', 'credit', credit)
    return jsonify({"status_code": 200})


@app.post('/cancel/<user_id>/<order_id>')
def cancel_payment(user_id: str, order_id: str):
    status = db.hget(f'order_id:{order_id}', 'paid').decode('utf-8')
    if status == 1:
        db.hset(f'order_id:{order_id}', 'paid', 0)
        return jsonify({"status_code": 200})
    
    # return failure if we try to cancel payment for order which is not yet paid ?
    return jsonify({"status_code": 400})


@app.post('/status/<user_id>/<order_id>')
def payment_status(user_id: str, order_id: str):
    status = db.hget(f'order_id:{order_id}', 'paid').decode('utf-8')
    return jsonify({"paid": status})
