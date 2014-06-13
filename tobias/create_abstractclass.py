import psycopg2 as pg
import sys
 
con = pg.connect(database ='arXivdata')
with con:
    cur = con.cursor()
    cur.execute("DROP TABLE IF EXISTS AbstractClass")
    cur.execute("CREATE TABLE AbstractClass(Id TEXT, Title TEXT, Abstract TEXT, Categories TEXT, MSC_Class TEXT)")
   
