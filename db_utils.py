import sqlite3
from sqlite3 import Error
import os
from api_config import DB_PATH

basedir = os.path.abspath(os.path.dirname(__file__))

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn

def create_league(conn, league_data):
    """
    Create a new project into the projects table
    :param conn:
    :param project:
    :return: project id
    """
    sql = ''' INSERT INTO League(fixture_id,league_id)
              VALUES(?,?) '''
    cur = conn.cursor()
    cur.execute(sql, league)
    return cur.lastrowid
