import json
import os
import random

from uuid import uuid4
from aiokafka import AIOKafkaConsumer
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from backend.kafka_rest_connectior import KafkaRESTConnector

app = FastAPI()


async def get_response(destination, send_func, payload):
    consumer = AIOKafkaConsumer(
        'payment-rest',
        bootstrap_servers=os.environ['BOOTSTRAP_SERVERS'],
        group_id=str(random.randint(1, 10000000)))

    await consumer.start()
    await send_func(payload)
    try:
        async for message in consumer:
            payload = json.loads(message.value.decode('utf-8'))
            msg_destination = payload['destination']

            if msg_destination == destination:
                response = payload['data']
                return response
    finally:
        await consumer.stop()


@app.post('/payment/create_user')
async def create_user():
    destination = f'payment-{str(uuid4())}'

    payload = {'data': {},
               'destination': destination}

    connector = KafkaRESTConnector()

    response = await get_response(destination, connector.payment_create_user, payload)

    if not response:
        return JSONResponse(content={}, status_code=400)

    return JSONResponse(content=response, status_code=200)


@app.get('/payment/find_user/{user_id}')
async def find_user(user_id: str):
    destination = f'payment-{str(uuid4())}'

    payload = {'data': {'user_id': user_id},
               'destination': destination}

    connector = KafkaRESTConnector()

    response = await get_response(destination, connector.payment_find_user, payload)

    if not response:
        return JSONResponse(content={}, status_code=400)

    return JSONResponse(content=response, status_code=200)


@app.post('/payment/add_funds/{user_id}/{amount}')
async def add_funds(user_id: str, amount: float):
    destination = f'payment-{str(uuid4())}'

    payload = {'data': {'user_id': user_id,
                        'amount': float(amount)},
               'destination': destination}

    connector = KafkaRESTConnector()

    response = await get_response(destination, connector.payment_add_funds, payload)

    if not response['done']:
        return JSONResponse(content=response, status_code=400)

    return JSONResponse(content=response, status_code=200)


@app.post('/payment/pay/{user_id}/{order_id}/{amount}')
async def pay(user_id: str, order_id: str, amount: float):
    destination = f'payment-{str(uuid4())}'

    payload = {'data': {'user_id': user_id,
                        'order_id': order_id,
                        'amount': float(amount)},
               'destination': destination}

    connector = KafkaRESTConnector()

    response = await get_response(destination, connector.payment_pay, payload)

    if not response['success']:
        return JSONResponse(content={}, status_code=400)

    return JSONResponse(content={}, status_code=200)


@app.get('/payment/status/{user_id}/{order_id}')
async def status(user_id: str, order_id: str):
    destination = f'payment-{str(uuid4())}'

    payload = {'data': {'user_id': user_id,
                        'order_id': order_id},
               'destination': destination}

    connector = KafkaRESTConnector()

    response = await get_response(destination, connector.payment_status, payload)

    if not response['paid']:
        return JSONResponse(content=response, status_code=400)

    return JSONResponse(content=response, status_code=200)
