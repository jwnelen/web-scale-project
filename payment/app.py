import os
import atexit
from flask import Flask, jsonify, make_response
import redis
import uuid


gateway_url = os.environ['GATEWAY_URL']

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
    with db.pipeline() as pipe:
        user_id = str(uuid.uuid4())
        pipe.hset(f"user_id:{user_id}", "credit", 0)
        pipe.execute()

    data = {"user_id": user_id}

    return data, 200


@app.get('/find_user/<user_id>')
def find_user(user_id: str):
    user_credit = int(db.hget(f"user_id:{user_id}", "credit").decode("utf-8"))
    return jsonify({"user_id": user_id, "credit": user_credit})


@app.post('/add_funds/<user_id>/<amount>')
def add_credit(user_id: str, amount: int):
    amount = round(float(amount))
    db.hincrby(f"user_id:{user_id}", "credit", amount)
    return jsonify({"done": True})


@app.post('/pay/<user_id>/<order_id>/<amount>')
def remove_credit(user_id: str, order_id: str, amount: int):
    response = make_response("")
    with db.pipeline() as pipe:
        amount = int(amount)
        pipe.hget(f'user_id:{user_id}', 'credit')
        credit = int(pipe.execute()[0].decode('utf-8'))
        if credit < amount:
            response.status_code = 400
            return response
        credit -= amount
        pipe.hset(f'user_id:{user_id}', 'credit', credit)
        result = pipe.execute()

    response.status_code = 200
    return response

@app.post('/cancel/<user_id>/<order_id>')
def cancel_payment(user_id: str, order_id: str):
    response = make_response("")
    with db.pipeline() as pipe:
        pipe.hget(f'order_id:{order_id}', 'paid')
        status = pipe.execute()[0].decode('utf-8')
        if status == 1:
            pipe.hset(f'order_id:{order_id}', 'paid', 0)
            result = pipe.execute()
            response.status_code = 200
            return response
        else:
            response.status_code = 400
    
    # return failure if we try to cancel payment for order which is not yet paid ?
    return response

@app.post('/status/<user_id>/<order_id>')
def payment_status(user_id: str, order_id: str):
    status = db.hget(f'order_id:{order_id}', 'paid').decode('utf-8')
    return jsonify({"paid": status})
