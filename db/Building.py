from psycopg2 import connect, Error
import pickle


class Building(object):

    def __init__(self, dbname, user, host, password):
        self.dbname = dbname
        self.user = user
        self.host = host
        self.password = password
        self.connection = None
        self.cursor = None

    def connect_db(self):

        # Create database connection
        self.connection = connect(
            dbname=self.dbname,
            user=self.user,
            password=self.password,
            host=self.host,
        )
        self.connection.set_session(autocommit=True)
        self.cursor = self.connection.cursor()

    def create_tb(self):
        if not self.connection:
            self.connect_db()
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS building_data (
                Address VARCHAR PRIMARY KEY,
                BuildingNPArray BYTEA
            )
            """
        )
        self.close()

    def select_db(self, address):
        if not self.connection:
            self.connect_db()
        # Fetch building data from the database
        self.cursor.execute(
            """
            SELECT Address, BuildingNPArray
            FROM building_data
            WHERE Address=%s
            """,
            (address,)
        )
        db_result = self.cursor.fetchone()
        if db_result is not None:
            result = {'Address': db_result[0], 'BuildingNPArray': pickle.loads(db_result[1])}
        else:
            result = None
        self.close()
        return result

    def insert_db(self, result):
        if not self.connection:
            self.connect_db()
        self.cursor.execute(
            """
            INSERT INTO building_data(Address, BuildingNPArray)
            VALUES (%s, %s)
            """,
            (result['Address'], pickle.dumps(result['BuildingNPArray']))
        )
        self.close()

    def close(self):
        self.cursor.close()
        self.connection.close()
        self.cursor = None
        self.connection = None
