import os
import zipfile
import MySQLdb as mysql
import time
import warnings
warnings.filterwarnings('ignore', category=mysql.Warning)

Conn = mysql.connect(host = "localhost",
                     user = "incubator",
                     db = "Commodities")
Conn.autocommit(False)

def insert_row(Conn, row, table, altabs):
    row = ['"'+a[0]+'"' if "varchar" in a[1][1] else a[0] for a in zip(row, altabs[table]) ] 
    
    #cmd = 'insert ignore into %s values (%s);' %(table, ','.join(row))
    #print cmd
    #Conn.cursor().execute(cmd)
    return '('+','.join(row)+')'

loadstep = 10000

tables={
    'EVENTS':[('GLOBALEVENTID','int primary key',0), 
              ('SQLDATE','int',1),
              ('Actor1Code', 'varchar(13)',5), 
              ('Actor2Code', 'varchar(13)',15),
              ('IsRootEvent', 'bool',25), 
              ('EventCode', 'int',26), 
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


os.system('ls /home/ameert/git_projects/dataprojects/alan/data/gdelt_files/201*.zip> zipfiles.txt')

zipfiles = open('zipfiles.txt').readlines()
#zipfiles = ['/home/ameert/git_projects/dataprojects/alan/data/gdelt_files/200601.zip',]
for inzip in zipfiles:
    print "Loading %s" %inzip
    inzip = inzip.strip()
    infile = zipfile.ZipFile(inzip, "r")
    csvfile = inzip.split('/')[-1].replace('.zip','.csv')
    
    cmd = 'insert ignore into EVENTS values '
    count = 0
    tot_load =0
    for line in infile.read(csvfile).split("\n"):
#        if "42.1497" not in line:
#            continue
        try:
            if count > loadstep:
                tot_load+=loadstep
                cmd = cmd.replace('---','NULL')
                cmd = cmd[:-1]+';'
                Conn.cursor().execute(cmd)
                Conn.commit()
                count = 0
                cmd = 'insert ignore into EVENTS values '
                print tot_load, ' loaded'
            count +=1
            row = line.replace(r'/',' ')
            row =line.strip().split('\t')
            row = ['NULL' if a=='' else a for a in row] 
            row = ['NULL' if a=='X' else a for a in row] 
            event_row= [row[a[2]] for a in tables['EVENTS']]
            cmd += insert_row(Conn, event_row, 'EVENTS', tables)+','
#        except IndexError:
#            pass
        except:
            print "bad group ",tot_load
            print cmd 
            break
    
    infile.close()
    cmd = cmd.replace('---','NULL')
    cmd = cmd[:-1]+';'        
    Conn.cursor().execute(cmd)
    Conn.commit()

    print inzip+ ' LOADED!!!'
    print "sleeping for 10 seconds to allow graceful kill"
    time.sleep(10)
    
    


"""
"CREATE TABLE , 

, 'Actor1Geo_Type', 'Actor1Geo_FullName', 'Actor1Geo_CountryCode', 'Actor1Geo_ADM1Code', 'Actor1Geo_Lat', 'Actor1Geo_Long', 'Actor1Geo_FeatureID', 'Actor2Geo_Type', 'Actor2Geo_FullName', 'Actor2Geo_CountryCode', 'Actor2Geo_ADM1Code', 'Actor2Geo_Lat', 'Actor2Geo_Long', 'Actor2Geo_FeatureID', 'ActionGeo_Type', 'ActionGeo_FullName', 'ActionGeo_CountryCode', 'ActionGeo_ADM1Code', 'ActionGeo_Lat', 'ActionGeo_Long', 'ActionGeo_FeatureID', 'DATEADDED'"
"""
