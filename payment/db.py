from uuid import uuid4

from google.cloud import spanner


class UserDatabase:
    def __init__(self):
        instance_id = "spanner-db"
        database_id = "database"

        # Instantiate a client.
        spanner_client = spanner.Client()

        # Get a Cloud Spanner instance by ID.
        self.instance = spanner_client.instance(instance_id)
        self.database = self.instance.database(database_id)

    def create_user(self):
        u_id = str(uuid4())

        def trans_create_user(transaction):
            transaction.execute_update(
                "INSERT INTO users (user_id, credit) "
                f"VALUES ('{u_id}', 0) "
            )

        try:
            self.database.run_in_transaction(trans_create_user)
        except Exception as e:
            return {"error": str(e)}

        return {"user_id": u_id}

    def find_user(self, user_id):
        query = f"SELECT * FROM users WHERE user_id = '{user_id}'"

        with self.database.snapshot() as snapshot:
            result = snapshot.execute_sql(query).one_or_none()

            if result is None:
                return {"error": "user_id does not exist"}

            return {
                "user_id": result[0],
                "credit": float(result[1])
            }

    def add_credit_to_user(self, user_id, amount):
        # For the adding, we don't need to check amounts and stuff.
        f = float(amount)
        rows_aff = self.database.execute_partitioned_dml(
            "UPDATE users "
            f"SET credit = credit + {f} "
            f"WHERE user_id = '{user_id}' "
        )

        if rows_aff != 1:
            return {"error": "user_id does not exist"}

        return {"done": True, "amount_rows_affected": rows_aff}

    def remove_credit_from_user(self, user_id, amount):
        def update_credit(transaction):
            # There is a check in the DB that credit cannot be negative
            current_credit = transaction.execute_sql(
                f"SELECT credit FROM users WHERE user_id = '{user_id}'"
            ).one_or_none()

            if current_credit is None:
                return {"error": "user_id does not exist"}

            new_credit = float(current_credit[0]) - float(amount)
            rows_aff = transaction.execute_partitioned_dml(
                "UPDATE users "
                f"SET credit = {new_credit} "
                f"WHERE (user_id) = '{user_id}'",
            )

            if rows_aff != 1:
                return {"error": "user_id does not exist"}

            return {"done": True}

        try:
            return self.database.run_in_transaction(update_credit)
        except Exception as e:
            return {"error": str(e)}

    def get_payment_status(self, order_id):
        with self.database.snapshot() as snapshot:
            result = snapshot.execute_sql(
                f"SELECT paid FROM orders WHERE order_id = '{order_id}'"
            ).one_or_none()

            if result is None:
                return {"error": "order does not exist"}

            return {
                "paid": bool(result[0])
            }
