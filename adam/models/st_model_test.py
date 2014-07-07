import pandas as pd
import csv
from numpy import *
import sklearn
import numpy as np
from sklearn import linear_model
from scipy import stats
import matplotlib.pyplot as plt
import time
from sklearn import cross_validation
from sklearn.ensemble import RandomForestClassifier
import copy
pd.options.mode.chained_assignment = None  # default='warn'

start_time = time.time()
data_lag  = 48
bucketSize = 24 #how many hours to group

raw_data = pd.read_csv('processed_Df.csv', parse_dates= ['date'], index_col='date')

y_temp = raw_data['BGEDAe'] - raw_data['BGERTe'] - abs(raw_data['OPRES'])
#y_temp = raw_data['APSDAe'] - raw_data['APSRTe'] - abs(raw_data['OPRES'])
#y_temp = raw_data['WESTERN HUBDAe'] - raw_data['WESTERN HUBRTe'] - abs(raw_data['OPRES'])

lfInds = [0,1,2,4,6]
eInds = []#14
X_temp = raw_data.iloc[:,lfInds +eInds]
X_temp.iloc[:,range(len(lfInds ))] =X_temp.iloc[:,range(len(lfInds ))]/1000


X_temp['shift'] = y_temp.shift( data_lag ).fillna(0)
X_temp['WH_recent'] = raw_data['WESTERN HUBDAe'].shift(24).fillna(0)

y_temp = pd.stats.moments.rolling_mean(y_temp, bucketSize )
X_temp = pd.stats.moments.rolling_mean(X_temp, bucketSize )

X = X_temp.iloc[bucketSize::bucketSize,:]
y = y_temp.iloc[bucketSize::bucketSize]

#now divide the data into blocks of d days for regression and 1 day for testing
reg_days = 15 #30 worked well
reg_time = 24/bucketSize * reg_days # how many points to regress
curr_date = data_lag/bucketSize # need to start 48 hours in so you have realistic data
#clf = linear_model.Ridge(alpha=.1)
clf = RandomForestClassifier(n_estimators=8, max_depth =3,min_samples_split =5, verbose=0)#verbose =3 for info
y_pred= []
y_act = []

curr_date = curr_date + 0
end_dt_adj = 400

while (curr_date + reg_time + 24/bucketSize ) < len(X - end_dt_adj):
    X_train = X.iloc[ curr_date:curr_date+reg_time, : ]
    X_test  = X.iloc[ curr_date+reg_time:curr_date+reg_time+24/bucketSize, : ]
    y_train = y[ curr_date:curr_date+reg_time ]  
    y_test  = y[ curr_date+reg_time:curr_date+reg_time+24/bucketSize ]
    clf.fit(X_train, y_train )
    y_act.append( y_test[0] )
    y_pred.append(clf.predict(X_test)[0])
    curr_date = curr_date + 24/bucketSize

y_pred = array(y_pred )
y_act  = array(y_act )

y_adj_pred = copy.deepcopy(y_act)
y_adj_pred[ abs(y_pred) > 1 ] = 0

y_adj_pred2 = copy.deepcopy(y_act)                
y_adj_pred2[ y_pred < 0 ] = 0                                                

print 'MSE Prct=%.2f' % ( sum( (y_act - y_pred)**2 )/ sum(y_act**2))
print 'MSE Prct=%.2f' % ( sum( (y_act - y_adj_pred)**2 )/ sum(y_act**2))
print 'MSE Prct=%.2f' % ( sum( (y_act - y_adj_pred2)**2 )/ sum(y_act**2))



print mean(y_act)
print sum( y_act[y_pred>0] )/len(y_act )
print sum( y_act[abs(y_pred)<1] )/len(y_act )

plt.figure(1)
plt.plot( pd.stats.moments.rolling_mean( y_adj_pred, 30 ) )
plt.plot( pd.stats.moments.rolling_mean( y_adj_pred2, 30 ) )
plt.plot( pd.stats.moments.rolling_mean( y_act, 30 ) )

plt.figure(2)
plt.hist([y_act[30::30], y_adj_pred[30::30] ] , bins = 30)

plt.show()


end_time = time.time()
print("Elapsed time was %g seconds" % (end_time - start_time))