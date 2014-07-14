import numpy as np
import matplotlib.pyplot as plt
import datetime 
import pandas as pd
import scipy.signal as signal
import statsmodels.api as sm
import pickle
import pandas.io.sql as psql
import MySQLdb as mysql
import scipy as sp
import sklearn.linear_model
import sklearn.tree
import sklearn.metrics
from statsmodels.graphics.api import qqplot

import sys
sys.path.append('../')
import settings
from utils import *

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


# Reporting function
def summarize_errors(test_me, real, model):
    error_pct = (test_me[real] -test_me[model])/test_me[real]

    print error_pct.describe()
    error_pct.plot()
    plt.ylim(-0.5, 0.5)
    plt.show()

    error_pct.hist(range= (-0.5, 0.5),bins=1000, normed=True)
#, weights = np.ones_like(error_pct)/error_pct.size)
    x = np.arange(-0.5, 0.5, 0.001)
    plt.plot(x, sp.stats.norm( loc=error_pct.median(), scale=(error_pct.quantile(0.84)-error_pct.quantile(0.16))/2.0 ).pdf(x), linewidth=3, color='red')
    plt.xlim(-0.5,0.5)
    plt.show()

    print "your model %.2e" %sklearn.metrics.mean_squared_error( test_me[real].fillna(0), test_me[model].fillna(0) )
    print "simple %.2e" %sklearn.metrics.mean_squared_error( test_me[real].fillna(0),test_me[real].shift(1).fillna(0))
    return

def error_figure(stock_data, resid_key, predict_key, norm_predict,figtitle):
    fig = plt.figure(figsize=(12,8))
    plt.subplots_adjust(hspace=0.6, bottom=0.1)
    plt.figtext(0.5, 0.97,figtitle)

    ax = fig.add_subplot(221)
    stock_data[resid_key].plot()
    plt.xlabel('Date')
    plt.ylabel('Absolute Residual Volume')
    plt.title('Absolute Residual Volume')

    ax = fig.add_subplot(222)
    stock_data['volume'].plot(label='volume')
    stock_data[predict_key].plot(label='predicted volume')
    plt.xlabel('Date')
    plt.ylabel('Volume')
    plt.title('Predicted and True Volume')
    plt.legend()

    ax = fig.add_subplot(223)
    stock_data[norm_predict].hist(range = (-0.75, 0.75), bins=100, 
                                  normed=True)
    x = np.arange(-0.75, 0.75, 0.001)
    #trim some crazy outliers
    trimmed_resid = np.extract(np.logical_and(stock_data[norm_predict]<1,
                                              stock_data[ norm_predict]>-1),
                               stock_data[norm_predict])  
    plt.plot(x, sp.stats.norm(loc=trimmed_resid.mean(), 
                              scale=trimmed_resid.std()).pdf(x), 
             linewidth=3, color='red')
    plt.xlim(-0.75,0.75)
    plt.title('normed residual distribution')
    plt.xlabel('Date')
    plt.ylabel('Volume')

    ax = fig.add_subplot(224)
    plt.title('folded residual')
    plt.scatter(stock_data['time_remaining'],
                stock_data[resid_key]/stock_data[predict_key], s=2)
    plt.subplots_adjust(hspace=0.4, wspace=0.4)
    plt.ylabel('residual relative to prediction')
    plt.xlabel('fraction remaining of contract')
    print stock_data[resid_key].describe()
    return

def normed_avg(df, key, span = 50, min_periods = 3):
    """takes the log of the value at lag 1 relative to the Exp. weighted MA"""
    value = np.log(df[key].shift(1)/pd.stats.moments.ewma(df[key].shift(1), span=span, min_periods=min_periods)).fillna(method='backfill').fillna(method='ffill')
    return value

def economic_predictors(df):
    """GDP, CPI, and other simple predictors"""
    df['percapGDP'] = df['GDP']/df['Population']
    df['normGDP'] =normed_avg(df, 'percapGDP')

    df['normFedFunds'] =normed_avg(df, 'FedFundsRate')
    return df

