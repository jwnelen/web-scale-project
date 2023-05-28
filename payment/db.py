from uuid import uuid4

from google.cloud import spanner


class UserDatabase:
    def __init__(self):
        instance_id = "spanner-db"
        database_id = "order-db"

        # Instantiate a client.
        spanner_client = spanner.Client()

        # Get a Cloud Spanner instance by ID.
        self.instance = spanner_client.instance(instance_id)
        self.database = self.instance.database(database_id)

    def create_user(self):
        u_id = str(uuid4())

        try:
            with self.database.batch() as batch:
                batch.insert(
                    table="users",
                    columns=("user_id", "credit"),
                    values=[(u_id, 0)],
                )

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
                "credit": result[1]
            }

    def add_credit_to_user(self, user_id, amount):
        def update_user(transaction):
            row_ct = transaction.execute_update(
                "UPDATE users "
                f"SET credit = credit + {amount} "
                f"WHERE (user_id) = '{user_id}'",
            )

            return {"amount_rows_affected": row_ct}

        return self.database.run_in_transaction(update_user)

    def get_payment_status(self, order_id):
        with self.database.snapshot() as snapshot:
            result = snapshot.execute_sql(
                f"SELECT paid FROM orders WHERE order_id = '{order_id}'"
            ).one_or_none()

            if result is None:
                return {"error": "order does not exist"}

            return {
                "paid": result[0]
            }
