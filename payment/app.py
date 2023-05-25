import os
import atexit
from flask import Flask, jsonify, make_response
import redis
import uuid


app = Flask("payment-service")
gateway_url = ""

if 'GATEWAY_URL' in os.environ:
    gateway_url = os.environ['GATEWAY_URL']

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
    return make_response(jsonify(data), 200)


@app.get('/find_user/<user_id>')
def find_user(user_id: str):
    user_credit = db.hget(f"user_id:{user_id}", "credit")
    if not user_credit:
        return {}, 400
    user_credit = int(user_credit.decode('utf-8'))
    data = {"user_id": user_id, "credit": user_credit}
    return make_response(jsonify(data), 200)


@app.post('/add_funds/<user_id>/<amount>')
def add_credit(user_id: str, amount: int):
    amount = round(float(amount))
    data = {'done': False}
    with db.pipeline() as pipe:
        pipe.exists(f'user_id:{user_id}')
        exists = pipe.execute()[0]
        if exists:
            pipe.hincrby(f"user_id:{user_id}", "credit", amount)
            pipe.execute()
            data['done'] = True
            return make_response(jsonify(data), 200)
        else:
            return make_response(jsonify(data), 400)


@app.post('/pay/<user_id>/<order_id>/<amount>')
def remove_credit(user_id: str, order_id: str, amount: int):
    amount = int(amount)
    with db.pipeline() as pipe:
        pipe.hget(f'user_id:{user_id}', 'credit')
        credit = int(pipe.execute()[0].decode('utf-8'))
        if credit < amount:
            return make_response(jsonify({}), 400)
        credit -= amount
        pipe.hset(f'user_id:{user_id}', 'credit', credit)
        pipe.execute()

    return make_response(jsonify({}), 400)

@app.post('/cancel/<user_id>/<order_id>')
def cancel_payment(user_id: str, order_id: str):
    with db.pipeline() as pipe:
        pipe.hget(f'order_id:{order_id}', 'paid')
        status = pipe.execute()[0].decode('utf-8')
        if status == 1:
            pipe.hset(f'order_id:{order_id}', 'paid', 0)
            pipe.execute()
            return make_response(jsonify({}), 200)
    
    # return failure if we try to cancel payment for order which is not yet paid ?
    return make_response(jsonify({}), 400)

@app.post('/status/<user_id>/<order_id>')
def payment_status(user_id: str, order_id: str):
    status = db.hget(f'order_id:{order_id}', 'paid').decode('utf-8')
    data = {"paid": status}
    return make_response(jsonify(data), 200)
