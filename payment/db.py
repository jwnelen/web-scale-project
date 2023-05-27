from google.api_core.exceptions import FailedPrecondition
from google.cloud import spanner
from uuid import uuid4


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
