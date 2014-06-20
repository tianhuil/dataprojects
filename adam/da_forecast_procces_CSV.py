import csv
import pandas as pd
import numpy as np
from numpy import *

zones = ['RTO','MIDATL','APS','COMED','DAY','DUQ','DOM']
yrs = [2011,2012,2013, 2014]

comb_loads =[]
dateVals = []
hourVals = []

for zcnt in range(len(zones)):
    zonalLoad = []
    for yr in yrs:
        print yr
        raw_csv =  'raw_csv/%s%i.csv' %(zones[zcnt],yr)
        df = pd.read_csv(raw_csv)
        for cnt in range( 3,len(df),8):  #here I need to just get right days
            if zcnt == 0:
                hourVals = np.append( hourVals, arange(1,25) ) 
                dateVals = np.append( dateVals, repeat( df[cnt:cnt+1].values[0][1:2],24) )
            zonalLoad = np.append( zonalLoad , df[cnt:cnt+1].values[0][2:27])
    if zcnt == 0:
        comb_loads = zonalLoad
    else:
        comb_loads = np.vstack( [comb_loads, zonalLoad] )
comb_loads = np.vstack([ dateVals, hourVals, comb_loads] )

f = open("model_data/lf_hist.csv", 'a')
writer = csv.writer(f)
comb_loads = comb_loads.T
print 'dates', zones
writer.writerow(np.append('day',np.append('hour', zones)) )
for row in comb_loads:
    print row
    writer.writerow(row)
f.close()


#snippit for putting the data into timeseries and plotting
#import matplotlib.pyplot as plt
#%matplotlib inline
#df = pd.read_csv( 'lf_hist.csv')
#a=  df.values[:][:,0]
#b= (df.values[:][:,2].astype(int)-1).astype(str) #HE indexing
#dt = pd.to_datetime( a +' ' +b + ':00')
#ts = pd.Series( df.values[:][:,2], dt)
#ts.plot()
