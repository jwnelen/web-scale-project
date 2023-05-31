from abc import abstractmethod, ABC


class Connector(ABC):
    def __init__(self):
        self.type = "Abstract Connector Class"

    @abstractmethod
    def payment_find_user(self, payload):
        pass

    @abstractmethod
    def payment_create_user(self, payload):
        pass

    @abstractmethod
    def payment_status(self, payload):
        pass

    @abstractmethod
    def payment_add_funds(self, payload):
        pass

    @abstractmethod
    def stock_item_create(self, payload):
        pass

    @abstractmethod
    def stock_find(self, payload):
        pass

    @abstractmethod
    def stock_add(self, payload):
        pass

    @abstractmethod
    def stock_subtract(self, payload):
        pass

    @abstractmethod
    def order_create_user(self, payload):
        pass

    @abstractmethod
    def order_remove(self, payload):
        pass

    @abstractmethod
    def order_addItem(self, payload):
        pass

    @abstractmethod
    def order_removeItem(self, payload):
        pass

    @abstractmethod
    def order_find(self, payload):
        pass

    @abstractmethod
    def order_checkout(self, payload):
        pass
