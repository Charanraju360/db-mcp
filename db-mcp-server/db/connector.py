import sqlite3
import psycopg2
import pymysql

def make_connection(db_type, host, port, user, password, database):

    if db_type == "sqlite":
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