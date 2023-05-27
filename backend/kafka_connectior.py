from confluent_kafka import Producer, Consumer
from uuid import uuid4
from .connector import Connector


class KafkaConnector(Connector):

    def __init__(self, bootstrap_servers, group_id, topic):
        super().__init__()
        self.type = "Eventbus Connector"

        if not group_id:
            group_id = uuid4()

        consumer_conf = {
            'bootstrap.servers': bootstrap_servers,
            'group.id': group_id,
            'auto.offset.reset': 'earliest'
        }

        self.producer = Producer({'bootstrap.servers': bootstrap_servers})
        self.consumer = Consumer(consumer_conf)

        self.consumer.subscribe([topic])

    def payment_create_user(self, payload):
        payload['message_type'] = "create_user"

        self.producer.produce('payment-worker', payload.encode('utf-8'))
        self.producer.flush()

    def payment_find_user(self, payload):
        payload['message_type'] = "find_user"

        self.producer.produce('payment-worker', payload.encode('utf-8'))
        self.producer.flush()

    def payment_pay(self, payload):
        payload['message_type'] = "pay"

        self.producer.produce('payment-worker', payload.encode('utf-8'))
        self.producer.flush()

    def payment_cancel(self, payload):
        payload['message_type'] = "cancel"

        self.producer.produce('payment-worker', payload.encode('utf-8'))
        self.producer.flush()

    def payment_status(self, payload):
        payload['message_type'] = "status"

        self.producer.produce('payment-worker', payload.encode('utf-8'))
        self.producer.flush()

    def payment_add_funds(self, payload):
        payload['message_type'] = "add_funds"

        self.producer.produce('payment-worker', payload.encode('utf-8'))
        self.producer.flush()

    def stock_find(self, payload):
        payload['message_type'] = "find"

        self.producer.produce('stock-worker', payload.encode('utf-8'))
        self.producer.flush()

    def stock_add(self, payload):
        payload['message_type'] = "add"

        self.producer.produce('stock-worker', payload.encode('utf-8'))
        self.producer.flush()

    def stock_subtract(self, payload):
        payload['message_type'] = "subtract"

        self.producer.produce('stock-worker', payload.encode('utf-8'))
        self.producer.flush()

    def stock_item_create(self, payload):
        payload['message_type'] = "item_create"

        self.producer.produce('stock-worker', payload.encode('utf-8'))
        self.producer.flush()

    def order_create_user(self, payload):
        payload['message_type'] = "create_user"

        self.producer.produce('order-worker', payload.encode('utf-8'))
        self.producer.flush()

    def order_remove(self, payload):
        payload['message_type'] = "remove"

        self.producer.produce('order-worker', payload.encode('utf-8'))
        self.producer.flush()

    def order_addItem(self, payload):
        payload['message_type'] = "addItem"

        self.producer.produce('order-worker', payload.encode('utf-8'))
        self.producer.flush()

    def order_removeItem(self, payload):
        payload['message_type'] = "removeItem"

        self.producer.produce('order-worker', payload.encode('utf-8'))
        self.producer.flush()

    def order_find(self, payload):
        payload['message_type'] = "find"

        self.producer.produce('order-worker', payload.encode('utf-8'))
        self.producer.flush()

    def order_checkout(self, payload):
        payload['message_type'] = "checkout"

        self.producer.produce('order-worker', payload.encode('utf-8'))
        self.producer.flush()

    def deliver_response(self, topic, payload):
        self.producer.produce(topic, payload.encode('utf-8'))
        self.producer.flush()
