from uuid import uuid4

from google.api_core.exceptions import FailedPrecondition
from google.cloud import spanner
from google.cloud.spanner_v1.streamed import StreamedResultSet


class OrderDatabase:
    def __init__(self):
        instance_id = "spanner-db"
        database_id = "database"

        # Instantiate a client.
        spanner_client = spanner.Client()

        # Get a Cloud Spanner instance by ID.
        self.instance = spanner_client.instance(instance_id)
        self.database = self.instance.database(database_id)

    # DML, f: execute_update, rows affected, visible to subsequent reads or SQL, f: execute_sql, result set
    # Changes you make using DML statements are visible to subsequent statements in the same transaction

    # Mutations
    # This is different from using mutations, where changes are not visible in any reads (including reads done in the same transaction) until the transaction commits.

    def create_order(self, user_id):
        u_id = str(uuid4())

        def trans_create_order(transaction):
            transaction.execute_sql(
                "INSERT INTO orders (order_id, user_id, paid) "
                f"VALUES ('{u_id}', '{user_id}', false) "
            )

        try:
            self.database.run_in_transaction(trans_create_order)
        except FailedPrecondition:
            return {"error": "user_id does not exist"}
        except Exception as e:
            return {"error": str(e)}

        return {"order_id": u_id}

    def remove_order(self, order_id):
        def trans_remove_order(transaction):
            return transaction.execute_update(
                f"DELETE FROM orders WHERE order_id = '{order_id}' "
            )

        try:
            r = self.database.run_in_transaction(trans_remove_order)
        except Exception as e:
            return {"error": str(e)}
        return {"rows_affected": r}

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
                return {"error": "order does not exist"}

            items = []
            total_price = 0
            result_list = list(results)
            f = result_list[0]

            for r in result_list:
                items.append(r[4])
                total_price += r[6]

            return {
                "order_id": f[0],
                "user_id": f[1],
                "paid": f[2],
                "items": items,
                "total_price": total_price
            }

    def add_item_to_order(self, order_id, item_id, price):
        # Check if the order-item pair already exists

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
                return {"order_id": local_res[0], "item_id": local_res[1],
                        "quantity": local_res[2], "price": local_res[3]}

            # Update the current value
            local_res = transaction.execute_sql(
                f"UPDATE orderitems SET quantity = quantity + 1, "
                f"total_price = total_price + {price} "
                f"WHERE order_id = '{order_id}' AND item_id = '{item_id}'"
                f"RETURNING order_id, item_id, quantity, total_price"
            ).one_or_none()

            return {"order_id": local_res[0], "item_id": local_res[1],
                    "quantity": local_res[2], "price": local_res[3]}

        try:
            res = self.database.run_in_transaction(adding)
        except Exception as e:
            return {"error": str(e)}
        return res

    def remove_item_from_order(self, order_id, item_id, price):
        def removing(transaction):
            finding_query = f"SELECT * FROM orderitems WHERE order_id = '{order_id}' AND item_id = '{item_id}'"
            order_item_combo = transaction.execute_sql(finding_query).one_or_none()
            # Does not exist
            if order_item_combo is None:
                return {"error": "order_id and item_id does not exist"}

            # Only one item left, delete the row
            if order_item_combo[2] == 1:
                local_res = transaction.execute_sql(
                    f"DELETE FROM orderitems WHERE order_id = '{order_id}' AND item_id = '{item_id}' "
                    f"RETURNING order_id, item_id"
                ).one_or_none()

                if local_res is None:
                    return {"error": "order_id and item_id does not exist"}

                return {"order_id": order_id, "item_id": item_id, "price": 0, "quantity": 0}

            # Update the current value
            local_res = transaction.execute_sql(
                f"UPDATE orderitems SET quantity = quantity - 1, "
                f"total_price = total_price - {price} "
                f"WHERE order_id = '{order_id}' AND item_id = '{item_id}'"
                f"RETURNING order_id, item_id, quantity, total_price"
            ).one_or_none()

            return {"order_id": local_res[0], "item_id": local_res[1],
                    "quantity": local_res[2], "price": local_res[3]}

        try:
            res = self.database.run_in_transaction(removing)
        except Exception as e:
            return {"error": str(e)}
        return res

    def pay_order(self, order_id):
        def paying(transaction):
            transaction.begin()
            finding_query = f"SELECT * FROM orders WHERE order_id = '{order_id}'"
            order = transaction.execute_sql(finding_query).one_or_none()

            print(order)

            if order is None or order[2] is True:
                return {"error": "order does not exist or has already been paid"}

            orderItemsQuery = "SELECT * FROM orderItems"

            query_all_items = f"SELECT * FROM orders AS o " \
                              f"LEFT JOIN ({orderItemsQuery}) AS oi " \
                              f"ON o.order_id = oi.order_id " \
                              f"WHERE o.order_id = '{order_id}'"

            # For a single consistent read, use snapshot
            # Snapshots do not have an execute update method
            print('query is \n', query_all_items)
            results: StreamedResultSet = transaction.execute_sql(query_all_items)

            if results is None:
                return {"error": "order does not exist"}

            result_list = list(results)
            print('result list', result_list)
            total_price = sum([float(r[6]) for r in result_list])

            print("total price is", total_price)

            # For each item, remove the items from the stock
            # There is a check that the item is in stock!!
            for i in range(0, len(result_list)):
                r = result_list[i]
                item_id = r[4]
                quantity = r[5]
                print('item id is', item_id)
                print('quantity is', quantity)

                upd = transaction.execute_sql(
                    f"UPDATE stock SET stock = stock - {quantity} WHERE item_id = '{item_id}'"
                )
                print('items removed from stock', upd)

            print('finished removing from stock')

            # Remove Credits
            user_id = result_list[0][1]
            print('user id is', user_id)

            rows_executed = transaction.execute_sql(
                f"UPDATE users SET credit = credit - {total_price} WHERE user_id = '{user_id}'"
            ).one_or_none()
            # This is not printed anymore
            print("amount of credits removed", rows_executed)

            # Mark the order as paid
            rows_executed2 = transaction.execute_sql(
                f"UPDATE orders SET paid = TRUE WHERE order_id = '{order_id}'"
            ).one_or_none()
            print("order marked as paid", rows_executed2)

            return {"order_id": order_id, "timestamp": timetamp}

        try:
            res = self.database.run_in_transaction(paying)
        except Exception as e:
            return {"error": str(e)}
        return res
