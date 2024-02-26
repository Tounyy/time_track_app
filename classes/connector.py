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
    
    def get_request(self, query, params=None):
        connection = self.create_connection()
        cursor = connection.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            data = cursor.fetchall()
        finally:
            connection.close()
        return data

    def execute_query(self, query, params=None):
        postgre_connection = self.create_connection()
        cursor = postgre_connection.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            postgre_connection.commit() 
        except Exception as e:
            print(f"An error occurred: {e}")
            postgre_connection.rollback()  
        finally:
            postgre_connection.close()