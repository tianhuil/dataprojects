import numpy as np
import pylab as pl
import datetime 
import pandas as pd
import scipy.signal as signal
from sklearn import linear_model

import sys
sys.path.append('../')
import settings

def load_stock(comm_choice, start_date, end_date):
    stock_data = pd.read_pickle('%s.pickle' %comm_choice)
    print stock_data

    ok_dates = np.logical_and(start_date<=stock_data.index,end_date>=stock_data.index)
    stock_data = stock_data[ok_dates]
    return stock_data

def date_contract(contract_dates, stock):
    days = np.array(stock.index).astype(float)
    day_bins = np.digitize(days, contract_dates)
    trange = np.array([(contract_dates[x]-y)/(contract_dates[x]-contract_dates[x-1]) for x,y in zip(day_bins, days)])
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
    start_date = [ int(a) for a in settings.start_date.split('-')]
    end_date = [ int(a) for a in settings.end_date.split('-')]

    contract_dates = [[a,b,15] for a in range(start_date[0]-2,end_date[0]+2) for b in settings.end_months[comm_choice] ] 

    contract_dates = np.array([datetime.date(*a).toordinal() for a in contract_dates])
    start_date = datetime.date(*start_date).toordinal()
    end_date = datetime.date(*end_date).toordinal()

    data_path = '/home/ameert/git_projects/dataprojects/alan/data/st_louis_fed/'

    stock_data = load_stock(comm_choice, start_date, end_date)
    #get the time to maturity in fraction of overall time
    date_contract(contract_dates, stock_data)
    momentum(stock_data)
    momentum(stock_data, key='CPI')

    pred_list = settings.pred_list
    stock_data, pred_list=update_avgs(stock_data, pred_list, maxdays)

    clf = linear_model.LinearRegression()
    clf.fit(stock_data[pred_list],stock_data['settle'])
    print clf.coef_
    clf.predict(stock_data[pred_list])

    model = clf.predict(stock_data[pred_list])

    np.savez('modeltmp.npz', coef=clf.coef_, intercept=clf.intercept_, predict_names = pred_list)

    pl.subplot(2,2,1)
    pl.plot(stock_data.index, stock_data['settle'], c='k')
    pl.plot(stock_data.index[maxdays:], model[maxdays:], c='r')
    pl.subplot(2,2,2)
    pl.plot(stock_data.index[maxdays:], stock_data['settle'][maxdays:]-model[maxdays:], c='r')
    pl.subplot(2,2,3)
    pl.plot(stock_data.index[maxdays:], (stock_data['settle'][maxdays:]-model[maxdays:])**2, c='r')
    pl.subplot(2,2,4)
    print model.size
    print model.size/2, model.size/2

    autocor = signal.correlate(stock_data['settle'], model, mode='same')
    offset = np.arange(-model.size/2, model.size/2)
    max_autocorr = np.extract(autocor >= np.max(autocor)-0.000001, offset)[0]
    pl.plot(offset,autocor)
    pl.text(0.1, 0.1, r'max\_autocorr$=$%0.1f'%max_autocorr, transform=pl.gca().transAxes)
    #pl.plot(stock_data.index, stock_data['open_interest'], c='r')
    #for a in contract_dates:
    #    pl.plot([a,a],pl.ylim(), 'k')
    pl.show()


    #for ind_file in ['CPI.txt', 'GDP.txt', 'Population.txt', 'rec_prob.txt',
    #                 'stress_ind.txt',  'um_sent.txt']:
    #    new_pandas = load_fred(data_path+ind_file)
