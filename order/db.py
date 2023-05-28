from uuid import uuid4

from google.api_core.exceptions import FailedPrecondition
from google.cloud import spanner


class OrderDatabase:
    def __init__(self):
        instance_id = "spanner-db"
        database_id = "order-db"

        # Instantiate a client.
        spanner_client = spanner.Client()

        # Get a Cloud Spanner instance by ID.
        self.instance = spanner_client.instance(instance_id)
        self.database = self.instance.database(database_id)

    def create_order(self, user_id):
        u_id = str(uuid4())

        try:
            with self.database.batch() as batch:
                batch.insert(
                    table="orders",
                    columns=("order_id", "user_id", "paid"),
                    values=[(u_id, user_id, False)],
                )

        # handle error when user_id does not exist
        except FailedPrecondition:
            return {"error": "user_id does not exist"}
        except Exception as e:
            return {"error": str(e)}

        return {"order_id": u_id}

    def remove_order(self, order_id):
        with self.database.batch() as batch:
            res = batch.delete(table="orders", keyset={"order_id": order_id})

        return res

    def find_order(self, order_id):
        query = f"SELECT * FROM orders WHERE order_id = '{order_id}'"

        with self.database.snapshot() as snapshot:
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
            finding_query = f"SELECT * FROM order_items WHERE order_id = '{order_id}' AND item_id = '{item_id}'"
            order_item_combo = transaction.execute_sql(finding_query).one_or_none()
            # Does not exist
            if order_item_combo is None:
                res = transaction.execute_sql(
                    f"INSERT INTO order_items (order_id, item_id, quantity, total_price) "
                    f"VALUES ('{order_id}', '{item_id}', 1, {price})"
                    f"RETURNING order_id, item_id, quantity, total_price"
                ).one()
                return {"order_id": res[0], "item_id": res[1], "quantity": res[2], "price": res[3]}

            # Update the current value
            res = transaction.execute_sql(
                f"UPDATE order_items SET quantity = quantity + 1, "
                f"total_price = total_price + {price} "
                f"WHERE order_id = '{order_id}' AND item_id = '{item_id}'"
                f"RETURNING order_id, item_id, quantity, total_price"
            ).one_or_none()

            return {"order_id": res[0], "item_id": res[1], "quantity": res[2], "price": res[3]}

        return self.database.run_in_transaction(adding)

    def remove_item_from_order(self, order_id, item_id, price):
        def adding(transaction):
            finding_query = f"SELECT * FROM order_items WHERE order_id = '{order_id}' AND item_id = '{item_id}'"
            order_item_combo = transaction.execute_sql(finding_query).one_or_none()
            # Does not exists
            if order_item_combo is None:
                return {"error": "order_id and item_id does not exist"}

            # Only one item left, delete the row
            if order_item_combo[2] == 1:
                res = transaction.execute_sql(
                    f"DELETE FROM order_items WHERE order_id = '{order_id}' AND item_id = '{item_id}' "
                    f"RETURNING order_id, item_id"
                ).one_or_none()

                if res is None:
                    return {"error": "order_id and item_id does not exist"}

                return {"order_id": order_id, "item_id": item_id, "price": 0, "quantity": 0}

            # Update the current value
            res = transaction.execute_sql(
                f"UPDATE order_items SET quantity = quantity - 1, "
                f"total_price = total_price - {price} "
                f"WHERE order_id = '{order_id}' AND item_id = '{item_id}'"
                f"RETURNING order_id, item_id, quantity, total_price"
            ).one_or_none()

            return {"order_id": res[0], "item_id": res[1], "quantity": res[2], "price": res[3]}

        return self.database.run_in_transaction(adding)
