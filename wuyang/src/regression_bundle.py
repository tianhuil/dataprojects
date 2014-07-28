import pandas as pd
import numpy as np
import multiprocessing
from sklearn import linear_model
from sklearn import metrics
from sklearn import grid_search
from sklearn import preprocessing
from sklearn import utils

def regression_train_and_eval((train_X, train_y, test_X, test_y)):
    # A bundle for training multiple regression models and then evaluate them
    
    score_criteria = 'mean_square_error'
    num_cv = 5
    # shuffle the training data in case cv is not shuffling at all
    train_X, train_y = utils.shuffle(train_X, train_y, random_state=42)

    # normalized the data as a standard procedure
    scaler = preprocessing.StandardScaler().fit(train_X)  # fit does nothing
    scaled_train_X = scaler.transform(train_X)
    scaled_test_X = scaler.transform(test_X)
    
    # baseline as always predict 0
    baseline_mse = metrics.mean_squared_error(test_y, np.ones(len(test_y))*train_y.mean())
    
    # linear regression
    linRegress = linear_model.LinearRegression()
    linRegress.fit(scaled_train_X, train_y)
    linRegress_mse = metrics.mean_squared_error(test_y, linRegress.predict(scaled_test_X))
    
    # ridge regression
    alphas = np.logspace(-2.0, 3.0, num=10)
    ridge_clf = linear_model.Ridge()
    parameters = {'alpha':alphas}
    ridge_models = grid_search.GridSearchCV(ridge_clf, parameters, scoring='mean_squared_error', cv=num_cv)
    ridge_models.fit(scaled_train_X, train_y)
    ridge_mse = metrics.mean_squared_error(test_y, ridge_models.predict(scaled_test_X))
    
    # lasso regression
    lasso_clf = linear_model.LassoLars()
    lasso_models = grid_search.GridSearchCV(lasso_clf, parameters, scoring='mean_squared_error', cv=num_cv)
    lasso_models.fit(scaled_train_X, train_y)
    lasso_mse = metrics.mean_squared_error(test_y, lasso_models.predict(scaled_test_X))
    
    return [baseline_mse, linRegress_mse, ridge_mse, lasso_mse], [linRegress, ridge_models.best_estimator_, lasso_models.best_estimator_]

def multiTimeSplit_models_train_and_eval(features, target, future_days, history_days, n_split=100):

    regress_accus = []
    regress_baseline = []
    
    num_of_workers = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(num_of_workers)
    regress_outputs = pool.map(regression_train_and_eval, [(features[-history_days-i_split*future_days-1:-i_split*future_days-1],
                                                    target[-history_days-i_split*future_days-1:-i_split*future_days-1],
                                                    features[-i_split*future_days-1:-(i_split-1)*future_days-1],
                                                    target[-i_split*future_days-1:-(i_split-1)*future_days-1]) 
                                                   for i_split in range(1, n_split+1)])
    pool.terminate()
    pool.join()
    
    regress_accus_and_models = pd.DataFrame(regress_outputs, columns=['accus', 'models'])
    regress_accus = []
    for i in range(len(regress_accus_and_models)):
        regress_accus.append(regress_accus_and_models['accus'][i])
    regress_accus = pd.DataFrame(regress_accus, columns=['baseline','linear_regression', 'ridge_regression', 'lasso_regression'])
    
    return regress_accus