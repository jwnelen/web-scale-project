from uuid import uuid4

from google.api_core.exceptions import FailedPrecondition
from google.cloud import spanner


class OrderDatabase:
    def __init__(self):
        instance_id = "spanner-db"
        database_id = "database"

        # Instantiate a client.
        spanner_client = spanner.Client()

        # Get a Cloud Spanner instance by ID.
        self.instance = spanner_client.instance(instance_id)
        self.database = self.instance.database(database_id)

    # Execute UPDATE will return the number of rows affected
    # Execute SQL will return the result set

    def create_order(self, user_id):
        u_id = str(uuid4())

        def trans_create_order(transaction):
            transaction.execute_update(
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
        query = f"SELECT * FROM orders WHERE order_id = '{order_id}'"

        # For a single consistent read, use snapshot
        with self.database.snapshot() as snapshot:
            # Snapshots do not have an execute update method
            result = snapshot.execute_sql(query).one_or_none()

            if result is None:
                return {"error": "order does not exist"}

            return {
                "order_id": result[0],
                "user_id": result[1],
                "paid": result[2]
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
