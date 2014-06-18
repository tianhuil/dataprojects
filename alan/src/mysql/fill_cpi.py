import numpy as np
import sys
import MySQLdb as mysql
import pylab as plt

sys.path.append('../')
import settings 
import scipy.interpolate as interp


Conn = mysql.connect(host = settings.host,
                     user = settings.user,
                     db = settings.db)
Conn.autocommit(True)

cursor = Conn.cursor()

cmd = 'select distinct a.JulianDate from ('

union_tabs = [ ' select juliandate from %s ' %a for a in settings.to_use]
cmd += ' UNION '.join(union_tabs) + ') as a left join  cpi as b on a.juliandate = b.juliandate and b.juliandate is null order by a.juliandate;'

print cmd
cursor.execute(cmd)

days =  np.array([a[0] for a in cursor.fetchall()])
print days

cmd = 'select juliandate, value from cpi order by juliandate;'
print cmd
cursor.execute(cmd)

cpi =  np.array(cursor.fetchall())
print cpi

interp_cpi = interp.splrep(cpi[:,0], cpi[:,1])

outcpi = interp.splev(days, interp_cpi)

print outcpi

plt.scatter(cpi[:,0], cpi[:,1])
plt.plot(days, outcpi)

plt.show()


cursor.executemany("""INSERT IGNORE INTO cpi (juliandate, value)
      VALUES (%s, %s)""", zip(days, outcpi))
