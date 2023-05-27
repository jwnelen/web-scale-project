from google.api_core.exceptions import FailedPrecondition
from google.cloud import spanner
from uuid import uuid4


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
