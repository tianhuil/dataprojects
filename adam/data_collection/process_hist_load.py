import csv
import urllib2
import StringIO 
import numpy as np
from numpy import *

st_yr  = 2008
end_yr = 2014
header = ['DAY', 'HOUR', 'PJME', 'PJMW', 'COMED', 'DAYTON', 'AEP', 'DUQ' ]

f = open("model_data/load_hist.csv", 'a')
writer = csv.writer(f)
yrs = arange(st_yr,end_yr + 1) 
for cnt in yrs:
    url = "http://www.pjm.com/pub/account/loadhryr/%i.txt" %cnt
    response = urllib2.urlopen(url)
    cr = csv.reader(response)
    rcnt = 0
    for row in cr:
        #need this to account for non standard files
        if rcnt  == 0:
            if cnt == st_yr:
                writer.writerow( header )
            print row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]
            rcnt = rcnt + 1
        else:
            writer.writerow([row[0], row[1], row[2], row[3], row[4], row[5], row[6],row[7]])
f.close()
