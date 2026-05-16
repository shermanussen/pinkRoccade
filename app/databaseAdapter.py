import psycopg2
import os

class postgresConnection:
    def getConnection():
        host_name = 'postgres'
        dbname = 'my_db'
        user_ = 'postgres'
        password_ = os.getenv("POSTGRESS_PASSWORD")
        conn = psycopg2.connect(database = dbname, user = user_, password = password_, host = host_name, port = 5432)
        return conn