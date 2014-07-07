import csv,requests, StringIO
import zipfile
import urllib2
import pandas as pd
import numpy as np
from numpy import *
import datetime as dt
import dateutil

#set-up dates
start_date = dt.date(2014,3,1)
end_date = dt.date(2014, 6,20)
dates = []
d = start_date
delta = dt.timedelta(days=30)

header = append( 'date', 'opres' )
f1 = open("model_data/orpes_histx.csv", 'a')
writer = csv.writer(f1)

totDays = 0
totOpres = 0

while d<= end_date:
    formDate = d.strftime("%Y%m")
    #print formDate
    url = 'http://www.pjm.com/pub/account/oper-reserve-rates/monthly/%s.csv' %formDate 
    response = urllib2.urlopen(url)
    raw_opres = csv.reader(response)
    rcnt = 0
    for row in raw_opres:
        if rcnt >3:
            if (row[0] != 'End of Report'):
                totDays = totDays + 1
                totOpres = totOpres +  float(row[7])
                #print row
                print row[0],row[7]
                for hcnt in range(24 ):
                    writer.writerow([row[0],str(hcnt), row[7]])  
        rcnt = rcnt + 1
    d += delta
f1.close()
print "success"

print totOpres/totDays
