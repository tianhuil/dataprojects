import csv,requests, StringIO
import zipfile
import pandas as pd
import numpy as np
from numpy import *
import datetime as dt

zones = ['WESTERN HUB', 'APS','COMED','DAY','DUQ','DOM','BGE']
#set-up dates
start_date = dt.date(2014,1,1)
end_date = dt.date(2014, 6,5)
zipcutoff = dt.date(2014, 3, 18 ) #this is a date where they start zipping
dates = []
d = start_date
delta = dt.timedelta(days=1)

header = append( 'date', zones )
f1 = open("model_data/ml_RTx.csv", 'a')
f2 = open("model_data/cong_RTx.csv", 'a')
f3 = open("model_data/energy_RTx.csv", 'a')
writer1 = csv.writer(f1)
writer2 = csv.writer(f2)
writer3 = csv.writer(f3)

while d<= end_date:
    formDate = d.strftime("%Y%m%d")
    print formDate
    if d > zipcutoff:
        url = 'http://www.pjm.com/pub/account/lmp/%s.csv' %formDate 
        rawLMP = pd.read_csv( url )
    else:
        url = 'http://www.pjm.com/pub/account/lmp/%s.zip' %formDate
        r = requests.get(url)
        z = zipfile.ZipFile(StringIO.StringIO(r.content))
        csvFile = '%s.csv' %formDate
        rawLMP  = pd.read_csv( z.open( csvFile ) )        
    zonalLMP = rawLMP[7:60]
    zcnt = 0
    for zone in zones:
        zoneLoc = nonzero(zonalLMP.values[:][:][:,2:3] == zone)
        if zcnt == 0:
            dayLMP = (zonalLMP.values[:][zoneLoc[0][0]:zoneLoc[0][0]+1]).T
        else:
            dayLMP = hstack( [ dayLMP, (zonalLMP.values[:][zoneLoc[0][0]:zoneLoc[0][0]+1]).T]  )
        zcnt = zcnt + 1
    for hcnt in range(len((dayLMP)[9:80:3] )):
        y1 = list((dayLMP)[9+3*hcnt] )
        y2 = list((dayLMP)[8+3*hcnt] )
        y3 = list((dayLMP)[7+3*hcnt] )
        y1.insert(0, formDate )
        y1.insert(1,hcnt)
        y2.insert(0, formDate )
        y2.insert(1,hcnt)
        y3.insert(0, formDate )
        y3.insert(1,hcnt)
        writer1.writerow( y1 )
        writer2.writerow( y2 )
        writer3.writerow( y3 )
    d += delta
    
f1.close()
f2.close()
f3.close()
print "success"
