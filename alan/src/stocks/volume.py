import numpy as np
import pylab as pl
import datetime 
import pandas as pd
import scipy.signal as signal
from sklearn import linear_model
import statsmodels.api as sm
import pickle
import pandas.io.sql as psql
import MySQLdb as mysql

import sys
sys.path.append('../')
import settings

from utils import *

Conn = mysql.connect(host = settings.host,
                     user = settings.user,
                     db = settings.db)
Conn.autocommit(True)
cursor = Conn.cursor()

from stock_returns import load_stock, date_contract, moving_average

comm_choice = settings.comm_choice
maxdays=settings.maxdays
start_date = do_date(settings.start_date)
end_date = do_date(settings.end_date)

data_path = '/home/ameert/git_projects/dataprojects/alan/data/st_louis_fed/'
stock_data = load_stock(comm_choice, start_date, end_date)

stock_data['log_ret'] = np.log(stock_data['settle']/stock_data['settle'].shift(-1))
stock_data['log_ret'] = stock_data['log_ret'].fillna(value=0)

events = psql.frame_query('select SQLDATE, count(*) as tot_events from ev0405 group by SQLDATE;',  con=Conn)
events['orddate'] = SQLdate_to_ord(events['SQLDATE'])

to_fit = pd.merge(events,stock_data,how='right', on='SQLDATE')

data =np.array(to_fit['tot_events'][:,np.newaxis]) 
yval =np.array(to_fit['log_ret'])


fig = pl.figure()
groups = to_fit.groupby('day_bins')
means= groups.mean()
period_mean =means['volume']
interest_mean =means['open_interest']
print period_mean

group_points = np.array([int(a) for a,b in groups])
#pl.scatter(group_points,np.log10(period_mean))
#pl.plot(group_points,pd.stats.moments.ewma(period_mean.apply(np.log10), span=5).values)
pl.subplot(2,2,1)
pl.scatter(group_points,np.log10(period_mean))
pl.plot(group_points,np.log10(pd.stats.moments.ewma(period_mean, span=5).values))
pl.xlabel('period')
pl.ylabel('log10 avg volume')

print means['settle']
pl.subplot(2,2,2)
pl.scatter(group_points,means['settle'].values)
pl.xlabel('period')
pl.ylabel('log10 avg settle')

pl.subplot(2,2,3)
pl.scatter(group_points,np.log10(means['Population'].values))
pl.xlabel('period')
pl.ylabel('population')
clf = linear_model.LinearRegression()
clf.fit(group_points[:,np.newaxis],np.log10(means['Population'].values))
pl.plot(group_points, clf.predict(group_points[:,np.newaxis]))

pl.subplot(2,2,4)
pl.scatter(group_points,np.log10(means['CPI'].values))
pl.ylabel('CPI')
pl.xlabel('period')


def rep_avg(a):
    return period_mean.loc[a]
def rep_avg2(a):
    return interest_mean.loc[a]

to_fit['avgVolume'] = map(rep_avg,to_fit['day_bins'].values) 
to_fit['normVolume'] = to_fit['volume'].values/to_fit['avgVolume'].values
to_fit['avginterest'] = map(rep_avg2,to_fit['day_bins'].values) 
to_fit['normInterest'] = to_fit['open_interest'].values/to_fit['avginterest'].values

print to_fit['volume']
fig2=pl.figure()
pl.subplot(2,2,1)
to_fit['normVolume'].plot(c='k')
pd.stats.moments.ewma(to_fit['normVolume'], span=30).plot()
pl.title("Normed Volume with ewma")
pl.ylabel("shares")

pl.subplot(2,2,2)
pl.scatter(to_fit['time_remaining'],to_fit['normVolume'], s=2 )
pl.title(" folded volume")
pl.ylabel("volume")
pl.xlabel("contract cycle")

pl.subplot(2,2,3)
folded_volume = to_fit['volume']/to_fit['open_interest']
pl.scatter(to_fit['time_remaining'],folded_volume, s=2)
pl.title(" folded volume/interest")
pl.ylabel("volume")
pl.xlabel("contract cycle")

pl.subplot(2,2,4)
#pl.scatter(to_fit['time_remaining'],to_fit['open_interest'].apply(np.log10), s=2)
pl.title("Interest")
pl.ylabel("log Interest")
pl.scatter(to_fit['time_remaining'],to_fit['normInterest'].apply(np.log10), s=2)
pl.subplots_adjust(hspace=0.5, wspace=0.5)
pl.figtext(0.5, 0.95, comm_choice)

pl.show()

#weird = np.where(to_fit['time_remaining'].values<0.1, 1,0)* np.where(to_fit['open_interest'].apply(np.log10).values >5.0, 1,0)

#print np.extract( weird, to_fit['SQLDATE'].values)
#print np.extract( weird,to_fit['time_remaining'].values)
#print np.extract( weird,to_fit['volume'].values)
#print np.extract( weird,to_fit['settle'].values)
#print np.extract( weird,to_fit['open_interest'].values)


