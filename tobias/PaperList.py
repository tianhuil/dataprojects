# This script reads a file, list.txt, that lists all
# the papers in a directory. It then opens each file
# one by one, creates a temporary Paper object, b,
# and adds its summary to a database. 
import sqlite3 as lite
import sys
con = lite.connect('test.db')
with con:
  cur = con.cursor()
  cur.execute("DROP TABLE IF EXISTS Papertest")
  cur.execute("CREATE TABLE Papertest(Id TEXT, Created TEXT, Title TEXT")


temp = open("/home/tobias/Harvests/list.txt","r")
directory = temp.read().splitlines()
directory.pop(0) #first line is list.txt
for line in directory:
    a = open("/home/tobias/Harvests/"+line,"r")
    b = Paper(BeautifulSoup(a))
    with con:
      cur = con.cursor()
      cur.execute("INSERT INTO Papertest VALUES(?,?,?)", b.summary)


