from kafka import KafkaProducer, KafkaConsumer
from .connector import Connector


class Eventbus_Connector(Connector):

    def __init__(self, bootstrap_servers):
        super().__init__()
        self.type = "Eventbus Connector"
        self.bootstrap_servers = bootstrap_servers
        self.producer = KafkaProducer(bootstrap_servers=self.bootstrap_servers)
        self.consumer = KafkaConsumer(bootstrap_servers=self.bootstrap_servers)

    def payment_create_user(self):
        pass

    def payment_find_user(self, user_id):
        pass

    def payment_pay(self, user_id, order_id, amount):
        data = {
            "message_type": "pay",
            "user_id": user_id,
            "order_id": order_id,
            "amount": amount
        }

        self.producer.send('payment', value=data)
        self.producer.flush()

    def payment_cancel(self, user_id, order_id):
        pass

    def payment_status(self, user_id, order_id):
        pass

    def payment_add_funds(self, user_id, amount):
        pass

    def stock_find(self, item_id):
        pass

    def stock_add(self, item_id, amount):
        pass

    def stock_subtract(self, item_id, amount):
        pass

    def stock_item_create(self, price):
        pass

    def order_create_user(self):
        pass

    def order_remove(self, order_id):
        pass

    def order_addItem(self, order_id, item_id):
        pass

    def order_removeItem(self, order_id, item_id):
        pass

    def order_find(self, order_id):
        pass

    def order_checkout(self, order_id):
        pass
