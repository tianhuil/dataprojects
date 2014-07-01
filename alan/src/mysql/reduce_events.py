import numpy as np
import pylab as pl
import MySQLdb as mysql
import time
import warnings
warnings.filterwarnings('ignore', category=mysql.Warning)

import sys
sys.path.append('../')
import settings

Conn = mysql.connect(host = settings.host,
                     user = settings.user,
                     db = settings.db)
Conn.autocommit(True)
cursor = Conn.cursor()


for event in [18,19]:
    cmd = "DROP TABLE IF EXISTS EVENT{event}country;".format(event=event)
    print cmd
    cursor.execute(cmd)
    cmd = "CREATE TABLE EVENT{event}country (SQLDATE int, Geo_CountryCode_1 varchar(3), Geo_CountryCode_2 varchar(3),numevents int);".format(event=event)
    print cmd
    cursor.execute(cmd)

    for year in range(2000, 2014):
        cmd = "insert into EVENT{event}country select SQLDATE, Geo_CountryCode_1, Geo_CountryCode_2, count(*) from EVENTS{year} where floor(EventCode) = {event} and (Geo_CountryCode_1 in ('US', 'IR', 'SA','NO','NI', 'RS', 'JA', 'KS','GM','FR') and Geo_CountryCode_2 in ('US', 'IR', 'SA','NO','NI', 'RS', 'JA', 'KS','GM','FR')) group by SQLDATE, Geo_CountryCode_1,Geo_CountryCode_2;".format(event=event, year=year)
        print cmd
        cursor.execute(cmd)
