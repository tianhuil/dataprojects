import sys
import MySQLdb as mysql
import datetime
import numpy as np
import os

sys.path.append('../')
import settings 

datapath = '%s/data/quandl/' %settings.project_path

Conn = mysql.connect(host = settings.host,
                     user = settings.user,
                     db = settings.db)
Conn.autocommit(False)


stock_cols=[ ('SQLDATE','int primary key'), 
             ('open', 'float'), 
             ('high', 'float'),
             ('low', 'float'), 
             ('last', 'float'),
             ('diff', 'float'),
             ('settle', 'float'), 
             ('volume','float'),
             ('open_interest', 'float')]

all_tabs = dict([(a,stock_cols) for a in settings.to_use])


def insert_rows(Conn, indat, table, altabs):
    cmd = 'insert ignore into %s values ' %(table)
    allrow = []
    for row in indat:
        row = [str(a) for a in row]
        row = [ '"'+a[0]+'"' if "varchar" in a[1][1] else a[0] for a in zip(row, altabs[table])] 
        allrow.append( '('+','.join(row)+')')
    cmd += ','.join(allrow) + ';'
    cmd = cmd.replace('nan', '-999')
    #print cmd
    Conn.cursor().execute(cmd)
    return


for tabname in settings.to_use:
    cmd ='DROP TABLE IF EXISTS %s;' %tabname
    Conn.cursor().execute(cmd)
    print cmd

    cmd ='CREATE TABLE IF NOT EXISTS %s (' %tabname
    cmd += ','.join([' '.join(a) for a in stock_cols])
    cmd += ');'
    Conn.cursor().execute(cmd)
    Conn.commit()
    print cmd



    os.system("""mysql -u {usr} {dba} -e "LOAD DATA INFILE '{datapath}/{stock}.csv' INTO TABLE {stock} FIELDS TERMINATED BY ',' IGNORE 1 LINES;" """.format(datapath=datapath, stock = tabname, usr=settings.user, dba=settings.db))






