import MySQLdb as mdb
import sys
import numpy as np
import glob

import load_credentials_nogit as creds

if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("Syntax: [list of files to be loaded into the DB (or 'all')] ['add or 'reset']")

    #Load in the files to be put in the DB
    filelist = []
    if sys.argv[1].lower() == 'all':
        filelist = glob.glob("*.csv")
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
        con = mdb.connect(host=creds.host,user=creds.user,db=creds.database,passwd=creds.password)
        cur = con.cursor()
        #If the user wants to restart, drop the db:
        if op_type == 'reset':
            cur.execute('drop table if exists flightdelays')
            cur.execute("""create table flightdelays(fid int not null auto_increment primary key,
            year int,
            quarter int,
            month int,
            dayofmonth int,
            dayofweek int,
            flightdate date,
            uniquecarrier varchar(10),
            airlineid int,
            tailnum varchar(7),
            flightnum varchar(10),
            originairportid int,
            origincitymarketid int,
            origin varchar(10),
            origincityname varchar(255),
            originstate varchar(5),
            originstatename varchar(255),
            destairportid int,
            destcitymarketid int,
            dest varchar(10),
            destcityname varchar(255),
            deststate varchar(5),
            deststatename varchar(255),
            crsdeptime varchar(4),
            deptime varchar(4),
            depdelay float,
            taxiout float,
            wheelsoff varchar(4),
            wheelson varchar(4),
            taxiin float,
            crsarrtime varchar(4),
            arrtime varchar(4),
            arrdelay float,
            cancelled float,
            cancellationcode varchar(5),
            diverted float,
            distance float,
            carrierdelay float not null default -1.,
            weatherdelay float not null default -1.,
            nasdelay float not null default -1.,
            securitydelay float not null default -1.,
            lateaircraftdelay float not null default -1.
            )""")

        for i,filename in enumerate(filelist):
            print filename
            cur.execute('''load data local infile "{0:s}" into table flightdelays fields terminated by "," optionally enclosed by """" ignore 1 lines(
            year,quarter,month,dayofmonth,dayofweek,@datevar,uniquecarrier,airlineid,@dummy,tailnum,flightnum,originairportid,@dummy,origincitymarketid,origin,origincityname,originstate,@dummy,originstatename,@dummy,destairportid,@dummy,destcitymarketid,dest,destcityname,deststate,@dummy,deststatename,@dummy,crsdeptime,deptime,depdelay,@depdelayminutes,@depdel15,@departuredelaygroups,@deptimeblk,taxiout,wheelsoff,wheelson,taxiin,crsarrtime,arrtime,arrdelay,@arrdelayminutes,@arrdelay15,@arrivaldelaygroups,@arrtimeblk,cancelled,cancellationcode,diverted,@crselapsedtime,@actualelapsedtime,@airtime,@flights,distance,@distancegroup,@carrierdelay,@weatherdelay,@nasdelay,@securitydelay,@lateaircraftdelay,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy)
            set flightdate=STR_TO_DATE(@datevar, '%Y-%m-%d'),
            carrierdelay = ifnull(nullif(@carrierdelay,''),-1.),
            weatherdelay = ifnull(nullif(@weatherdelay,''),-1),
            nasdelay = ifnull(nullif(@nasdelay,''),-1),
            securitydelay = ifnull(nullif(@securitydelay,''),-1),
            lateaircraftdelay = ifnull(nullif(@lateaircraftdelay,''),-1)
            '''.format(filename))
            # cur.execute('''load data local infile "{0:s}" into table flightdelays fields terminated by "," optionally enclosed by """" ignore 1 lines(
            # year,quarter,month,dayofmonth,dayofweek,@datevar,uniquecarrier,airlineid,@dummy,tailnum,flightnum,originairportid,@dummy,origincitymarketid,origin,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy,@dummy)
            # set flightdate=STR_TO_DATE(@datevar, '%Y-%m-%d')'''.format(filename))
            con.commit()

    except mdb.Error, e:
        print "Error %d: %s" % (e.args[0],e.args[1])
        sys.exit(1)
    finally:
        if con:
            con.close()
        
