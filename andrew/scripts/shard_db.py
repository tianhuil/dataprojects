import numpy as np
import MySQLdb as mdb
#import sqlalchemy as sql
import sys
import time

import load_credentials_nogit as creds

#Splits the main DB into smaller shards for easier future processing.
if __name__ == "__main__":

    if len(sys.argv) != 2:
        sys.exit("Syntax: [minimum number of flights to be considered]")
    min_flights = int(sys.argv[1])
        
    months = {'jan':1,'feb':2,'mar':3,'apr':4,'may':5,'jun':6,'jul':7,'aug':8,'sep':9,'oct':10,'nov':11,'dec':12}
    #weekdays = {'sun':1,'mon':2,'tue':3,'wed':4,'thu':5,'fri':6,'sat':7]
    hours = {'early':[0,800],'morning':[800,1200],'afternoon':[1200,1500],'evening':[1500,1900],'night':[1900,2400]}

    #Connect to the db:
    con = ''
    try:
        con = mdb.connect(host=creds.host,user=creds.user,db=creds.database,passwd=creds.password,local_infile=1)
        cur = con.cursor()

        #Get the airports that have had more than min_flights departures:
        start = time.time()
        cur.execute('select origin from flightdelays group by origin having count(origin) > {0:d} order by count(origin);'.format(min_flights))
        bestairports = np.array(cur.fetchall()).reshape(-1)
        bestairports_str = '"'+'","'.join(bestairports)+'"'
        conditional_str = 'origin in ({bestairports}) and dest in ({bestairports})'.format(bestairports=bestairports_str)
        print "Figured out which airports are good in {0:.2f}s".format(time.time()-start)
        
        #Iterate through each month and hour combo -it's actually fastest to downsample the whole dataset each time, because it takes awhile to populate each new database:
        for monthkey in months.keys():
            for hourkey in hours.keys():
                start = time.time()
                shard_table = 'flightdelays_{month}_{time}'.format(month=monthkey,time=hourkey)
                cur.execute('drop table if exists {0:s}'.format(shard_table))
                #Create the shard:
                cur.execute('create table {shard_table} select * from flightdelays where month(flightdate) = {month} and crsdeptime >= {hourmin} and crsdeptime < {hourmax} and {bestairports_cond};'.format(shard_table=shard_table,month=months[monthkey],hourmin=hours[hourkey][0],hourmax=hours[hourkey][1],bestairports_cond=conditional_str))
                #Make sure it knows it can still use the fid as the primary key:
                cur.execute('alter table {shard_table} add primary key(fid);'.format(shard_table=shard_table))
                print monthkey,hourkey, "Took {0:.2f}".format(time.time()-start)
                
    except mdb.Error, e:
        print "Error %d: %s" % (e.args[0],e.args[1])
        sys.exit(1)
    finally:
        if con:
            con.close()
        
