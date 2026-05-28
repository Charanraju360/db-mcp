import sqlite3
import psycopg2
import pymysql

# this function takes db type and credentials
# and returns a connection object

def make_connection(db_type, host, port, user, password, database):

    if db_type == "sqlite":
        # sqlite only needs a file path, no host or user needed
        conn = sqlite3.connect(database)
        return conn

    elif db_type == "postgres":
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            dbname=database
        )
        return conn

    elif db_type == "mysql":
        conn = pymysql.connect(
            host=host,
            port=int(port),
            user=user,
            password=password,
            database=database
        )
        return conn

    else:
        raise ValueError(f"unknown db type: {db_type}. use sqlite, postgres or mysql")