from uuid import uuid4

from google.cloud import spanner


class StockDatabase:
    def __init__(self):
        instance_id = "spanner-db"
        database_id = "database"

        # Instantiate a client.
        spanner_client = spanner.Client()

        # Get a Cloud Spanner instance by ID.
        self.instance = spanner_client.instance(instance_id)
        self.database = self.instance.database(database_id)

    def create_item(self, price):
        item_id = str(uuid4())

        # This is using Mutations
        try:
            with self.database.batch() as batch:
                batch.insert(
                    table="stock",
                    columns=("item_id", "price", "amount"),
                    values=[(item_id, price, 0)],
                )
        except Exception as e:
            return {"error": str(e)}

        return {"item_id": item_id}

        # def trans_create_item(transaction):
        #     transaction.execute_update(
        #         "INSERT INTO stock (item_id, price, amount) "
        #         f"VALUES ('{item_id}', {price}, 0) "
        #     )
        #
        # try:
        #     self.database.run_in_transaction(trans_create_item)
        # except Exception as e:
        #     return {"error": str(e)}
        # return {"item_id": item_id}

    def find_item(self, item_id):
        query = f"SELECT * FROM stock WHERE item_id = '{item_id}'"

        with self.database.snapshot() as snapshot:
            result = snapshot.execute_sql(query).one_or_none()

            if result is None:
                return {"error": "item_id does not exist"}
            return {
                "stock": int(result[2]),
                "price": float(result[1])
            }

    def add_stock(self, item_id, amount):
        def update_stock(transaction):
            row_ct = transaction.execute_update(
                "UPDATE stock "
                f"SET amount = amount + {amount} "
                f"WHERE (item_id) = '{item_id}'"
            )

            return row_ct

        try:
            res = self.database.run_in_transaction(update_stock)
        except Exception as e:
            return {"error": str(e)}
        return {"rows_updated": res}

    def remove_stock(self, item_id, amount):
        def update_stock(transaction):
            current_stock = transaction.execute_sql(
                f"SELECT amount FROM stock WHERE item_id = '{item_id}'"
            ).one_or_none()
            if int(amount) > int(current_stock[0]):
                return {"error": "not enough stock"}

            row_ct = transaction.execute_update(
                "UPDATE stock "
                f"SET amount = amount - {amount} "
                f"WHERE (item_id) = '{item_id}'"
            )

            return {"amount_rows_affected": row_ct}

        try:
            res = self.database.run_in_transaction(update_stock)
        except Exception as e:
            return {"error": str(e)}
        return res