def gdelt_predictors(df):
    """event predictors. We normalize by the moving average to account for event count inflation"""
    for country in ['US', 'IR', 'RS', 'NO','KS','SA', 'NI','JA','GM','FR']:
        df['normcount%s' %country] = normed_avg(df, 'count%s' %country)
        for event in [18,19]:
            df['normcount%d%s' %(event,country)] = normed_avg(df,'count%d%s' %(event,country))
    return df


def price_predictors(df):
    df['log_ret'] = np.log(df['settle']/df['settle'].shift(1))
    df['log_ret_yesterday'] = df['log_ret'].shift(1).fillna(method='backfill')

    df['log_ret'] = df['log_ret'].fillna(value=0)

    df['ewma_ratio'] = normed_avg(df, 'settle', span = 5, min_periods = 3)
    df['ewma50_ratio']= normed_avg(df, 'settle', span = 50, min_periods = 3)

    df = economic_predictors(df)

    df = gdelt_predictors(df)
    
    df['const'] = np.ones_like(df['settle'].values)

    return df


def volume_predictors(df):
    df['log_vol'] = np.log(df['volume']/df['volume'].shift(1))
    df['log_yesterday'] = df['log_vol'].shift(1).fillna(method='backfill')

    df['log_vol'] = df['log_vol'].fillna(value=0)
    df['ewma_ratio'] = normed_avg(df, 'volume', span = 5, min_periods = 3)
    df['ewma50_ratio']= normed_avg(df, 'volume', span = 50, min_periods = 3)


    df = economic_predictors(df)
    df = gdelt_predictors(df)
    df['const'] = np.ones_like(np.array(df['settle'].values))
    return df


def get_pred_arr(df):
    cols_to_use = ['ewma50_ratio','ewma_ratio','log_yesterday',
                   'um_sent','time_remaining', 'normFedFunds',
                   'normGDP','stress_ind', 'normcountUS', 'normcountIR', 
                   'normcountRS', 'normcountNO','normcountKS',
                   'normcountSA', 'normcountNI',
                   'normcountJA','normcountGM','normcountFR',
                   'normcount19US', 'normcount19IR', 
                   'normcount19RS', 'normcount19NO','normcount19KS',
                   'normcount19SA', 'normcount19NI',
                   'normcount19JA','normcount19GM','normcount19FR',
                   'normcount18US', 'normcount18IR', 
                   'normcount18RS', 'normcount18NO','normcount18KS',
                   'normcount18SA', 'normcount18NI',
                   'normcount18JA','normcount18GM','normcount18FR', 'const']
    outarr = np.array([df[a] for a in cols_to_use]).T 
    return outarr

def plot_error(true, prediction, title, scorer):
    fig = plt.figure()
    plt.scatter(true, true-prediction, s=2)
    plt.title(title)
    plt.ylabel('error (true-predict)')
    plt.xlabel('true change')
    plt.text(.1,.1,'score:%.2e' %scorer(true,prediction), transform=plt.gca().transAxes)
    return

def plot_vol_error(true, prediction, title, scorer):
    fig = plt.figure()
    plt.scatter(true, (true-prediction)/true, s=2)
    plt.title(title)
    plt.ylabel('error (true-predict)/true')
    plt.xlabel('true volume')
    plt.xlim((20000.0,plt.xlim()[1]))
    plt.ylim((-1.5,1.5))
    plt.text(.1,.1,'score:%.2e' %scorer(true,prediction), transform=plt.gca().transAxes)
    return

def class_error(true, prediction, title, scorer):
    fig = plt.figure()
    imgplot = plt.imshow(sklearn.metrics.confusion_matrix(true, prediction)/float(true.size), origin='bottom')
    imgplot.set_interpolation('nearest')
    plt.colorbar()
    plt.title(title)
    plt.ylabel('actual class')
    plt.xlabel('predicted class')
    plt.text(-.1,-.1,'score:%.2e' %scorer(true,prediction), transform=plt.gca().transAxes)

    return
    
