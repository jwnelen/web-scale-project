import time
import unittest
from threading import Thread

import utils as tu


class TestMicroservices(unittest.TestCase):

    def stock_stress(self):
        start = time.time()
        for i in range(2):
            item = tu.create_item(i)
            tu.find_item(item['item_id'])
        end = time.time()
        print(f"DONE {end - start}")

    def test_find_item(self):
        item: dict = tu.create_item(2.3)
        print(item)
        item_id: str = item['item_id']
        item: dict = tu.find_item(item_id)
        print(item)

    def test_create(self):
        item: dict = tu.create_item(2.3)
        print(item)

    def test_create_item(self):
        for i in range(12):
            Thread(target=self.stock_stress).start()

    def test_stock(self):
        # Test /stock/item/create/<price>
        item: dict = tu.create_item(5)
        print(item)
        self.assertTrue('item_id' in item)

        item_id: str = item['item_id']
        print(item_id)
        # Test /stock/find/<item_id>
        item: dict = tu.find_item(item_id)
        print(item)
        self.assertEqual(item['price'], 5)
        self.assertEqual(item['stock'], 0)

        # Test /stock/add/<item_id>/<number>
        add_stock_response = tu.add_stock(item_id, 50)
        print(add_stock_response)
        self.assertTrue(200 <= int(add_stock_response) < 300)

        stock_after_add: int = tu.find_item(item_id)['stock']
        print(stock_after_add)
        self.assertEqual(stock_after_add, 50)

        # Test /stock/subtract/<item_id>/<number>        
        over_subtract_stock_response = tu.subtract_stock(item_id, 200)
        print(over_subtract_stock_response)
        self.assertTrue(tu.status_code_is_failure(int(over_subtract_stock_response)))

        subtract_stock_response = tu.subtract_stock(item_id, 15)
        print(subtract_stock_response)
        self.assertTrue(tu.status_code_is_success(int(subtract_stock_response)))

        stock_after_subtract: int = tu.find_item(item_id)['stock']
        print(stock_after_subtract)
        self.assertEqual(stock_after_subtract, 35)

    def payment_stress(self):
        start = time.time()
        for i in range(50):
            user: dict = tu.create_user()
            data: dict = tu.find_user(user['user_id'])
        end = time.time()
        print(f"DONE {end - start}")

    def test_create_user(self):
        for i in range(10):
            Thread(target=self.payment_stress).start()

    def test_user(self):
        user: dict = tu.create_user()
        print(user)

    def test_find_user(self):
        user: dict = tu.create_user()
        data: dict = tu.find_user(user['user_id'])
        print(data)

    def test_add_credit(self):
        user: dict = tu.create_user()
        user_id: str = user['user_id']
        add_credit_response = tu.add_credit_to_user(user_id, 15)
        print(add_credit_response)
        data: dict = tu.find_user(user['user_id'])
        print(data)
        add_credit_response = tu.add_credit_to_user(user_id, -3)
        data: dict = tu.find_user(user['user_id'])
        print(data)

    def test_payment(self):
        # Test /payment/pay/<user_id>/<order_id>
        user: dict = tu.create_user()
        print(user)
        self.assertTrue('user_id' in user)

        user_id: str = user['user_id']
        print(user_id)
        # Test /users/credit/add/<user_id>/<amount>
        add_credit_response = tu.add_credit_to_user(user_id, 15)
        print(add_credit_response)
        self.assertTrue(tu.status_code_is_success(add_credit_response))

        # add item to the stock service
        item: dict = tu.create_item(5)
        print(item)
        self.assertTrue('item_id' in item)

        item_id: str = item['item_id']
        print(item_id)
        add_stock_response = tu.add_stock(item_id, 50)
        print(add_stock_response)
        self.assertTrue(tu.status_code_is_success(add_stock_response))

        # create order in the order service and add item to the order
        order: dict = tu.create_order(user_id)
        print(order)
        self.assertTrue('order_id' in order)

        order_id: str = order['order_id']
        print(order_id)
        add_item_response = tu.add_item_to_order(order_id, item_id)
        print(add_item_response)
        self.assertTrue(tu.status_code_is_success(add_item_response))

        add_item_response = tu.add_item_to_order(order_id, item_id)
        print(add_item_response)
        self.assertTrue(tu.status_code_is_success(add_item_response))
        add_item_response = tu.add_item_to_order(order_id, item_id)
        print(add_item_response)
        self.assertTrue(tu.status_code_is_success(add_item_response))

        payment_response = tu.payment_pay(user_id, order_id, 10)
        print(payment_response)
        self.assertTrue(tu.status_code_is_success(payment_response))

        credit_after_payment: int = tu.find_user(user_id)['credit']
        print(credit_after_payment)
        self.assertEqual(credit_after_payment, 5)

    def test_order(self):
        # Test /payment/pay/<user_id>/<order_id>
        user: dict = tu.create_user()
        self.assertTrue('user_id' in user)

        user_id: str = user['user_id']

        # create order in the order service and add item to the order
        order: dict = tu.create_order(user_id)
        self.assertTrue('order_id' in order)

        order_id: str = order['order_id']

        # add item to the stock service
        item1: dict = tu.create_item(5)
        self.assertTrue('item_id' in item1)
        item_id1: str = item1['item_id']
        add_stock_response = tu.add_stock(item_id1, 15)
        self.assertTrue(tu.status_code_is_success(add_stock_response))

        # add item to the stock service
        item2: dict = tu.create_item(5)
        self.assertTrue('item_id' in item2)
        item_id2: str = item2['item_id']
        add_stock_response = tu.add_stock(item_id2, 1)
        self.assertTrue(tu.status_code_is_success(add_stock_response))

        add_item_response = tu.add_item_to_order(order_id, item_id1)
        self.assertTrue(tu.status_code_is_success(add_item_response))

        add_item_response = tu.add_item_to_order(order_id, item_id2)
        self.assertTrue(tu.status_code_is_success(add_item_response))

        subtract_stock_response = tu.subtract_stock(item_id2, 1)
        self.assertTrue(tu.status_code_is_success(subtract_stock_response))

        checkout_response = tu.checkout_order(order_id).status_code
        self.assertTrue(tu.status_code_is_failure(checkout_response))

        stock_after_subtract: int = tu.find_item(item_id1)['stock']
        self.assertEqual(stock_after_subtract, 15)

        add_stock_response = tu.add_stock(item_id2, 15)
        self.assertTrue(tu.status_code_is_success(int(add_stock_response)))

        credit_after_payment: int = tu.find_user(user_id)['credit']
        self.assertEqual(credit_after_payment, 0)

        checkout_response = tu.checkout_order(order_id).status_code
        self.assertTrue(tu.status_code_is_failure(checkout_response))

        add_credit_response = tu.add_credit_to_user(user_id, 15)
        self.assertTrue(tu.status_code_is_success(int(add_credit_response)))

        credit: int = tu.find_user(user_id)['credit']
        self.assertEqual(credit, 15)

        stock: int = tu.find_item(item_id1)['stock']
        self.assertEqual(stock, 15)

        checkout_response = tu.checkout_order(order_id).status_code
        self.assertTrue(tu.status_code_is_success(checkout_response))

        stock_after_subtract: int = tu.find_item(item_id1)['stock']
        self.assertEqual(stock_after_subtract, 14)

        credit: int = tu.find_user(user_id)['credit']
        self.assertEqual(credit, 5)


if __name__ == '__main__':
    unittest.main()
