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

        with self.database.batch() as batch:
            batch.insert(
                table="orders",
                columns=("order_id", "user_id", "paid"),
                values=[(u_id, user_id, False)],
            )

        return {"order_id": u_id}

    def find_order(self, order_id):
        query = f"SELECT * FROM orders WHERE order_id = '{order_id}'"

        with self.database.snapshot() as snapshot:
            result = snapshot.execute_sql(query)
            first_res = list(result)[0]
            return {
                "order_id": first_res[0],
                "user_id": first_res[1],
                "paid": first_res[2]
            }
