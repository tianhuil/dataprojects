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

Conn = mysql.connect(host = settings.host,
                     user = settings.user,
                     db = settings.db)
Conn.autocommit(True)
cursor = Conn.cursor()

from stock_difference_functions import *

from sklearn.metrics import mean_squared_error
scorer = mean_squared_error

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
    stock_data = volume_predictors(stock_data)
    test_data = volume_predictors(test_data)
    
    fig = plt.figure(figsize=(12,8))
    plt.subplots_adjust(hspace=0.4)
    ax1 = fig.add_subplot(211)
    plt.title('Volume Autocorrelation')
    plt.xlabel('Lag (Business Days)')
    plt.ylabel('Correlation')
    sm.graphics.tsa.plot_acf(stock_data['volume'].values.squeeze(), lags=60, ax=ax1)
    ax2 = fig.add_subplot(212)
    plt.title('Volume PAcf')
    plt.xlabel('Lag (Business Days)')
    plt.ylabel('Correlation')
    sm.graphics.tsa.plot_pacf(stock_data['volume'], lags=60, ax=ax2)
    plt.figtext(0.5, 0.95,'Volume Correllations')
    plt.savefig('volume_corr.png')


    arma_mod11 = sm.tsa.ARMA(stock_data['volume'], (1,1)).fit()
    print arma_mod11.summary()
    stock_data['ARMAPredictVolume'] = arma_mod11.predict()
    stock_data['ARMAResid'] = arma_mod11.resid
    stock_data['ARMANormResids'] =arma_mod11.resid/stock_data['volume'].shift(1)
    stock_data['ARMANormResids']= stock_data['ARMANormResids'].fillna(0)


    arma_test11 = sm.tsa.ARMA(test_data['volume'], (1,1)).fit()
    print arma_test11.summary()
    test_data['ARMAPredictVolume'] = arma_test11.predict()
    test_data['ARMAResid'] = arma_test11.resid
    test_data['ARMANormResids'] =arma_test11.resid/test_data['volume'].shift(1)
    test_data['ARMANormResids']= test_data['ARMANormResids'].fillna(0)
    

    fig = plt.figure(figsize=(12,8))
    plt.subplots_adjust(hspace=0.4)
    ax1 = fig.add_subplot(211)
    plt.xlabel('Lag (Business Days)')
    plt.ylabel('Correlation')
    plt.title('Residual Volume Autocorrelation')
    sm.graphics.tsa.plot_acf(stock_data['ARMAResid'].values.squeeze(), lags=60, ax=ax1)
    ax2 = fig.add_subplot(212)
    plt.title('Residual Volume  Pacf')
    plt.xlabel('Lag (Business Days)')
    plt.ylabel('Correlation')
    sm.graphics.tsa.plot_pacf(stock_data['ARMAResid'], lags=60, ax=ax2)
    plt.savefig('volume_ARMAresidcorr.png')
    
    fig = plt.figure(figsize=(12,8))
    plt.title('qq plot of the ARMA Volume Residual')
    qqplot(stock_data['ARMAResid'], line='q', ax=plt.gca(), fit=True)
    plt.savefig('volARMAresid_qq.png')

    error_figure(stock_data, 'ARMAResid', 'ARMAPredictVolume', 
                 'ARMANormResids','ARMA Only')
    plt.savefig('ARMA_stock_residual_panel.png')

    error_figure(test_data, 'ARMAResid', 'ARMAPredictVolume', 
                 'ARMANormResids','ARMA Only')
    plt.savefig('ARMA_test_residual_panel.png')
    plt.close('all')
    
    train_arr = get_pred_arr(stock_data)
    test_arr =get_pred_arr(test_data)     

    scaler = preprocessing.StandardScaler().fit(train_arr)
    sctrain_arr = scaler.transform(train_arr) 
    sctest_arr = scaler.transform(test_arr) 

    #there is some remaining autocorrelation at ~20 days. This is due to the monthly roll-off, so lets fit a decision tree to the folded data.
    print "Decision Tree"
    from sklearn import tree
    clf = tree.DecisionTreeRegressor()
    stock_data['rolloff'] = clf.fit(np.array(stock_data['time_remaining'])[:,np.newaxis],stock_data['ARMAResid']/stock_data['ARMAPredictVolume']).predict(np.array(stock_data['time_remaining'])[:,np.newaxis])*stock_data['ARMAPredictVolume']
    test_data['rolloff'] = clf.predict(np.array(test_data['time_remaining'])[:,np.newaxis])*test_data['ARMAPredictVolume']
    
    def rolloff(df):
        df['timePredictVolume'] = (df['ARMAPredictVolume']+df['rolloff']).fillna(-999).fillna(method='ffill')
        df['timeResid'] = (df['volume'].values-df['timePredictVolume']).fillna(-999).fillna(-999)
        df['timeNormResids'] =df['timeResid']/df['volume'].shift(1)
        df['timeNormResids']= df['timeNormResids'].fillna(-999).fillna(-999)
        return df

    stock_data = rolloff(stock_data)
    test_data = rolloff(test_data)

    error_figure(test_data, 'timeResid', 'timePredictVolume', 
                 'timeNormResids','roll-off plus ARMA')
    plt.savefig('time_test_residual_panel.png')


    plot_vol_error(test_data['volume'].values,test_data['timePredictVolume'], 'decision tree regression test set', scorer)
    plt.xlabel('volume')
    plot_vol_error(test_data['volume'].values,test_data['ARMAPredictVolume'], 'test set ARMA only', scorer)
    plot_vol_error(test_data['volume'].values,test_data['timePredictVolume'], 'test set time resid corrected', scorer)
    plt.xlabel('volume')
    plt.savefig('test_rolloff_residual_panel.png')

    from sklearn.cross_validation import train_test_split
    volume_train, volume_cv, true_train, true_cv = train_test_split(sctrain_arr, stock_data['log_vol'].fillna(method='backfill').values, test_size=0.33, random_state=42)

    from sklearn import dummy
    dumreg = dummy.DummyRegressor()
    dumreg.fit(volume_train, true_train)
    dumguess = dumreg.predict(sctest_arr)
    plot_error(test_data['log_vol'].values, dumguess, 'Dumb regression test set', scorer)
    plt.savefig('volcorr_Dummy.png')
    
    clf = sklearn.linear_model.LinearRegression()
    clf.fit(volume_train, true_train)
    stock_data['predictchange']=clf.predict(sctrain_arr)
    plot_error(test_data['log_vol'].values, clf.predict(sctest_arr), 'linear regression test set', scorer)
    plt.savefig('volcorr_linear.png')

    print "Decision Tree"
    from sklearn import tree
    clf = tree.DecisionTreeRegressor()
    clf = clf.fit(volume_train, true_train).predict(sctest_arr)
    plot_error(test_data['log_vol'].values,clf, 'decision tree regression test set', scorer)
    plt.savefig('volcorr_DecTree.png')

    param_grid=[ {'n_estimators':range(5,56,10), 
                  'min_samples_split':range(5,36,10),
                  'min_samples_leaf':range(10,51,10)},]

    print "Random Forest"
    from sklearn.ensemble import RandomForestClassifier
    clf = RandomForestClassifier(n_estimators=10)
    clf = sklearn.grid_search.GridSearchCV(clf, param_grid, scoring='mean_squared_error', verbose = 10)
    clf.fit(volume_train, true_train)
    clf = clf.predict(sctest_arr)
    plot_error(test_data['log_vol'].values,clf, 'random forest regression test set', scorer)
    plt.savefig('volcorr_RandFor.png')

    print "SVM"
    from sklearn import svm
    param_grid = [
        {'C': [0.001,0.01,0.1, 1.0], 'kernel': ['linear']},
        {'C': [0.001,0.01,0.1,1.0], 'gamma': [0.01, 0.001], 
         'kernel': ['rbf']},
        ]
    clf = svm.SVR()
    clf = sklearn.grid_search.GridSearchCV(clf, param_grid, scoring='mean_squared_error', verbose = 10)
    clf.fit(volume_train, true_train)
    plot_error(test_data['log_vol'].values,clf.predict(sctest_arr), 'SVM regression test set', scorer)
    print clf.get_params()
    plt.savefig('volcorr_SVM.png')






