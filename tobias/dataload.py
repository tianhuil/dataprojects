import psycopg2 as pg
import sys

con = pg.connect(database= 'arXivdata')
with con:
    cur = con.cursor()
 #   cur.execute("DROP TABLE IF EXISTS arXivmeta") (commented out to avoid accidental deletions..)
    cur.execute("CREATE TABLE arXivmeta(arxivid TEXT PRIMARY KEY, Authors TEXT, Title TEXT, Abstract TEXT, Categories TEXT, MSC_Class TEXT, Created DATE)")

temp = open("/home/tobias/BigHarvest2/list.txt","r")
directory = temp.read().splitlines()
for line in directory:
    a = open("/home/tobias/BigHarvest2/"+line ,"r")
    b = Paper(BeautifulSoup(a))
    temp = (b.ident, b.authors, b.title, b.abstract, b.categories, b.mscclass, b.create)
    with con:
      cur.execute("INSERT INTO arXivmeta (arxivid, Authors, Title, Abstract, Categories, MSC_Class, Created) VALUES(%s, %s, %s, %s, %s, %s, %s)", temp)
      con.commit()
