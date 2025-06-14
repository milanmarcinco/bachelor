import psycopg2
from dotenv import dotenv_values

env = dotenv_values()


def connection_factory():
    connection = psycopg2.connect(
        dbname=env["DB_NAME"],
        user=env["DB_USER"],
        password=env["DB_PASSWORD"],
        host=env["DB_HOST"],
        port=env["DB_PORT"]
    )

    connection.autocommit = True
    return connection


connection = connection_factory()
db = connection.cursor()
