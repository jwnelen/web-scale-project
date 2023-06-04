from google.cloud import spanner


class SpannerDB:
    def __init__(self):
        instance_id = "spanner-db"
        database_id = "database"

        # Instantiate a client.
        spanner_client = spanner.Client()

        # Get a Cloud Spanner instance by ID.
        self.instance = spanner_client.instance(instance_id)
        self.database = self.instance.database(database_id)

    def create_item(self, item_id, price):
        def trans_create_item(transaction):
            transaction.execute_update(
                "INSERT INTO stock (item_id, price, amount) "
                f"VALUES ('{item_id}', {price}, 0) "
            )

        try:
            self.database.run_in_transaction(trans_create_item)
            data = {'item_id': item_id}

        except Exception as e:
            data = {}

        return data

    def find_item(self, item_id):
        query = f"SELECT * FROM stock WHERE item_id = '{item_id}'"

        with self.database.snapshot() as snapshot:
            result = snapshot.execute_sql(query).one_or_none()

            if result is None:
                data = {}
            else:
                data = {
                    "stock": int(result[2]),
                    "price": float(result[1])
                }

        return data

    def add_stock(self, item_id, amount):
        def update_stock(transaction):
            return transaction.execute_update(
                "UPDATE stock "
                f"SET amount = amount + {amount} "
                f"WHERE (item_id) = '{item_id}'"
            )

        try:
            row_ct = self.database.run_in_transaction(update_stock)
            if row_ct == 1:
                data = {'success': True}
            else:
                data = {'success': False}
        except Exception as e:
            data = {'success': False}

        return data

    def remove_stock(self, item_id, amount):
        def update_stock(transaction):
            current_stock = transaction.execute_sql(
                f"SELECT amount FROM stock WHERE item_id = '{item_id}'"
            ).one_or_none()

            if current_stock is None:
                return 0

            if int(amount) > int(current_stock[0]):
                return 0

            return transaction.execute_update(
                "UPDATE stock "
                f"SET amount = amount - {amount} "
                f"WHERE (item_id) = '{item_id}'"
            )

        try:
            row_ct = self.database.run_in_transaction(update_stock)
            if row_ct == 1:
                data = {'success': True}
            else:
                data = {'success': False}
        except Exception as e:
            data = {'success': False}

        return data
