import requests

from .connector import Connector


class K8sConnector(Connector):

    def __init__(self):
        super().__init__()
        self.type = "K8s Connector"

    def payment_create_user(self, payload):
        pass

    def payment_find_user(self, payload):
        user_id = payload['user_id']
        return requests.get(f"http://payment-service:5000/find_user/{user_id}").json()

    def payment_pay(self, payload):
        user_id = payload['user_id']
        order_id = payload['order_id']
        amount = payload['amount']
        return requests.post(f"http://payment-service:5000/pay/{user_id}/{order_id}/{amount}")

    def payment_cancel(self, payload):
        user_id = payload['user_id']
        order_id = payload['order_id']
        return requests.post(f"http://payment-service:5000/cancel/{user_id}/{order_id}")

    def payment_status(self, payload):
        user_id = payload['user_id']
        order_id = payload['order_id']
        return requests.get(f"http://payment-service:5000/status/{user_id}/{order_id}").json()

    def payment_add_funds(self, payload):
        user_id = payload['user_id']
        amount = payload['amount']
        return requests.post(f"http://payment-service:5000/add_funds/{user_id}/{amount}")

    def stock_find(self, payload):
        item_id = payload['item_id']
        return requests.get(f"http://stock-service:5000/find/{item_id}").json()

    def stock_add(self, payload):
        item_id = payload['item_id']
        amount = payload['amount']
        return requests.post(f"http://stock-service:5000/add/{item_id}/{amount}")

    def stock_subtract(self, payload):
        item_id = payload['item_id']
        amount = payload['amount']
        return requests.post(f"http://stock-service:5000/subtract/{item_id}/{amount}")

    def stock_item_create(self, payload):
        pass

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
