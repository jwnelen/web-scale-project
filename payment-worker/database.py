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

    def create_user(self, user_id):

        def trans_create_user(transaction):
            transaction.execute_update(
                "INSERT INTO users (user_id, credit) "
                f"VALUES ('{user_id}', 0) "
            )

        try:
            self.database.run_in_transaction(trans_create_user)
            data = {"user_id": user_id}
        except Exception as e:
            data = {}

        return data

    def find_user(self, user_id):
        query = f"SELECT * FROM users WHERE user_id = '{user_id}'"

        with self.database.snapshot() as snapshot:
            result = snapshot.execute_sql(query).one_or_none()

            if result is None:
                data = {}
            else:
                data = {"user_id": result[0], "credit": float(result[1])}

            return data

    def add_credit_to_user(self, user_id, amount):
        def update_user(transaction):
            return transaction.execute_update(
                "UPDATE users "
                f"SET credit = credit + {amount} "
                f"WHERE (user_id) = '{user_id}'",
            )

        try:
            row_ct = self.database.run_in_transaction(update_user)
            if row_ct == 1:
                data = {'done': True}
            else:
                data = {'done': False}
        except Exception as e:
            data = {'done': False}

        return data

    def remove_credit_from_user(self, user_id, amount):
        def update_credit(transaction):
            # There is a check in the DB that credit cannot be negative
            current_credit = transaction.execute_sql(
                f"SELECT credit FROM users WHERE user_id = '{user_id}'"
            ).one_or_none()

            if current_credit is None:
                return {'success': False}

            new_credit = float(current_credit[0]) - float(amount)
            transaction.execute_update(
                "UPDATE users "
                f"SET credit = {new_credit} "
                f"WHERE (user_id) = '{user_id}'",
            )

            return {'success': True}

        try:
            data = self.database.run_in_transaction(update_credit)
        except Exception as e:
            data = {}

        return data

    def get_payment_status(self, order_id):
        with self.database.snapshot() as snapshot:
            result = snapshot.execute_sql(
                f"SELECT paid FROM orders WHERE order_id = '{order_id}'"
            ).one_or_none()

            if result is None:
                data = {}
            else:
                data = {"paid": bool(result[0])}

            return data