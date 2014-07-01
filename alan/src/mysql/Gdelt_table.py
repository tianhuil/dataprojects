import os
import MySQLdb as mysql

Conn = mysql.connect(host = "localhost",
                     user = "incubator",
                     db = "Commodities")
Conn.autocommit(True)

cmds = ["""DROP TABLE IF EXISTS EVENTS{year};""",
"""CREATE TABLE EVENTS{year} (GLOBALEVENTID  int primary key,
        SQLDATE int, Actor1Code varchar(13),
	Actor2Code varchar(13), IsRootEvent bool,
	EventCode float, GoldsteinScale float,
	NumMentions smallint, AvgTone float, 
	Geo_Type_1 int, Geo_CountryCode_1 varchar(3),
        Geo_ADM1Code_1 varchar(5), Geo_Lat_1 float,
        Geo_Long_1 float, 
	Geo_Type_2 int, Geo_CountryCode_2 varchar(3),
        Geo_ADM1Code_2 varchar(5), Geo_Lat_2 float,
        Geo_Long_2 float);
"""
]
for year in range(2000,2015):
    for cmd in cmds:
        print cmd.format(year=year)
        Conn.cursor().execute(cmd.format(year=year))
        Conn.commit()
    
    
