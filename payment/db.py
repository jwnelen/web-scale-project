from uuid import uuid4

from google.cloud import spanner

import sqlalchemy, sys


class UserDatabase:
    def __init__(self):
        instance_id = "spanner-db"
        database_id = "database-staging"
        project_id = "wdmproject23-v2"

        # # Instantiate a client.
        # spanner_client = spanner.Client()
        # # Get a Cloud Spanner instance by ID.
        # self.instance = spanner_client.instance(instance_id)
        # self.database = self.instance.database(database_id)

        db_url = f"spanner+spanner:///projects/{project_id}/instances/{instance_id}/databases/{database_id}"
        self.engine = sqlalchemy.create_engine(db_url)
        self.connection = self.engine.connect()

        print("@# TABLE NAMES", self.engine.dialect.get_table_names(self.connection), file=sys.stderr)

        self.metadata = sqlalchemy.MetaData()
        self.users = sqlalchemy.Table('users', self.metadata, autoload_with=self.engine)

    def create_user(self):
        u_id = str(uuid4())

        query = sqlalchemy.insert(self.users).values(user_id=u_id, credit=0)
        result = self.connection.execute(query)

        print("###CREATE USER", u_id, file=sys.stderr)

        return {"user_id": u_id}

    def find_user(self, user_id):
        query = sqlalchemy.select(self.users).where(self.users.columns.user_id == user_id) 
        result = self.connection.execute(query).fetchall()

        print("##FIND USER ", result, file=sys.stderr)
        return {'user_id': result[0][0], 'credit': result[0][1]}


    def add_credit_to_user(self, user_id, amount):
        def update_user(transaction):

            current_credit = transaction.execute_sql(
                f"SELECT credit FROM users WHERE user_id = '{user_id}'"
            ).one_or_none()

            if current_credit is None:
                return {"error": "user_id does not exist"}

            new_credit = float(current_credit[0]) + float(amount)
            rows_aff = transaction.execute_update(
                "UPDATE users "
                f"SET credit = {new_credit} "
                f"WHERE (user_id) = '{user_id}'",
            )

            return {"done": True, "amount_rows_affected": rows_aff}

        try:
            return self.database.run_in_transaction(update_user)
        except Exception as e:
            return {"error": str(e)}

    def remove_credit_from_user(self, user_id, amount):
        def update_credit(transaction):
            # There is a check in the DB that credit cannot be negative
            current_credit = transaction.execute_sql(
                f"SELECT credit FROM users WHERE user_id = '{user_id}'"
            ).one_or_none()

            if current_credit is None:
                return {"error": "user_id does not exist"}

            new_credit = float(current_credit[0]) - float(amount)
            rows_aff = transaction.execute_update(
                "UPDATE users "
                f"SET credit = {new_credit} "
                f"WHERE (user_id) = '{user_id}'",
            )

            return {"done": True, "amount_rows_affected": rows_aff}

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
