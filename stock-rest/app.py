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
        'stock-rest',
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


@app.post('/stock/item/create/{price}')
async def item_create(price: float):
    destination = f'stock-{str(uuid4())}'

    payload = {'data': {'price': float(price)},
               'destination': destination}

    connector = KafkaRESTConnector()

    response = await get_response(destination, connector.stock_item_create, payload)

    if not response:
        return JSONResponse(content={}, status_code=400)

    return JSONResponse(content=response, status_code=200)


@app.get('/stock/find/{item_id}')
async def find(item_id: str):
    destination = f'stock-{str(uuid4())}'

    payload = {'data': {'item_id': item_id},
               'destination': destination}

    connector = KafkaRESTConnector()

    response = await get_response(destination, connector.stock_find, payload)

    if not response:
        return JSONResponse(content={}, status_code=400)

    return JSONResponse(content=response, status_code=200)


@app.post('/stock/add/{item_id}/{amount}')
async def add(item_id: str, amount: int):
    destination = f'stock-{str(uuid4())}'

    payload = {'data': {'item_id': item_id,
                        'amount': int(amount)},
               'destination': destination}

    connector = KafkaRESTConnector()

    response = await get_response(destination, connector.stock_add, payload)

    if not response['success']:
        return JSONResponse(content={}, status_code=400)

    return JSONResponse(content={}, status_code=200)


@app.post('/stock/subtract/{item_id}/{amount}')
async def subtract(item_id: str, amount: int):
    destination = f'stock-{str(uuid4())}'

    payload = {'data': {'item_id': item_id,
                        'amount': int(amount)},
               'destination': destination}

    connector = KafkaRESTConnector()

    response = await get_response(destination, connector.stock_subtract, payload)

    if not response['success']:
        return JSONResponse(content={}, status_code=400)

    return JSONResponse(content={}, status_code=200)
