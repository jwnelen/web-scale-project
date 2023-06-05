from uuid import uuid4

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

        # This is using Mutations
        try:
            with self.database.batch() as batch:
                batch.insert(
                    table="orders",
                    columns=("order_id", "user_id", "paid"),
                    values=[(u_id, user_id, False)],
                )
                data = {"order_id": u_id}
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
                return 1

            # Update the current value
            local_res = transaction.execute_sql(
                f"UPDATE orderitems SET quantity = quantity + 1, "
                f"total_price = total_price + {price} "
                f"WHERE order_id = '{order_id}' AND item_id = '{item_id}' "
                f"RETURNING order_id, item_id, quantity, total_price"
            ).one_or_none()

            if local_res is None:
                return 0

            return 1

        try:
            status = self.database.run_in_transaction(adding)
            if status == 1:
                data = {'success': True}
            else:
                data = {'success': False}
        except Exception as e:
            data = {'success': False}

        return data

    def remove_item_from_order(self, order_id, item_id, price):
        def removing(transaction):
            finding_query = f"SELECT * FROM orderitems WHERE order_id = '{order_id}' AND item_id = '{item_id}'"
            order_item_combo = transaction.execute_sql(finding_query).one_or_none()
            # Does not exist
            if order_item_combo is None:
                return 0

            # Only one item left, delete the row
            if order_item_combo[2] == 1:
                local_res = transaction.execute_sql(
                    f"DELETE FROM orderitems WHERE order_id = '{order_id}' AND item_id = '{item_id}' "
                    f"RETURNING order_id, item_id"
                ).one_or_none()

                if local_res is None:
                    return 0

                return 1

            # Update the current value
            rows_executed = transaction.execute_sql(
                f"UPDATE orderitems SET quantity = quantity - 1, "
                f"total_price = total_price - {price} "
                f"WHERE order_id = '{order_id}' AND item_id = '{item_id}' "
                f"RETURNING order_id, item_id, quantity, total_price"
            ).one_or_none()

            if rows_executed is None:
                return 0

            return 1

        try:
            status = self.database.run_in_transaction(removing)
            if status == 1:
                data = {'success': True}
            else:
                data = {'success': False}
        except Exception as e:
            data = {'success': False}

        return data

    def pay_order(self, order_id):
        # First check if everything is in stock and if the order exists
        # We need multi-use to read multiple sql statements
        with self.database.snapshot(multi_use=True) as snapshot:
            print("Snapshot created")
            # Check order
            finding_query = f"SELECT * FROM orders WHERE order_id = '{order_id}'"
            order = snapshot.execute_sql(finding_query).one_or_none()
            if order is None or order[2] is True:
                print("Order does not exist or is already paid")
                return {'success': False}

            user_id = order[1]
            # orderItemsQuery = "SELECT * FROM orderItems"

            # query_all_items = f"SELECT * FROM orders AS o " \
            #                   f"LEFT JOIN ({orderItemsQuery}) AS oi " \
            #                   f"ON o.order_id = oi.order_id " \
            #                   f"WHERE o.order_id = '{order_id}'"

            # Newly created VIEW
            query_all_items = f"SELECT * FROM orderswithitems where order_id = '{order_id}'"

            results: StreamedResultSet = snapshot.execute_sql(query_all_items)

            result_list = list(results)
            total_price = sum([float(r[4]) for r in result_list])

            # Check if the user has enough credit
            res = snapshot.execute_sql(
                f"SELECT credit FROM users WHERE user_id = '{user_id}' "
            ).one_or_none()

            if res is None:
                print("User does not exist")
                return {'success': False}
            if float(res[0]) < total_price:
                print("User does not have enough credit", res[0], total_price)
                return {'success': False}

            # Check if all items are in stock
            for i in range(0, len(result_list)):
                r = result_list[i]
                item_id_ = r[3]
                quantity_ = r[5]

                res = snapshot.execute_sql(
                    f"SELECT amount FROM stock WHERE item_id = '{item_id_}' "
                ).one_or_none()

                if res is None:
                    print("Item does not exist")
                    return {'success': False}
                if int(res[0]) < quantity_:
                    print("Item does not have enough stock", res[0], quantity_)
                    return {'success': False}

        def transaction_pay_order(transaction):
            print("Transaction started")
            # For each item, remove the items from the stock

            print(result_list)

            for indx in range(0, len(result_list)):
                r = result_list[indx]
                item_id = r[3]
                quantity = r[5]

                upd = transaction.execute_update(
                    f"UPDATE stock SET amount = amount - {quantity} WHERE item_id = '{item_id}'"
                )

            # Remove Credits
            rows_executed = transaction.execute_update(
                f"UPDATE users SET credit = credit - {total_price} WHERE user_id = '{user_id}'"
            )

            # Mark the order as paid - COMMIT
            rows_executed2 = transaction.execute_update(
                f"UPDATE orders SET paid = TRUE WHERE order_id = '{order_id}'"
            )
            if rows_executed != 1 or rows_executed2 != 1:
                return 0

            return 1

        try:
            status = self.database.run_in_transaction(transaction_pay_order)
            if status == 1:
                data = {'success': True}
            else:
                data = {'success': False}
        except Exception as e:
            data = {'success': False}

        return data
