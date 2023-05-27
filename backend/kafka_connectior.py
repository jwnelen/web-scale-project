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
        pass

    def payment_find_user(self, payload):
        pass

    def payment_pay(self, payload):
        pass

    def payment_cancel(self, payload):
        pass

    def payment_status(self, payload):
        pass

    def payment_add_funds(self, payload):
        pass

    def stock_find(self, payload):
        pass

    def stock_add(self, payload):
        pass

    def stock_subtract(self, payload):
        pass

    def stock_item_create(self, payload):
        payload['message_type'] = "item_create"

        self.producer.produce('stock', payload.encode('utf-8'))
        self.producer.flush()

    def order_create_user(self, payload):
        pass

    def order_remove(self, payload):
        pass

    def order_addItem(self, payload):
        pass

    def order_removeItem(self, payload):
        pass

    def order_find(self, payload):
        pass

    def order_checkout(self, payload):
        pass

    def deliver_response(self, payload):
        dest = payload['dest']
        data = payload['data']

        self.producer.send(dest, value=data)
        self.producer.flush()
