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


def select_all_league(conn):
    """
    Query all rows in the league table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM League")

    rows = cur.fetchall()

    for row in rows:
        print(row)

# def delete_columns(conn):
#     """
#     Delete all rows in the league table
#     :param conn: the Connection object
#     :return:
#     """
#     cur = conn.cursor()
#     test = cur.execute("select * from league")
#     columns = list(map(lambda x: x[0], test.description))
#     columns = [x for x in columns if 'sog_away' not in x]
#     columns = [x for x in columns if 'sog_home' not in x]
    # cols_str = str(columns).replace('[', '').replace(']', '')
    # cur.execute("""-- disable foreign key constraint check
    # -- start a transaction
    # BEGIN TRANSACTION;""")
    # cur.execute("""CREATE TABLE IF NOT EXISTS new_table( """ + cols_str + """
    # );""")
    # cur.execute("""INSERT INTO new_table(""" + cols_str + """)
    # SELECT """ + cols_str + """
    # FROM league;""")
    # cur.execute("""DROP TABLE league;""")
    # cur.execute("""ALTER TABLE new_table RENAME TO league;""")
    # cur.execute("""COMMIT;""")

def main():
    database = DB_PATH

    # create a database connection
    conn = create_connection(database)
    with conn:
        # create a new project

        delete_columns(conn)

if __name__ == '__main__':
    main()