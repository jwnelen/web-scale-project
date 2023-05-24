import requests

from common.connector import Connector


class K8sConnector(Connector):

    def __init__(self):
        super().__init__()
        self.type = "K8s Connector"

    def payment_find_user(self, user_id):
        return requests.get(f"http://user-service:5000/find_user/{user_id}").json()

    def payment_pay(self, user_id, order_id, amount):
        return requests.post(f"http://user-service:5000/pay/{user_id}/{order_id}/{amount}")

    def payment_cancel(self, user_id, order_id):
        return requests.post(f"http://user-service:5000/cancel/{user_id}/{order_id}")

    def payment_status(self, user_id, order_id):
        return requests.post(f"http://user-service:5000/status/{user_id}/{order_id}")

    def payment_add_funds(self, user_id, amount):
        return requests.post(f"http://user-service:5000/add_funds/{user_id}/{amount}")

    def stock_find(self, item_id):
        return requests.get(f"http://stock-service:5000/find/{item_id}").json()

    def stock_add(self, item_id, amount):
        return requests.post(f"http://stock-service:5000/add/{item_id}/{amount}")

    def stock_subtract(self, item_id, amount):
        return requests.post(f"http://stock-service:5000/subtract/{item_id}/{amount}")

