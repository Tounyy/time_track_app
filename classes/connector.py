from dotenv import load_dotenv
from psycopg2 import connect
import os

class Database:
    def __init__(self):
        try:
            self.DATABASE_URL = os.environ['DATABASE_URL']
        except:
            load_dotenv()
            self.DATABASE_URL = os.environ['DATABASE_URL']

    def create_connection(self):
        postgre_connection = connect(self.DATABASE_URL)
        postgre_connection.autocommit = True
        return postgre_connection
    
    def get_request(self, query):
        postgre_connection = self.create_connection()
        cursor = postgre_connection.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        postgre_connection.close()
        return data