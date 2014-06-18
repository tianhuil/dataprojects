import sys
import MySQLdb as mysql
import datetime
import numpy as np

datapath = '../data/st_louis_fed/'

Conn = mysql.connect(host = "localhost",
                     user = "incubator",
                     db = "Commodities")
Conn.autocommit(False)


stock_cols=[('JulianDate','int primary key'),
             ('SQLDATE','int'), 
             ('value', 'float')]

stocknames = [ 'cpi']
all_tabs = dict([(a,stock_cols) for a in stocknames])


def insert_row(Conn, row, table, altabs):
    row = ['"'+a[0]+'"' if "varchar" in a[1][1] else a[0] for a in zip(row, altabs[table]) ] 
    
    cmd = 'insert ignore into %s values (%s);' %(table, ','.join(row))
    #print cmd
    Conn.cursor().execute(cmd)
    return


for tabname in stocknames:
    cmd ='Drop TABLE IF EXISTS %s;' %tabname
    print cmd
    Conn.cursor().execute(cmd)

    cmd ='CREATE TABLE IF NOT EXISTS %s (' %tabname
    cmd += ','.join([' '.join(a) for a in stock_cols])
    cmd += ');'
    
    print cmd
    Conn.cursor().execute(cmd)

    indat = np.loadtxt(datapath+'CPIAUCNS.txt')
    
    juldates = [datetime.date(int(a[0]),int(a[1]), int(a[2])).toordinal() for a in indat]

    mysqldate = [int('%04d%02d%02d' %(a[0],a[1], a[2])) for a in indat]

    indat = np.array(indat)[:,1:]
    indat[:,1] = np.array(mysqldate, dtype = int).T
    indat[:,0] = np.array(juldates, dtype = int).T
    for row in indat:
        row = [str(a) for a in row]
        insert_row(Conn, row, tabname, all_tabs)
        Conn.commit()

