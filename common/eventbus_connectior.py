from common.connector import Connector


class Eventbus_Connector(Connector):

    def __init__(self):
        super().__init__()
        self.type = "Eventbus Connector"

    def payment_find_user(self, user_id):
        pass

    def payment_pay(self, user_id, order_id, amount):
        pass

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
