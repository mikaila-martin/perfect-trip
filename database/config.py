import psycopg2
import psycopg2.extras
from config import env, postgres

# Information on psycopg2 library from
# https://www.psycopg.org/docs/usage.html#passing-parameters-to-sql-queries
# 10/12/2022


def connect_to_database():
    """Connects to the database associated with the information given in the
    config.py file."""
    connection = psycopg2.connect(
        host=postgres[env]["host"],
        database=postgres[env]["database"],
        user=postgres[env]["user"],
        password=postgres[env]["password"],
        port=postgres[env]["port"],
    )

    cur = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    return connection, cur


def query_one(query, data):
    """Takes in a query string and data and returns the result of running that SQL
    query for the database."""

    # Establish connection and execute query on cursor
    connection, cursor = connect_to_database()
    cursor.execute(query, data)

    # Fetch row
    row = cursor.fetchone()

    # Close connection and cursor
    connection.close()
    cursor.close()

    # Convert row to dictionary
    if row is not None:
        row = dict(row)

    return row


def query_many(query, data):
    """Takes in a query string and data and returns the result of running that SQL
    query for the database."""

    # Establish connection and execute query on cursor
    connection, cursor = connect_to_database()
    cursor.execute(query, data)

    # Fetch rows and convert to list of dictionaries
    rows = cursor.fetchall()
    rows = [dict(row) for row in rows]

    # Close connection and cursor
    connection.close()
    cursor.close()

    return rows


def mutation(query, data):
    """Takes in a query string and data. Modifies the database by running the SQL query.
    Does not return anything."""

    # Establish connection and execute query on cursor
    connection, cursor = connect_to_database()
    cursor.execute(query, data)

    # Commit mutation
    connection.commit()

    # Close connection and cursor
    connection.close()
    cursor.close()
