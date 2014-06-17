from __future__ import print_function
import psycopg2
from amazonData import read_gz
import sys
import getpass

"""
create a connector object via
mysql.connector.connect(user=usr, database=db)
To execute queries:
cursor = cnx.cursor()
cursor.execute(query_string)
"""


class DBFill():
    def __init__(self, category, connection):
        self._category = category.lower()
        self._connection = connection
        self._cursor = connection.cursor()

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
                        helpfulness varchar(10),
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
    connection = psycopg2.connect(database=database, user=user, password=password)
    with DBFill(category, connection) as filler:
        entries = read_gz.parse(category)
        filler.create_table()
        filler.fill_table(entries)
        filler.commit()
        filler.close()