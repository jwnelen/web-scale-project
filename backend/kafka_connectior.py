from kafka import KafkaProducer, KafkaConsumer
from uuid import uuid4
from .connector import Connector


class KafkaConnector(Connector):

    def __init__(self, bootstrap_servers, group_id, topic):
        super().__init__()
        self.type = "Eventbus Connector"

        if not group_id:
            group_id = uuid4()

        self.producer = KafkaProducer(bootstrap_servers=bootstrap_servers, api_version=(0, 10, 2))
        self.consumer = KafkaConsumer(group_id=group_id, bootstrap_servers=bootstrap_servers)

        self.consumer.subscribe(topic)

    def payment_create_user(self, payload):
        payload['message_type'] = "create_user"

        self.producer.send('payment-worker', payload.encode('utf-8'))
        self.producer.flush()

    def payment_find_user(self, payload):
        payload['message_type'] = "find_user"

        self.producer.send('payment-worker', payload.encode('utf-8'))
        self.producer.flush()

    def payment_pay(self, payload):
        payload['message_type'] = "pay"

        self.producer.send('payment-worker', payload.encode('utf-8'))
        self.producer.flush()

    def payment_cancel(self, payload):
        payload['message_type'] = "cancel"

        self.producer.send('payment-worker', payload.encode('utf-8'))
        self.producer.flush()

    def payment_status(self, payload):
        payload['message_type'] = "status"

        self.producer.send('payment-worker', payload.encode('utf-8'))
        self.producer.flush()

    def payment_add_funds(self, payload):
        payload['message_type'] = "add_funds"

        self.producer.send('payment-worker', payload.encode('utf-8'))
        self.producer.flush()

    def stock_find(self, payload):
        payload['message_type'] = "find"

        self.producer.send('stock-worker', payload.encode('utf-8'))
        self.producer.flush()

    def stock_add(self, payload):
        payload['message_type'] = "add"

        self.producer.send('stock-worker', payload.encode('utf-8'))
        self.producer.flush()

    def stock_subtract(self, payload):
        payload['message_type'] = "subtract"

        self.producer.send('stock-worker', payload.encode('utf-8'))
        self.producer.flush()

    def stock_item_create(self, payload):
        payload['message_type'] = "item_create"

        self.producer.send('stock-worker', payload.encode('utf-8'))
        self.producer.flush()

    def order_create_user(self, payload):
        payload['message_type'] = "create_user"

        self.producer.send('order-worker', payload.encode('utf-8'))
        self.producer.flush()

    def order_remove(self, payload):
        payload['message_type'] = "remove"

        self.producer.send('order-worker', payload.encode('utf-8'))
        self.producer.flush()

    def order_addItem(self, payload):
        payload['message_type'] = "addItem"

        self.producer.send('order-worker', payload.encode('utf-8'))
        self.producer.flush()

    def order_removeItem(self, payload):
        payload['message_type'] = "removeItem"

        self.producer.send('order-worker', payload.encode('utf-8'))
        self.producer.flush()

    def order_find(self, payload):
        payload['message_type'] = "find"

        self.producer.send('order-worker', payload.encode('utf-8'))
        self.producer.flush()

    def order_checkout(self, payload):
        payload['message_type'] = "checkout"

        self.producer.send('order-worker', payload.encode('utf-8'))
        self.producer.flush()

    def deliver_response(self, topic, payload):
        self.producer.send(topic, payload.encode('utf-8'))
        self.producer.flush()
