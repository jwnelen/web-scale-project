import sqlalchemy
from sqlalchemy.exc import NoResultFound, MultipleResultsFound


class SpannerDB:
    def __init__(self):
        project_id = "wdmproject23-v2"
        instance_id = "spanner-db"
        database_id = "database"

        db_url = f"spanner+spanner:///projects/{project_id}/instances/{instance_id}/databases/{database_id}"

        self.engine = sqlalchemy.create_engine(db_url)
        self.connection = self.engine.connect()

        self.metadata = sqlalchemy.MetaData()
        self.users = sqlalchemy.Table('users', self.metadata, autoload_with=self.engine)

    def create_user(self, user_id):
        query = sqlalchemy.insert(self.users).values(user_id=user_id, credit=0)
        result = self.connection.execute(query).one_or_none()

        if result is None:
            return None

        return {"user_id": user_id}

    def find_user(self, user_id):
        users = self.users
        query = sqlalchemy.select([users]).where(users.columns.user_id == user_id)
        try:
            result = self.connection.execute(query).one()
        except NoResultFound:
            print('No result found')
            return None
        except MultipleResultsFound:
            print('Multiple results found')
            return None

        return result

    def add_credit_to_user(self, user_id, amount):
        users = self.users
        query = sqlalchemy.update(users).where(users.columns.user_id == user_id).values(
            credit=users.columns.credit + amount)

        try:
            data = self.connection.execute(query).one()
        except NoResultFound:
            print('No result found')
            data = {'done': False}
        except MultipleResultsFound:
            print('Multiple results found')
            data = {'done': False}

        return data

    def remove_credit_from_user(self, user_id, amount):
        users = self.users
        query = sqlalchemy.update(users).where(users.columns.user_id == user_id).values(
            credit=users.columns.credit - amount)

        try:
            data = self.connection.execute(query).one()
        except NoResultFound:
            print('No result found')
            data = {'done': False}
        except MultipleResultsFound:
            print('Multiple results found')
            data = {'done': False}

        return data

    def get_payment_status(self, order_id):
        users = self.users
        query = sqlalchemy.select([users]).where(users.columns.order_id == order_id)

        try:
            result = self.connection.execute(query).one()
        except NoResultFound:
            print('No result found')
            return None
        except MultipleResultsFound:
            print('Multiple results found')
            return None

        return result
