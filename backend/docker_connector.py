import requests

from .connector import Connector


class DockerConnector(Connector):


    def __init__(self, gateway):
        super().__init__()
        self.type = "Docker Connector"
        self.gateway = gateway

    def payment_find_user(self, payload):
        user_id = payload['user_id']
        return requests.get(f"{self.gateway}/payment/find_user/{user_id}").json()

    def payment_pay(self, payload):
        user_id = payload['user_id']
        order_id = payload['order_id']
        amount = payload['amount']
        return requests.post(f"{self.gateway}/payment/pay/{user_id}/{order_id}/{amount}")

    def payment_cancel(self, payload):
        user_id = payload['user_id']
        order_id = payload['order_id']
        return requests.post(f"{self.gateway}/payment/cancel/{user_id}/{order_id}")

    def payment_status(self, payload):
        user_id = payload['user_id']
        order_id = payload['order_id']
        return requests.get(f"{self.gateway}/payment/status/{user_id}/{order_id}").json()

    def payment_add_funds(self, payload):
        user_id = payload['user_id']
        amount = payload['amount']
        return requests.post(f"{self.gateway}/payment/add_funds/{user_id}/{amount}")

    def payment_create_user(self, payload):
        pass

    def stock_find(self, payload):
        item_id = payload['item_id']
        return requests.get(f"{self.gateway}/stock/find/{item_id}").json()

    def stock_add(self, payload):
        item_id = payload['item_id']
        amount = payload['amount']
        return requests.post(f"{self.gateway}/stock/add/{item_id}/{amount}")

    def stock_subtract(self, payload):
        item_id = payload['item_id']
        amount = payload['amount']
        return requests.post(f"{self.gateway}/stock/subtract/{item_id}/{amount}")

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
