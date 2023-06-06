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
        self.stock = sqlalchemy.Table('stock', self.metadata, autoload_with=self.engine)

    def create_item(self, item_id, price):
        query = sqlalchemy.insert(self.stock).values(item_id=item_id, price=price, amount=0)
        result = self.connection.execute(query).one_or_none()

        if result is None:
            return None

        return {"item_id": item_id}

    def find_item(self, item_id):
        stock = self.stock
        query = sqlalchemy.select([stock]).where(stock.columns.item_id == item_id)
        try:
            result = self.connection.execute(query).one()
        except NoResultFound:
            print('No result found')
            return None
        except MultipleResultsFound:
            print('Multiple results found')
            return None

        return result

    def add_stock(self, item_id, amount):
        stock = self.stock
        query = sqlalchemy.update(stock).where(stock.columns.item_id == item_id).values(
            amount=stock.columns.amount + amount)

        try:
            data = self.connection.execute(query).one()
        except NoResultFound:
            print('No result found')
            data = {'done': False}
        except MultipleResultsFound:
            print('Multiple results found')
            data = {'done': False}

        return data

    def remove_stock(self, item_id, amount):
        stock = self.stock
        query = sqlalchemy.update(stock).where(stock.columns.item_id == item_id).values(
            amount=stock.columns.amount - amount)

        try:
            data = self.connection.execute(query).one()
        except NoResultFound:
            print('No result found')
            data = {'done': False}
        except MultipleResultsFound:
            print('Multiple results found')
            data = {'done': False}

        return data
