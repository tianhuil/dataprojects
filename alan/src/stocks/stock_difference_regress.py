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
from sklearn import preprocessing


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

from stock_difference_functions import *


if __name__ == "__main__":
    comm_choice = settings.comm_choice
    maxdays=settings.maxdays
    train_start_date = do_date(settings.train_start_date)
    train_end_date = do_date(settings.train_end_date)

    test_start_date = do_date(settings.test_start_date)
    test_end_date = do_date(settings.test_end_date)

    
    #load the data 
    stock_data = load_stock(comm_choice, train_start_date, train_end_date)
    test_data = load_stock(comm_choice, test_start_date, test_end_date)

    # calculate the log return, which is simpler to model
    stock_data = price_predictors(stock_data)
    test_data = price_predictors(test_data)
    print test_data

    print stock_data.columns
    stock_data['log_ret'].hist(range=(-0.5, 0.5),bins=100, normed=True)
    x = np.arange(-0.5, 0.5, 0.001)
    plt.plot(x, sp.stats.norm(loc=stock_data['log_ret'].mean(), scale=stock_data['log_ret'].std()).pdf(x), linewidth=3, color='red')
    plt.xlim(-0.5,0.5)
    plt.title('log return distribution')
    print stock_data['log_ret'].describe()


    fig = plt.figure(figsize=(12,8))
    plt.subplots_adjust(hspace=0.4)
    ax1 = fig.add_subplot(211)
    plt.title('Price Autocorrelation')
    plt.xlabel('Lag (Business Days)')
    plt.ylabel('Correlation')
    sm.graphics.tsa.plot_acf(stock_data['settle'].values.squeeze(), lags=60, ax=ax1)
    ax2 = fig.add_subplot(212)
    plt.title('Price PAcf')
    plt.xlabel('Lag (Business Days)')
    plt.ylabel('Correlation')
    sm.graphics.tsa.plot_pacf(stock_data['settle'], lags=60, ax=ax2)
    plt.figtext(0.5, 0.95,'Stock Price Correllations')
    plt.savefig('stock_corr.png')

    fig = plt.figure(figsize=(12,8))
    plt.subplots_adjust(hspace=0.4)
    ax1 = fig.add_subplot(211)
    plt.xlabel('Lag (Business Days)')
    plt.ylabel('Correlation')
    plt.title('Log(Return) Autocorrelation')
    sm.graphics.tsa.plot_acf(stock_data['log_ret'].values.squeeze(), lags=60, ax=ax1)
    ax2 = fig.add_subplot(212)
    plt.title('Log(Return) Pacf')
    plt.xlabel('Lag (Business Days)')
    plt.ylabel('Correlation')
    sm.graphics.tsa.plot_pacf(stock_data['log_ret'], lags=60, ax=ax2)
    plt.figtext(0.5, 0.95,'Daily Return Correllations by Date')
    plt.savefig('stock_logregcorr.png')
    
    sys.exit()
    
    fig = plt.figure(figsize=(12,8))
    plt.title('qq plot of the log(return)')
    qqplot(stock_data['log_ret'], line='q', ax=plt.gca(), fit=True)
    plt.savefig('logrec_qq.png')
    
    train_arr = get_pred_arr(stock_data)
    test_arr =get_pred_arr(test_data)     

    scaler = preprocessing.StandardScaler().fit(train_arr)
    sctrain_arr = scaler.transform(train_arr) 
    sctest_arr = scaler.transform(test_arr) 

    from sklearn.cross_validation import train_test_split
    stock_train, stock_cv, true_train, true_cv = train_test_split(sctrain_arr, stock_data['log_ret'].fillna(method='backfill').values, test_size=0.33, random_state=42)

    # reweight outliers
    weighter_scale =  preprocessing.StandardScaler().fit(true_train)
    train_weight_outliers = 5.0*np.abs(weighter_scale.transform(true_train))+1
    cv_weight_outliers = 5.0*np.abs(weighter_scale.transform(true_cv))+1
    test_weight_outliers = 5.0*np.abs(weighter_scale.transform(test_data['log_ret'].values))+1

    from sklearn.metrics import mean_squared_error
    scorer = mean_squared_error

    from sklearn import dummy
    dumreg = dummy.DummyRegressor()
    dumreg.fit(stock_train, true_train)
    dumguess = dumreg.predict(sctest_arr)
    plot_error(test_data['log_ret'].values, dumguess, 'Dumb regression test set', scorer)
    plt.savefig('logregcorr_Dummy.png')
    
    clf = sklearn.linear_model.LinearRegression()
    clf.fit(stock_train, true_train)
    stock_data['predictchange']=clf.predict(sctrain_arr)
    plot_error(test_data['log_ret'].values, clf.predict(sctest_arr), 'linear regression test set', scorer)
    plt.savefig('logregcorr_linear.png')

    print "Decision Tree"
    from sklearn import tree
    clf = tree.DecisionTreeRegressor()
    clf = clf.fit(stock_train, true_train,sample_weight=train_weight_outliers).predict(sctest_arr)
    plot_error(test_data['log_ret'].values,clf, 'decision tree regression test set', scorer)
    plt.savefig('logregcorr_DecTree.png')

    param_grid=[ {'n_estimators':range(5,56,10), 
                  'min_samples_split':range(5,36,10),
                  'min_samples_leaf':range(10,51,10)},]

    print "Random Forest"
    from sklearn.ensemble import RandomForestClassifier
    clf = RandomForestClassifier(n_estimators=10)
    clf = sklearn.grid_search.GridSearchCV(clf, param_grid, scoring='mean_squared_error', verbose = 10)
    clf.fit(stock_train, true_train,sample_weight=train_weight_outliers)
    clf = clf.predict(sctest_arr)
    plot_error(test_data['log_ret'].values,clf, 'random forest regression test set', scorer)
    plt.savefig('logregcorr_RandFor.png')

    print "SVM"
    from sklearn import svm
    param_grid = [
        {'C': [0.01,0.1, 1.0, 10.0, 100.0, 1000.0], 'kernel': ['linear']},
        {'C': [0.01,0.1,1.0, 10.0, 100.0, 1000.0], 'gamma': [0.01, 0.001], 
         'kernel': ['rbf']},
        ]
    clf = svm.SVR()
    clf = sklearn.grid_search.GridSearchCV(clf, param_grid, scoring='mean_squared_error', verbose = 10)
    clf.fit(stock_train, true_train,sample_weight=train_weight_outliers)
    plot_error(test_data['log_ret'].values,clf.predict(sctest_arr), 'SVM regression test set', scorer)
    print clf.get_params()
    plt.savefig('logregcorr_SVM.png')

