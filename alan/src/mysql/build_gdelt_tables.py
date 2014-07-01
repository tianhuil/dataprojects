import os
import zipfile
import MySQLdb as mysql
import time
import warnings
import traceback

warnings.filterwarnings('ignore', category=mysql.Warning)

import sys
sys.path.append('../')
import settings 

data_path = settings.project_path + 'data/gdelt_files'

Conn = mysql.connect(host = settings.host,
                     user = settings.user,
                     db = settings.db)
Conn.autocommit(False)

def insert_row(Conn, row, table, altabs):
    row = ['"'+a[0]+'"' if "varchar" in a[1][1] else a[0] for a in zip(row, altabs[table]) ]     
    return '('+','.join(row)+')'

loadstep = 10000

tables={
    'EVENTS':[('GLOBALEVENTID','int primary key',0), 
              ('SQLDATE','int',1),
              ('Actor1Code', 'varchar(13)',5), 
              ('Actor2Code', 'varchar(13)',15),
              ('IsRootEvent', 'bool',25), 
              ('EventCode', 'float',26), 
              ('GoldsteinScale', 'float',30), 
              ('NumMentions', 'smallint',31), 
              ('AvgTone', 'float',34),
              ('Geo_Type_1', 'smallint',35),
              ('Geo_CountryCode_1', 'varchar(3)',37),
              ('Geo_ADM1Code_1', 'varchar(3)',38),
              ('Geo_Lat_1', 'float',39),
              ('Geo_Long_1', 'float',40),
              ('Geo_Type_2', 'smallint',42),
              ('Geo_CountryCode_2', 'varchar(3)',44),
              ('Geo_ADM1Code_2', 'varchar(3)',45),
              ('Geo_Lat_2', 'float',46),
              ('Geo_Long_2', 'float',47)]
    }
    
event_cols = [a[0] for a in tables['EVENTS']]


os.system('ls %s/20*.zip> zipfiles.txt' %data_path)

zipfiles = open('zipfiles.txt').readlines()
for inzip in zipfiles:
    print "Loading %s" %inzip
    inzip = inzip.strip()
    infile = zipfile.ZipFile(inzip, "r")
    csvfile = inzip.split('/')[-1].replace('.zip','.csv')

    year = int(inzip.split('/')[-1].split('.zip')[0][:4])
    print "year ", year
    cmd = 'insert ignore into EVENTS%d values ' %year
    count = 0
    tot_load =0
    for line in infile.read(csvfile).split("\n"):
        try:
            if count > loadstep:
                tot_load+=loadstep
                cmd = cmd.replace('---','NULL')
                cmd = cmd[:-1]+';'
                Conn.cursor().execute(cmd)
                Conn.commit()
                count = 0
                cmd = 'insert ignore into EVENTS%d values ' %year
                print tot_load, ' loaded'
            count +=1
            row = line.replace(r'/',' ')
            row = row.replace('---','NULL')
            row =line.strip().split('\t')
            row = ['NULL' if a=='' else a for a in row] 
            row = ['NULL' if a=='X' else a for a in row] 
            event_row= [row[a[2]] for a in tables['EVENTS']]
            # add a decimal to the event code
            try:
                float(event_row[5])
                event_row[5] =event_row[5][:2]+'.'+event_row[5][2:]
            except:
                pass                
            cmd += insert_row(Conn, event_row, 'EVENTS', tables)+','
        except Exception, err:
            print Exception, err
            print "bad group ",tot_load
            
    infile.close()
    cmd = cmd[:-1]+';'        
    Conn.cursor().execute(cmd)
    Conn.commit()

    print inzip+ ' LOADED!!!'
    print "sleeping for 10 seconds to allow graceful kill"
    time.sleep(10)

statusfile = open(settings.gdelt_sql, 'w')
statusfile.write('GDelt data Successfully loaded to SQL!')
statusfile.close()
