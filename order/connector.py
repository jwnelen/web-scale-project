from abc import abstractmethod, ABC


class Connector(ABC):
    def __init__(self):
        self.type = "Abstract Connector Class"

    @abstractmethod
    def payment_find_user(self, user_id):
        pass

    @abstractmethod
    def payment_pay(self, user_id, order_id, amount):
        pass

    @abstractmethod
    def payment_cancel(self, user_id, order_id):
        pass

    @abstractmethod
    def payment_status(self, user_id, order_id):
        pass

    @abstractmethod
    def payment_add_funds(self, user_id, amount):
        pass

    @abstractmethod
    def stock_find(self, item_id):
        pass

    @abstractmethod
    def stock_add(self, item_id, amount):
        pass

    @abstractmethod
    def stock_subtract(self, item_id, amount):
        pass
