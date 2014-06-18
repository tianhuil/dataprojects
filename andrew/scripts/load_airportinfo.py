import MySQLdb as mdb
import sys
import numpy as np
import glob
import zipfile
import os

import load_credentials_nogit as creds

#Load up the lookup table of airports into sql:
if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Syntax: [Airport name csv file]")


    #Connect to the db:
    con = ''
    try:
        con = mdb.connect(host=creds.host,user=creds.user,db=creds.database,passwd=creds.password,local_infile=1)
        cur = con.cursor()
        #drop the db:
        cur.execute('drop table if exists airports')
        cur.execute("""create table airports(
        origin varchar(3) not null primary key,
        airportname varchar(255) not null default ''
        )""")

        #Load the db
        cur.execute('''load data local infile "{0:s}" into table airports fields terminated by "," optionally enclosed by """" lines terminated by "\r\n" ignore 1 lines(origin,airportname)'''.format(sys.argv[1]))
        con.commit()

    except mdb.Error, e:
        print "Error %d: %s" % (e.args[0],e.args[1])
        sys.exit(1)
    finally:
        if con:
            con.close()
        
