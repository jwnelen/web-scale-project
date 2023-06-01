from google.cloud import spanner
from google.cloud.spanner_v1.streamed import StreamedResultSet


class SpannerDB:
    def __init__(self):
        instance_id = "spanner-db"
        database_id = "database"

        # Instantiate a client.
        spanner_client = spanner.Client()

        # Get a Cloud Spanner instance by ID.
        self.instance = spanner_client.instance(instance_id)
        self.database = self.instance.database(database_id)

    def create_order(self, order_id, user_id):
        def trans_create_order(transaction):
            transaction.execute_update(
                "INSERT INTO orders (order_id, user_id, paid) "
                f"VALUES ('{order_id}', '{user_id}', false) "
            )

        try:
            self.database.run_in_transaction(trans_create_order)
            data = {"order_id": order_id}
        except Exception as e:
            data = {}

        return data

    def remove_order(self, order_id):
        def trans_remove_order(transaction):
            return transaction.execute_update(
                f"DELETE FROM orders WHERE order_id = '{order_id}' "
            )

        try:
            row_ct = self.database.run_in_transaction(trans_remove_order)
            if row_ct == 1:
                data = {'success': True}
            else:
                data = {'success': False}
        except Exception as e:
            data = {'success': False}

        return data

    def find_order(self, order_id):
        orderItemsQuery = "SELECT * FROM orderItems"

        new_query = f"SELECT * FROM orders AS o " \
                    f"LEFT JOIN ({orderItemsQuery}) AS oi " \
                    f"ON o.order_id = oi.order_id " \
                    f"WHERE o.order_id = '{order_id}'"

        # For a single consistent read, use snapshot
        with self.database.snapshot() as snapshot:
            # Snapshots do not have an execute update method
            results: StreamedResultSet = snapshot.execute_sql(new_query)

            if results is None:
                data = {}
            else:
                items = []
                total_price = 0
                result_list = list(results)
                f = result_list[0]

                for r in result_list:
                    items.append(r[4])
                    total_price += r[6]

                data = {
                    "order_id": f[0],
                    "user_id": f[1],
                    "paid": f[2],
                    "items": items,
                    "total_price": total_price
                }

            return data

    def add_item_to_order(self, order_id, item_id):
        # Check if the order-item pair already exists
        query = f"SELECT * FROM stock WHERE item_id = '{item_id}'"

        with self.database.snapshot() as snapshot:
            result = snapshot.execute_sql(query).one_or_none()

            if result is None:
                return {'success': False}
            else:
                stock_data = {
                    "stock": int(result[2]),
                    "price": float(result[1])
                }

        price = stock_data["price"]

        def adding(transaction):
            finding_query = f"SELECT * FROM orderitems WHERE order_id = '{order_id}' AND item_id = '{item_id}'"
            order_item_combo = transaction.execute_sql(finding_query).one_or_none()
            # Does not exist
            if order_item_combo is None:
                local_res = transaction.execute_sql(
                    f"INSERT INTO orderitems (order_id, item_id, quantity, total_price) "
                    f"VALUES ('{order_id}', '{item_id}', 1, {price}) "
                    f"RETURNING *"
                ).one()
                return {'success': True}

            # Update the current value
            local_res = transaction.execute_sql(
                f"UPDATE orderitems SET quantity = quantity + 1, "
                f"total_price = total_price + {price} "
                f"WHERE order_id = '{order_id}' AND item_id = '{item_id}'"
                f"RETURNING order_id, item_id, quantity, total_price"
            ).one_or_none()

            if local_res is None:
                return {'success': False}


            return {'success': True}

        try:
            data = self.database.run_in_transaction(adding)
        except Exception as e:
            data = {'success': False}

        return data

    def remove_item_from_order(self, order_id, item_id):
        # Check if the order-item pair already exists
        query = f"SELECT * FROM stock WHERE item_id = '{item_id}'"

        with self.database.snapshot() as snapshot:
            result = snapshot.execute_sql(query).one_or_none()

            if result is None:
                return {'success': False}
            else:
                stock_data = {
                    "stock": int(result[2]),
                    "price": float(result[1])
                }

        price = stock_data["price"]

        def removing(transaction):
            finding_query = f"SELECT * FROM orderitems WHERE order_id = '{order_id}' AND item_id = '{item_id}'"
            order_item_combo = transaction.execute_sql(finding_query).one_or_none()
            # Does not exist
            if order_item_combo is None:
                return {'success': False}

            # Only one item left, delete the row
            if order_item_combo[2] == 1:
                local_res = transaction.execute_sql(
                    f"DELETE FROM orderitems WHERE order_id = '{order_id}' AND item_id = '{item_id}' "
                    f"RETURNING order_id, item_id"
                ).one_or_none()

                if local_res is None:
                    return {'success': False}

                return {'success': True}

            # Update the current value
            rows_executed = transaction.execute_sql(
                f"UPDATE orderitems SET quantity = quantity - 1, "
                f"total_price = total_price - {price} "
                f"WHERE order_id = '{order_id}' AND item_id = '{item_id}'"
                f"RETURNING order_id, item_id, quantity, total_price"
            ).one_or_none()

            if rows_executed is None:
                return {'success': False}

            return {'success': True}

        try:
            data = self.database.run_in_transaction(removing)
        except Exception as e:
            data = {'success': False}

        return data

    def checkout(self, order_id):
        def trans_pay_order(transaction):

            finding_query = f"SELECT * FROM orders WHERE order_id = '{order_id}'"
            order = transaction.execute_sql(finding_query).one_or_none()

            if order is None or order[2] is True:
                return {'success': False}

            orderItemsQuery = "SELECT * FROM orderItems"

            query_all_items = f"SELECT * FROM orders AS o " \
                              f"LEFT JOIN ({orderItemsQuery}) AS oi " \
                              f"ON o.order_id = oi.order_id " \
                              f"WHERE o.order_id = '{order_id}'"

            results: StreamedResultSet = transaction.execute_sql(query_all_items)

            if results is None:
                return {'success': False}

            result_list = list(results)
            total_price = sum([float(r[6]) for r in result_list])

            # Check if the user has enough credit
            user_id = result_list[0][1]
            res = transaction.execute_sql(
                f"SELECT credit FROM users WHERE user_id = '{user_id}'"
            ).one_or_none()
            if res is None:
                return {'success': False}
            if float(res[0]) < total_price:
                return {'success': False}

            # For each item, remove the items from the stock
            # There is a check that the item is in stock!!
            for i in range(0, len(result_list)):
                r = result_list[i]
                item_id = r[4]
                quantity = r[5]

                upd = transaction.execute_update(
                    f"UPDATE stock SET amount = amount - {quantity} WHERE item_id = '{item_id}' "
                )

            # Remove Credits
            user_id = result_list[0][1]

            rows_executed = transaction.execute_update(
                f"UPDATE users SET credit = credit - {total_price} WHERE user_id = '{user_id}' "
            )

            # Mark the order as paid - COMMIT
            rows_executed2 = transaction.execute_update(
                f"UPDATE orders SET paid = TRUE WHERE order_id = '{order_id}'"
            )

            return {'success': True}

        try:
            data = self.database.run_in_transaction(trans_pay_order)
        except Exception as e:
            data = {'success': False}

        return data
