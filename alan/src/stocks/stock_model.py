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

from stock_returns import load_stock, date_contract

Conn = mysql.connect(host = settings.host,
                     user = settings.user,
                     db = settings.db)
Conn.autocommit(True)
cursor = Conn.cursor()

if __name__ == "__main__":
    comm_choice = settings.comm_choice
    maxdays=settings.maxdays
    start_date = do_date(settings.start_date)
    end_date = do_date(settings.end_date)

    data_path = '/home/ameert/git_projects/dataprojects/alan/data/st_louis_fed/'
    stock_data = load_stock(comm_choice, start_date, end_date)

    # calculate the log return, which is simpler to model
    stock_data['log_ret'] = np.log(stock_data['settle']/stock_data['settle'].shift(-1))
    stock_data['log_ret'] = stock_data['log_ret'].fillna(value=0)

    # build a simple model for the stock price based on the CPI 
    
    #select and model the CPI
    cmd = 'select SQLDATE, value as CPI from CPI where SQLDATE between 19700000 and 20000000 order by SQLDATE;'
    metric_df = psql.frame_query(cmd, con=Conn)
    metric_df.index = SQLdate_to_date(metric_df['SQLDATE'])
    metric_df.index = pd.to_datetime(metric_df.index)
    metric_df['orddate'] = SQLdate_to_ord(metric_df['SQLDATE'])

    clf = linear_model.LinearRegression()
    clf.fit(metric_df['orddate'].values[:,np.newaxis], metric_df['CPI'])
    metric_df['predict']=clf.predict(metric_df['orddate'].values[:,np.newaxis])
    
    stock_data['CPIpredict']=clf.predict(stock_data['orddate'].values[:,np.newaxis])
    stock_data['normPrice'] = stock_data['settle']/stock_data['CPIpredict']*clf.predict(np.array([datetime.date(2000,1,1).toordinal()])[:,np.newaxis])
    
    metric_df[['CPI', 'predict']].plot()
    
    stock_data[['normPrice']].plot()
    stock_data[['settle']].plot()
    stock_data[['CPI', 'CPIpredict']].plot()
    
    #pl.show()
    #first, lets look at the volume correlated with the price
    fig = pl.figure()
    pl.plot( np.array( [ stock_data['normPrice'].corr( stock_data['volume'].shift(i) ) for i in range(1,200) ] ) )
    pl.title("Lagged price-volume correlation")
    pl.ylabel("Correlation")
    pl.xlabel("Lag (business days)")

    #pl.show()

    # since volume is correllated with price up to a lag of 30 days,
    # lets predict volume based on the average price over the last 30 days
    stock_data['priceMean30']=pd.rolling_mean(stock_data['normPrice'], 30,min_periods=1)
    stock_data['priceVar30']=pd.rolling_var(stock_data['normPrice'], 30,min_periods=1)
    stock_data['VolMean30']=pd.rolling_mean(stock_data['volume'], 30,min_periods=1)
    stock_data['VolVar30']=pd.rolling_var(stock_data['volume'].apply(np.log10), 30,min_periods=1)
    stock_data.fillna(value = 0, inplace=True)
    vol_pred = linear_model.LinearRegression()
    log_vol = np.log10(stock_data['volume'].values)
    log_vol = np.where(np.logical_or(np.isinf(log_vol), np.isnan(log_vol)),0,log_vol)
    log_vol = np.where(log_vol<0, 0,log_vol)
    #vol_pred.fit(stock_data['priceMean30'].values[:,np.newaxis], stock_data['volume'].values)
    print np.array([stock_data['priceMean30'],stock_data['priceVar30'],stock_data['stress_ind']]).T.shape
    print log_vol.shape

    #vol_pred.fit(stock_data['stress_ind'].values[:,np.newaxis], log_vol)
    #stock_data['predictVolume']=10**(vol_pred.predict(stock_data['stress_ind'].values[:,np.newaxis]))

    
    vol_pred.fit(np.array([stock_data['VolVar30'],stock_data['stress_ind']]).T, log_vol)
    stock_data['predictVolume']=10**(vol_pred.predict(np.array([stock_data['VolVar30'],stock_data['stress_ind']]).T ))
    
    stock_data[['volume','predictVolume', 'VolMean30']].plot()
    stock_data[['normPrice', 'priceMean30']].plot()
    print stock_data.columns
    print vol_pred.intercept_
    print vol_pred.coef_

    stock_data[['countUS','countIR', 'countIZ']].plot()
    fig = pl.figure()

    stock_data['volResid'] = stock_data['volume']-stock_data['predictVolume']
    stock_data['volResid'].plot()
    

    fig = pl.figure()
    pl.plot( np.array( [ stock_data['countUS'].corr( stock_data['volResid'].shift(i) ) for i in range(1,200) ] ) )
    pl.title("Lagged event-volume residual correlation")
    pl.ylabel("Correlation")
    pl.xlabel("Lag (business days)")

    

    pl.show()
    sys.exit()
    
    # for volume, lets look at the folded volume 
    groups = to_fit.groupby('day_bins')
    
    
    means= groups.mean()
    period_mean =means['volume']
    interest_mean =means['open_interest']



    sys.exit()



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



if 0:
        clf = sm.tsa.ARMA(stock_data['settle'], order=(1,1),exog=stock_data['CPI'])
        model = clf.fit()
        print model.params
        print model.aic, model.bic, model.hqic
        print model
        sm.stats.normaltest(model.resid)
        r,q,p = sm.tsa.acf(model.resid.values.squeeze(), qstat=True)
        data = np.c_[range(1,41), r[1:], q, p]
        table = pd.DataFrame(data, columns=['lag', "AC", "Q", "Prob(>Q)"])
        print table.set_index('lag')



        pl.subplot(2,2,1)
        stock_data['settle'].plot(c='k')
        pd.stats.moments.ewma(stock_data['settle'], span=30).plot()
        pl.title("price with ewma")
        pl.ylabel("dollars")
        predict = model.predict('2004-01-12', '2005-02-01', dynamic=True)
        print predict
        predict.plot()

        pl.subplot(2,2,2)
        pl.plot(np.array([stock_data['settle'].corr(stock_data['settle'].shift(i) ) for i in range(1,200) ] ) )
        pl.title("Lagged autocorrelation")
        pl.ylabel("Correlation")
        pl.xlabel("Lag (business days)")

        pl.subplot(2,2,3)
        pl.plot(sm.tsa.stattools.pacf(stock_data['settle'], nlags=40))
        pl.title("partial autocorrelation")
        pl.ylabel("Correlation")
        pl.xlabel("Lag (business days)")

        pl.subplot(2,2,4)
        model.resid.plot()
        pl.title("Residuals")
        pl.ylabel("Residual")

        pl.subplots_adjust(hspace=0.5, wspace=0.5)
        pl.figtext(0.5, 0.95, comm_choice)
        pl.show()

        sm.iolib.smpickle.save_pickle(model, 'modeltmp.pickle')
