from __future__ import print_function
import psycopg2
from amazonData import read_gz
import sys
import getpass

"""
create a connection object via
cnx = psycopg2.connect(user=usr, database=db, password=pwd)
To execute queries:
cursor = cnx.cursor()
cursor.execute(query_string)

careful with the query string, use of string concatenation
is to be avoided (with user input) table names should be
hard coded.
"""


class DBFill():

    def __init__(self, database, category, user="", password=""):
        self._category = category.lower()
        self._connection = psycopg2.connect(database=database, user=user, password=password)
        self._cursor = self._connection.cursor()

    def __enter__(self):
        return self

    def __exit__(self, _type, value, traceback):
        self.close()

    def create_table(self):
        self._cursor.execute("DROP TABLE IF EXISTS %s;" % self._category)
        self._cursor.execute("""CREATE TABLE %s
                       (productId varchar(30),
                        userId varchar(30),
                        profileName varchar(50),
                        price numeric(7, 2),
                        title text,
                        summary text,
                        text text,
                        score integer,
                        helpfulness varchar(12),
                        time integer
                       );""" % self._category)

    def insert_entry(self, entry):
        self._cursor.execute("""INSERT INTO """ + self._category + """
                             (productId, userId, profileName, price, title, summary, text, score, helpfulness, time)
                             VALUES
                             (%(productId)s, %(userId)s, %(profileName)s, %(price)s, %(title)s,
                             %(summary)s, %(text)s, %(score)s, %(helpfulness)s, %(time)s);""", entry)

    def fill_table(self, entries):
        """
        Populate the database
        :param entries: an iterable of database entries
        """
        for entry in entries:
            self.insert_entry(entry)
        self.commit()

    def commit(self):
        self._connection.commit()

    def close(self):
        self._cursor.close()
        self._connection.close()


class DBRead():

    def __init__(self, database, user, password):
        self._database = database
        self._connection = psycopg2.connect(database, user=user, password=password)
        self._cursor = self._connection.cursor()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self._cursor.close()
        self._connection.close()

    def select(self, columns):
        columns = ", ".join(columns)
        self._cursor.execute("SELECT " + columns +  # this is bad; change it to use categories list
                             " FROM " + database)

    def fetch_one(self):
        return self._cursor.fetchone()


if __name__ == "__main__":
    args = sys.argv
    try:
        user = args[1]
        database = args[2]
        category = read_gz.categories[int(args[3])]
    except IndexError:
        sys.exit("Usage:\n"
                 "\tpython create_db.py username database category")
    password = getpass.getpass("Password:")
    with DBFill(database, category, user, password) as filler:
        entries = read_gz.parse(category)
        filler.create_table()
        filler.fill_table(entries)
        filler.commit()
        filler.close()