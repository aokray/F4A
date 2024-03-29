import psycopg2
from configparser import ConfigParser
from typing import Dict, List

# From postgres tutorial
def config(filename: str = "database.ini", section: str = "postgresql") -> Dict:
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)

    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception(
            "Section {0} not found in the {1} file".format(section, filename)
        )

    return db


# From postgres tutorial
def connect(qstring: str) -> List:
    """Connect to the PostgreSQL database server"""
    conn = None
    returnVal = None
    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        # print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)

        # create a cursor
        cur = conn.cursor()

        # execute a statement
        # print('Querying...')
        cur.execute(qstring)

        # display the PostgreSQL database server version
        # db_version = cur.fetchone()
        # print(db_version)

        returnVal = cur.fetchall()
        # print(returnVal)

        # close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error on: ")
        print(qstring)
        print(error)
    finally:
        if conn is not None:
            conn.close()
            # print('Database connection closed.')

    return returnVal


def connect_insert(istring: str) -> None:
    """Connect to the PostgreSQL database server"""
    conn = None
    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        print("Connecting to the PostgreSQL database...")
        conn = psycopg2.connect(**params)

        # create a cursor
        cur = conn.cursor()

        # execute a statement
        print("Inserting...")
        cur.execute(istring)

        # returnVal = cur.fetchall()
        # print(returnVal)

        # close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print("Database connection closed.")
