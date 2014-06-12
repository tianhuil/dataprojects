

#!/usr/bin/python

import MySQLdb as mdb
import json

# store login credentials in same directory as this
with open(creds.json) as c:
  creds = json.load(c)

# connect to mysql
# make sure credentials have the appropriate permissions to create databases, tables, etc
con = mdb.connect(host=localhost, user=creds["uname"], passwd=creds["pwd"])
cur = con.cursor()

cur.execute("create database beerad")  # create database
cur.execute("use beerad")              # select it

# create table of monthly segment aggregates
# total freight/passengers/etc per carrier per route
cur.execute('''create table if not exists beerscores (
  ,
  primary key(year, month, airline_id, origin_airport_id, dest_airport_id) )''' )
  
  
# beer meta data
#cur.execute("""create table if not exists aircraft