import MySQLdb as mdb
import sys
import numpy as np
import glob
import zipfile
#import pandas as pd
import os

import load_credentials_nogit as creds

if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("Syntax: [list of files to be loaded into the DB (or 'all')] ['add or 'reset']")

    #Load in the files to be put in the DB
    filelist = []
    if sys.argv[1].lower() == 'all':
        filelist = glob.glob("*.[cz][si][vp]")
    else:
        filelist = np.loadtxt(sys.argv[1],dtype=np.str,usecols=(0,),ndmin=1)
    filelist = np.array(filelist)


    #Check that there is at least one file:
    if len(filelist) == 0:
        raise IOError("No files in list!")

    #Check that the user wants to either append or overwrite the database:
    op_type = sys.argv[2].lower()
    if op_type != 'add' and op_type != 'reset':
        raise IOError("Operation type must be either 'add' or 'reset'")

    #Connect to the db:
    con = ''
    try:
        con = mdb.connect(host=creds.host,user=creds.user,db=creds.database,passwd=creds.password,local_infile=1)
        cur = con.cursor()
        #If the user wants to restart, drop the dbs:
        if op_type == 'reset':
            cur.execute('drop table if exists flightdelays')
            cur.execute("""create table flightdelays(fid int not null auto_increment primary key,
            flightdate date not null default '0000-00-00',
            uniquecarrier varchar(7) not null default '-9999',
            tailnum varchar(6) not null default 'ZZZZZZ',
            origincitymarketid mediumint not null default -1,
            origin varchar(3) not null default '-1',
            originstate varchar(2) not null default '-1',
            destcitymarketid mediumint not null default -1,
            dest varchar(3) not null default '-1',
            deststate varchar(2) not null default '-1',
            crsdeptime varchar(4) not null default '-999',
            depdelay float not null default -9999.,
            crsarrtime varchar(4) not null default '-999',
            arrdelay float not null default -9999.,
            cancelled float not null default -1,
            diverted float not null default -1,
            distance float not null default -1
            )""")

        for i,filename in enumerate(filelist):
            deletefile_atend = False
            if os.path.splitext(filename)[1] == '.zip':
                zipname = filename
                print zipname,
                zipf = zipfile.ZipFile(zipname)
                for zipped_file in zipf.infolist():
                    if os.path.splitext(zipped_file.filename)[1] == '.csv':
                        zipf.extract(zipped_file)
                        filename = zipped_file.filename
                        deletefile_atend = True
                        break
            if os.path.splitext(filename)[1] != '.csv':
                sys.exit("Could not find CSV file: came up with {0:s}".format(filename))
            print filename
            cur.execute('''load data local infile "{0:s}" into table flightdelays fields terminated by "," optionally enclosed by """" ignore 1 lines(
            @year,@quarter,@month,@dayofmonth,@dayofweek,@datevar,uniquecarrier,@airlineid,@dummy,@tailnum,@flightnum,@originairportid,@dummy,origincitymarketid,origin,@origincityname,originstate,@dummy,@originstatename,@dummy,@destairportid,@dummy,destcitymarketid,dest,@destcityname,deststate,@dummy,@deststatename,@dummy,crsdeptime,@deptime,@depdelay,@depdelayminutes,@depdel15,@departuredelaygroups,@deptimeblk,@taxiout,@wheelsoff,@wheelson,@taxiin,crsarrtime,@arrtime,@arrdelay,@arrdelayminutes,@arrdelay15,@arrivaldelaygroups,@arrtimeblk,cancelled,@cancellationcode,diverted,@crselapsedtime,@actualelapsedtime,@airtime,@flights,distance,@distancegroup,@carrierdelay,@weatherdelay,@nasdelay,@securitydelay,@lateaircraftdelay,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy)
            set flightdate=STR_TO_DATE(@datevar, '%Y-%m-%d'),
            tailnum = ifnull(nullif(@tailnum,''),'ZZZZZZ'),
            depdelay = ifnull(nullif(@depdelay,''),-9999.),
            arrdelay = ifnull(nullif(@arrdelay,''),-9999.)
            '''.format(filename))
            con.commit()
            if deletefile_atend:
                os.remove(filename)

    except mdb.Error, e:
        print "Error %d: %s" % (e.args[0],e.args[1])
        sys.exit(1)
    finally:
        if con:
            con.close()
        
