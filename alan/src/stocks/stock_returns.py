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

def date_contract(contract_dates, stock):
    contract_ord = np.array([ a.date().toordinal() for a in contract_dates])
    day_bins = np.digitize(stock['orddate'], contract_ord, right=True)
    stock['day_bins'] = day_bins
    trange = np.array([(contract_ord[x]-y)/float(contract_ord[x]-contract_ord[x-1]) for x,y in zip(day_bins, stock['orddate'])])
    stock['time_remaining'] = trange
    return

def load_stock(comm_choice, start_date, end_date):
    stock_data = pd.read_pickle('%s.pickle' %comm_choice)
    stock_data = stock_data[pd.datetime(start_date.year,start_date.month,start_date.day):pd.datetime(end_date.year,end_date.month,end_date.day)]
    return stock_data

def moving_average(days, stock, key):
    good_days = np.concatenate([np.zeros(days+1),np.ones(days)])/float(days)
    moving_average = signal.convolve(stock[key], good_days, mode='same')
    return moving_average

def momentum(stock, key='settle'):
    momentum = np.zeros_like(stock['settle'])
    days = np.array(stock.index)
    settle = np.array(stock[key])

    for pos, index in enumerate(days):
        try:
            momentum[pos] = (settle[pos-1]-settle[pos-2])/(days[pos-1]-days[pos-2])
        except IndexError, KeyError:
            momentum[pos] = np.nan
    
    stock[key+'momentum'] = momentum
    return 

def model_func(price_days, price_factor, momentum_days, momentum_factor, 
          maturity_factor):
    model = price_factor*moving_average(price_days, stock_data, 'settle') +\
        momentum_factor*moving_average(momentum_days, stock_data, 'momentum') +\
        maturity_factor*stock_data['time_remaining']
    return model

def update_avgs(stock_data, pred_list, maxdays):
        for day_c in range(1, maxdays):
            stock_data['mom_avg_%d' %day_c] = moving_average(day_c, stock_data, 'settlemomentum')
            pred_list.append('mom_avg_%d' %day_c)
            stock_data['p_avg_%d' %day_c] = moving_average(day_c, stock_data, 'settle')
            pred_list.append('p_avg_%d' %day_c)
        
            stock_data['CPI_mom_%d' %day_c] = moving_average(day_c, stock_data, 'CPI')
            pred_list.append('CPI_mom_%d' %day_c)
        print stock_data.columns
        return stock_data, pred_list



if __name__ == "__main__":
    comm_choice = settings.comm_choice
    maxdays=settings.maxdays
    start_date = datetime.date(*[ int(a) for a in settings.start_date.split('-')])
    end_date = datetime.date(*[ int(a) for a in settings.end_date.split('-')])

    contract_dates = [[a,b,15] for a in range(start_date.year-2,end_date.year+2) for b in settings.end_months[comm_choice] ] 

    contract_dates = np.array([datetime.date(*a) for a in contract_dates])

    data_path = '/home/ameert/git_projects/dataprojects/alan/data/st_louis_fed/'

    stock_data = load_stock(comm_choice, start_date, end_date)

    #get the time to maturity in fraction of overall time
    date_contract(contract_dates, stock_data)

    stock_data['log_ret'] = np.log(stock_data['settle']/stock_data['settle'].shift(-1))
    stock_data['log_ret'] = stock_data['log_ret'].fillna(value=0)
    
    events = psql.frame_query('select SQLDATE, avg(GoldsteinScale) as GoldsteinScale from ev0405 group by SQLDATE;',  con=Conn)
    events['orddate'] = SQLdate_to_ord(events['SQLDATE'])

    to_fit = pd.merge(events,stock_data,how='inner', on='SQLDATE')
    
    data =np.array(to_fit['GoldsteinScale'][:,np.newaxis]) 
    yval =np.array(to_fit['log_ret'])

    print data
    print yval
    print data.shape, yval.shape
    from sklearn import linear_model
    clf = linear_model.LinearRegression()

    clf.fit(data, yval)

    x_vals = np.arange(-10.0, 10.0, 0.01)

    pl.scatter(to_fit['GoldsteinScale'],to_fit['log_ret'])
    pl.plot(x_vals, clf.predict(x_vals[:,np.newaxis]))
    pl.show()

    pl.subplot(3,3,1)
    stock_data['settle'].plot(c='k')
    pd.stats.moments.ewma(stock_data['settle'], span=30).plot()
    pl.title("price with ewma")
    pl.ylabel("dollars")

    pl.subplot(3,3,2)
    pl.hist(stock_data['log_ret'], range=(-0.1,0.1),bins=100)
    pl.title("Daily Change")
    pl.ylabel("daily change")

    pl.subplot(3,3,3)
    stock_data['log_ret'].plot()
    pl.title("Daily Change")
    pl.ylabel("daily change")

    pl.subplot(3,3,4)
    stock_data['time_remaining'].plot()
    pl.title("time in contract")
    pl.ylabel("time")
    pl.xlabel("days")

    pl.subplot(3,3,5)
    stock_data['volume'].plot()
    pl.title("Volume")
    pl.ylabel("Volume")

    pl.subplot(3,3,6)
    stock_data['open_interest'].plot()
    pl.title("Interest")
    pl.ylabel("Interest")

    pl.subplot(3,3,7)
    pl.plot(np.array([stock_data['log_ret'].corr(stock_data['time_remaining'].shift(i) ) for i in range(1,200) ] ) )
    pl.title("Lagged cross-correlation (return and time remaining)")
    pl.ylabel("Correlation")
    pl.xlabel("Lag (business days)")

    pl.subplot(3,3,8)
    pl.plot(np.array([stock_data['log_ret'].corr(stock_data['volume'].shift(i) ) for i in range(1,200) ] ) )
    pl.title("Lagged cross-correlation (return and volume)")
    pl.ylabel("Correlation")
    pl.xlabel("Lag (business days)")

    pl.subplot(3,3,9)
    pl.scatter(stock_data['time_remaining'],stock_data['log_ret'], s=2 )
    pl.title(" folded return")
    pl.ylabel("return")
    pl.xlabel("contract cycle")

    pl.subplots_adjust(hspace=0.5, wspace=0.5)
    pl.figtext(0.5, 0.95, comm_choice)
    pl.show()

