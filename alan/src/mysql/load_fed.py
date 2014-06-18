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

filenames = ['CPI.txt',  'GDP.txt',  'Population.txt',  'rec_prob.txt',
             'stress_ind.txt',  'um_sent.txt']


for name in filenames:
    data = np.loadtxt(data_path+name, unpack=True)
    sqldate = ['%04d%02d%02d' %(int(a[0]),int(a[1]),int(a[2])) for a in zip(data[0],data[1],data[2])]
    
    values = ','.join(['('+','.join([str(b) for b in a]) +')' for a in zip(sqldate, data[3])])
    cmd = 'insert ignore into %s values %s;' %(name.split('.txt')[0], values)
    cursor.execute(cmd)
