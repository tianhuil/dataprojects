import numpy as np
import pylab as pl
import datetime 
import pandas as pd
import scipy.signal as signal
from sklearn import linear_model
import statsmodels.api as sm
import pickle

import sys
sys.path.append('../')
import settings

def load_stock(comm_choice, start_date, end_date):
    stock_data = pd.read_pickle('%s.pickle' %comm_choice)
    stock_data = stock_data[pd.datetime(start_date.year,start_date.month,start_date.day):pd.datetime(end_date.year,end_date.month,end_date.day)]
    return stock_data

def date_contract(contract_dates, stock):
    contract_ord = np.array([a.toordinal() for a in contract_dates], dtype=int)
    print stock['orddate']
    print contract_ord
    day_bins = np.digitize(stock['orddate'], contract_ord)
    print day_bins
    trange = np.array([(contract_ord[x]-y)/float(contract_ord[x]-contract_ord[x-1]) for x,y in zip(day_bins, stock['orddate'])])
    stock['time_remaining'] = trange
    return

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

    clf = sm.tsa.ARMA(stock_data['settle'], order=(0,5))#exog=stock_data['CPI'], freq='B'
    model = clf.fit()
    print model.params
    print model.aic, model.bic, model.hqic
    print model
#    sm.stats.normaltest(model.resid)
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
