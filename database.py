from psycopg2 import pool
import os

connection_pool = None

def init_connection_pool():
    global connection_pool
    connection_pool = pool.SimpleConnectionPool(
        minconn=1, 
        maxconn=20, 
        user=os.environ.get('DBUSER'),
        password=os.environ.get('DBPASS'),
        host=os.environ.get('DBHOST'),
        database=os.environ.get('DATABASE')
    )
