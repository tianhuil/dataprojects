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

data_path = settings.project_path +'data/st_louis_fed/'

if __name__=="__main__":
    for tab in settings.fed_series.values():
        cursor.execute('DROP TABLE IF EXISTS %s;' %tab)
        cursor.execute('CREATE TABLE %s (SQLDATE int primary key, value float);' %tab)
        data = np.loadtxt(data_path+tab+'.txt', unpack=True)
        sqldate = ['%04d%02d%02d' %(int(a[0]),int(a[1]),int(a[2])) for a in zip(data[0],data[1],data[2])]
    
        values = ','.join(['('+','.join([str(b) for b in a]) +')' for a in zip(sqldate, data[3])])
        cmd = 'insert ignore into %s values %s;' %(tab, values)
        cursor.execute(cmd)

    
statusfile = open(settings.fed_sql, 'w')
statusfile.write('Fed Data data Successfully loaded to SQL!')
statusfile.close()
