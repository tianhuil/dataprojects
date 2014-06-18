import psycopg2 as pg
import sys
temp = open("/home/tobias/BigHarvest2/list.txt","r")
directory = temp.read().splitlines()
for line in directory:
    a = open("/home/tobias/BigHarvest2/"+line,"r")
    b = Paper(BeautifulSoup(a))
    with con:
      #cur = con.cursor()
      cur.execute("INSERT INTO AbstractClass (Id, Title, Abstract, Categories, MSC_Class) VALUES(%s, %s, %s, %s, %s)", b.summary)
      con.commit()
