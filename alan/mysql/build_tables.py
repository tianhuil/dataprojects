import os
import zipfile
import MySQLdb as mysql
import time

Conn = mysql.connect(host = "localhost",
                     user = "incubator",
                     db = "Commodities")
Conn.autocommit(False)

infile = '../data/gdelt_files/CSV.header.historical.txt'

infile = open(infile)
data = infile.readline()
infile.close()


def insert_row(Conn, row, table, altabs):
    row = ['"'+a[0]+'"' if "varchar" in a[1][1] else a[0] for a in zip(row, altabs[table]) ] 
    
    cmd = 'insert ignore into %s values (%s);' %(table, ','.join(row))
    #print cmd
    Conn.cursor().execute(cmd)
    return



cols = [(b,a) for a,b in enumerate(data.strip().split('\t'))]

coldict = dict(cols)

print coldict

tables={
    'EVENTS':[('GLOBALEVENTID','int primary key'), 
              ('SQLDATE','int'),
              ('Actor1Code', 'varchar'), 
              ('Actor2Code', 'varchar'),
              ('IsRootEvent', 'bool'), 
              ('EventCode', 'varchar(4)'), 
              ('QuadClass','int'),
              ('GoldsteinScale', 'float'), 
              ('NumMentions', 'smallint'), 
              ('NumSources', 'smallint'), 
              ('NumArticles', 'smallint'), 
              ('AvgTone', 'float'),
              ('DATEADDED','int')],

    'ACTORS':[('ActorCode','varchar() primary key'),
              ('ActorName','varchar()'),
              ('ActorCountryCode','varchar(3)'),
              ('ActorKnownGroupCode', 'varchar()'),
              ('ActorEthnicCode', 'varchar()')],
    'ACTOR_RELIGIONS':[('ActorCode','varchar() primary key()'),
                       ('ActorReligionCode','varchar()')
                       ],
    'ACTOR_TYPES':[('ActorCode','varchar() primary key()'),
                   ('ActorTypeCode','varchar()')],
    'EVENT_ACTOR_GEO':[('GLOBALEVENTID','int'), #unique key pair with actor num
                     ('ActorNum', 'tinyint'), #unique key pair 
                     ('Geo_Type', 'int'),
                     ('Geo_CountryCode', 'varchar(2)'),
                     ('Geo_ADM1Code', 'varchar(4)'),
                     ('Geo_Lat', 'float'),
                     ('Geo_Long', 'float'),
                     ('Geo_FeatureID', 'int')]
                     }
    
event_cols = [a[0] for a in tables['EVENTS']]
geo_cols = [a[0] for a in tables['EVENT_ACTOR_GEO']]
actor_cols = ['Actor{num}Code','Actor{num}Name','Actor{num}CountryCode',
              'Actor{num}KnownGroupCode', 'Actor{num}EthnicCode']
actor_reg_cols = ['Actor{num}Code', 'Actor{num}Religion{regnum}Code']
actor_type_cols = ['Actor{num}Code','Actor{num}Type{typenum}Code' ]


os.system('ls /home/ameert/git_projects/dataprojects/alan/data/gdelt_files/2*.zip> zipfiles.txt')

zipfiles = open('zipfiles.txt').readlines()
#zipfiles = ['/home/ameert/git_projects/dataprojects/alan/data/gdelt_files/test.zip',]
for inzip in zipfiles:
    inzip = inzip.strip()
    infile = zipfile.ZipFile(inzip, "r")
    csvfile = inzip.split('/')[-1].replace('.zip','.csv')

    for line in infile.read(csvfile).split("\n"):
        try:
            row =line.strip().split('\t')
            row = ['-99' if a=='' else a for a in row] 

            event_row = [row[coldict[a]] for a in event_cols]
            insert_row(Conn, event_row, 'EVENTS', tables)

            for count in [1,2]:
                actor_row = [row[coldict[b]] for b in [a.format(num=count) for a in actor_cols]]
                insert_row(Conn, actor_row, 'ACTORS', tables)
            
                for reg_count in [1,2]:
                    reg_row = [row[coldict[b]] for b in [a.format(num=count, regnum=reg_count) for a in actor_reg_cols]]
                    insert_row(Conn, reg_row, 'ACTOR_RELIGIONS', tables)

                for type_count in [1,2,3]:
                    type_row = [row[coldict[b]] for b in [a.format(num=count, typenum=type_count) for a in actor_type_cols]]
                    insert_row(Conn, type_row, 'ACTOR_TYPES', tables)

            for count in [1,2]:
                geo_row = [row[coldict[geo_cols[0]]], str(count)]+[row[coldict["Actor%d%s"%(count,b)]] for b in geo_cols[2:]]
                insert_row(Conn, geo_row, 'EVENT_ACTOR_GEO', tables)
                
        except IndexError:
            pass

    infile.close()
    Conn.commit()

    print inzip+ ' LOADED!!!'
    print "sleeping for 10 seconds to allow graceful kill"
    time.sleep(10)
    
    


"""
"CREATE TABLE , 

, 'Actor1Geo_Type', 'Actor1Geo_FullName', 'Actor1Geo_CountryCode', 'Actor1Geo_ADM1Code', 'Actor1Geo_Lat', 'Actor1Geo_Long', 'Actor1Geo_FeatureID', 'Actor2Geo_Type', 'Actor2Geo_FullName', 'Actor2Geo_CountryCode', 'Actor2Geo_ADM1Code', 'Actor2Geo_Lat', 'Actor2Geo_Long', 'Actor2Geo_FeatureID', 'ActionGeo_Type', 'ActionGeo_FullName', 'ActionGeo_CountryCode', 'ActionGeo_ADM1Code', 'ActionGeo_Lat', 'ActionGeo_Long', 'ActionGeo_FeatureID', 'DATEADDED'"
"""
