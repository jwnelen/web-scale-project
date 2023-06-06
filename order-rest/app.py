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
        'order-rest',
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


@app.post('/orders/create/{user_id}')
async def create(user_id):
    destination = f'order-{str(uuid4())}'

    payload = {'data': {'user_id': user_id},
               'destination': destination}

    connector = KafkaRESTConnector()

    response = await get_response(destination, connector.order_create_user, payload)

    if not response:
        return JSONResponse(content={}, status_code=400)

    return JSONResponse(content=response, status_code=200)


@app.delete('/orders/remove/{order_id}')
async def remove(order_id):
    destination = f'order-{str(uuid4())}'

    payload = {'data': {'order_id': order_id},
               'destination': destination}

    connector = KafkaRESTConnector()

    response = await get_response(destination, connector.order_remove, payload)

    if not response['success']:
        return JSONResponse(content={}, status_code=400)

    return JSONResponse(content={}, status_code=200)


@app.post('/orders/addItem/{order_id}/{item_id}')
async def add_item(order_id, item_id):
    destination = f'order-{str(uuid4())}'

    payload = {'data': {'order_id': order_id,
                        'item_id': item_id},
               'destination': destination}

    connector = KafkaRESTConnector()

    response = await get_response(destination, connector.order_addItem, payload)

    if not response['success']:
        return JSONResponse(content={}, status_code=400)

    return JSONResponse(content={}, status_code=200)


@app.delete('/orders/removeItem/{order_id}/{item_id}')
async def remove_item(order_id, item_id):
    destination = f'order-{str(uuid4())}'

    payload = {'data': {'order_id': order_id,
                        'item_id': item_id},
               'destination': destination}

    connector = KafkaRESTConnector()

    response = await get_response(destination, connector.order_removeItem, payload)

    if not response['success']:
        return JSONResponse(content={}, status_code=400)

    return JSONResponse(content={}, status_code=200)


@app.get('/orders/find/{order_id}')
async def find(order_id):
    destination = f'order-{str(uuid4())}'

    payload = {'data': {'order_id': order_id},
               'destination': destination}

    connector = KafkaRESTConnector()

    response = await get_response(destination, connector.order_find, payload)

    if not response:
        return JSONResponse(content={}, status_code=400)

    return JSONResponse(content=response, status_code=200)


@app.post('/orders/checkout/{order_id}')
async def checkout(order_id):
    destination = f'order-{str(uuid4())}'

    payload = {'data': {'order_id': order_id},
               'destination': destination}

    connector = KafkaRESTConnector()

    response = await get_response(destination, connector.order_checkout, payload)

    if not response['success']:
        return JSONResponse(content=response, status_code=400)

    return JSONResponse(content=response, status_code=200)

