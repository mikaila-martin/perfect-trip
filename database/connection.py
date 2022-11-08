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


def get_query(query, data=None):
    """Takes in a query string and data and returns the result of running that SQL
    query for the database."""

    # Establish connection and execute query on cursor
    connection, cursor = connect_to_database()
    cursor.execute(query, data)

    # Get rows and convert to list of dictionaries
    rows = cursor.fetchall()
    data = [dict(row) for row in rows]

    # Close connection and cursor
    connection.close()
    cursor.close()

    # Return data
    if len(data) == 0:
        data = None

    return data


def send_query(query, data=None):
    """Takes in a query string and data. Modifies the database by running the SQL query.
    Does not return anything."""
    connection, cursor = connect_to_database()
    cursor.execute(query, data)
    connection.commit()
    connection.close()
    cursor.close()
