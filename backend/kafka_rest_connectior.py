import json
import os
import logging

from aiokafka import AIOKafkaProducer
from .connector import Connector

logging.basicConfig(level=logging.INFO)


class KafkaRESTConnector(Connector):

    def __init__(self):
        super().__init__()
        self.type = "Eventbus Connector"
        self.bootstrap_servers = os.environ['BOOTSTRAP_SERVERS']

    async def payment_create_user(self, payload):
        producer = AIOKafkaProducer(bootstrap_servers=self.bootstrap_servers,
                                    api_version="0.10.2")
        payload['message_type'] = "create_user"
        await producer.start()
        try:
            await producer.send_and_wait('payment-worker', json.dumps(payload).encode('utf-8'))
        finally:
            await producer.stop()

    async def payment_find_user(self, payload):
        producer = AIOKafkaProducer(bootstrap_servers=self.bootstrap_servers,
                                    api_version="0.10.2")
        payload['message_type'] = "find_user"
        await producer.start()
        try:
            await producer.send_and_wait('payment-worker', json.dumps(payload).encode('utf-8'))
        finally:
            await producer.stop()

    async def payment_pay(self, payload):
        producer = AIOKafkaProducer(bootstrap_servers=self.bootstrap_servers,
                                    api_version="0.10.2")
        payload['message_type'] = "pay"
        await producer.start()
        try:
            await producer.send_and_wait('payment-worker', json.dumps(payload).encode('utf-8'))
        finally:
            await producer.stop()

    async def payment_status(self, payload):
        producer = AIOKafkaProducer(bootstrap_servers=self.bootstrap_servers,
                                    api_version="0.10.2")
        payload['message_type'] = "status"
        await producer.start()
        try:
            await producer.send_and_wait('payment-worker', json.dumps(payload).encode('utf-8'))
        finally:
            await producer.stop()

    async def payment_add_funds(self, payload):
        producer = AIOKafkaProducer(bootstrap_servers=self.bootstrap_servers,
                                    api_version="0.10.2")
        payload['message_type'] = "add_funds"
        await producer.start()
        try:
            await producer.send_and_wait('payment-worker', json.dumps(payload).encode('utf-8'))
        finally:
            await producer.stop()

    async def stock_find(self, payload):
        producer = AIOKafkaProducer(bootstrap_servers=self.bootstrap_servers,
                                    api_version="0.10.2")
        payload['message_type'] = "find"
        await producer.start()
        try:
            await producer.send_and_wait('stock-worker', json.dumps(payload).encode('utf-8'))
        finally:
            await producer.stop()

    async def stock_add(self, payload):
        producer = AIOKafkaProducer(bootstrap_servers=self.bootstrap_servers,
                                    api_version="0.10.2")
        payload['message_type'] = "add"
        await producer.start()
        try:
            await producer.send_and_wait('stock-worker', json.dumps(payload).encode('utf-8'))
        finally:
            await producer.stop()

    async def stock_subtract(self, payload):
        producer = AIOKafkaProducer(bootstrap_servers=self.bootstrap_servers,
                                    api_version="0.10.2")
        payload['message_type'] = "subtract"
        await producer.start()
        try:
            await producer.send_and_wait('stock-worker', json.dumps(payload).encode('utf-8'))
        finally:
            await producer.stop()

    async def stock_item_create(self, payload):
        producer = AIOKafkaProducer(bootstrap_servers=self.bootstrap_servers,
                                    api_version="0.10.2")
        payload['message_type'] = "item_create"
        await producer.start()
        try:
            await producer.send_and_wait('stock-worker', json.dumps(payload).encode('utf-8'))
        finally:
            await producer.stop()

    async def order_create_user(self, payload):
        producer = AIOKafkaProducer(bootstrap_servers=self.bootstrap_servers,
                                    api_version="0.10.2")
        payload['message_type'] = "create_user"
        await producer.start()
        try:
            await producer.send_and_wait('order-worker', json.dumps(payload).encode('utf-8'))
        finally:
            await producer.stop()

    async def order_remove(self, payload):
        producer = AIOKafkaProducer(bootstrap_servers=self.bootstrap_servers,
                                    api_version="0.10.2")
        payload['message_type'] = "remove"
        await producer.start()
        try:
            await producer.send_and_wait('order-worker', json.dumps(payload).encode('utf-8'))
        finally:
            await producer.stop()

    async def order_addItem(self, payload):
        producer = AIOKafkaProducer(bootstrap_servers=self.bootstrap_servers,
                                    api_version="0.10.2")
        payload['message_type'] = "addItem"
        await producer.start()
        try:
            await producer.send_and_wait('order-worker', json.dumps(payload).encode('utf-8'))
        finally:
            await producer.stop()

    async def order_removeItem(self, payload):
        producer = AIOKafkaProducer(bootstrap_servers=self.bootstrap_servers,
                                    api_version="0.10.2")
        payload['message_type'] = "removeItem"
        await producer.start()
        try:
            await producer.send_and_wait('order-worker', json.dumps(payload).encode('utf-8'))
        finally:
            await producer.stop()

    async def order_find(self, payload):
        producer = AIOKafkaProducer(bootstrap_servers=self.bootstrap_servers,
                                    api_version="0.10.2")
        payload['message_type'] = "find"
        await producer.start()
        try:
            await producer.send_and_wait('order-worker', json.dumps(payload).encode('utf-8'))
        finally:
            await producer.stop()

    async def order_checkout(self, payload):
        producer = AIOKafkaProducer(bootstrap_servers=self.bootstrap_servers,
                                    api_version="0.10.2")
        payload['message_type'] = "checkout"
        await producer.start()
        try:
            await producer.send_and_wait('order-worker', json.dumps(payload).encode('utf-8'))
        finally:
            await producer.stop()
