import numpy as np
import pandas as pd
from scipy import stats
from sklearn import linear_model
from sklearn import svm
from sklearn import ensemble
from sklearn import metrics
from sklearn import grid_search
from sklearn import preprocessing
from sklearn import utils
import multiprocessing

def grid_search_then_eval(train_data, train_label, test_data, test_label, clf, parameters, score_criteria, num_cv):
    models = grid_search.GridSearchCV(clf, parameters, scoring=score_criteria, cv=num_cv)
    models.fit(train_data, train_label)
    opt_model = models.best_estimator_
    if score_criteria == 'accuracy':
        opt_model_accu = metrics.accuracy_score(test_label, opt_model.predict(test_data))
    elif score_criteria == 'roc_auc':
        opt_model_accu = metrics.roc_auc_score(test_label, opt_model.predict(test_data))
    return opt_model_accu, opt_model

def classifiers_train_and_eval((train_data, train_label, test_data, test_label)):
    # A bundle for training multiple classifiers and then evaluate them
    
    score_criteria = 'accuracy'
    num_cv = 5
    # shuffle the training data in case cv is not shuffling at all
    train_data, train_label = utils.shuffle(train_data, train_label, random_state=42)

    # normalized the data as a standard procedure
    scaler = preprocessing.StandardScaler().fit(train_data)  # fit does nothing
    scaled_train_data = scaler.transform(train_data)
    scaled_test_data = scaler.transform(test_data)
    
    # baseline: predict the major class of training samples to all test samples 
    mode_label = stats.mode(train_label.astype(float))[0][0] # the majority label of the training samples
    if score_criteria == 'accuracy':
        baseline_accu = metrics.accuracy_score(test_label, np.ones(len(test_label))*mode_label)
    elif score_criteria == 'roc_auc':
        baseline_accu = metrics.roc_auc_score(test_label, np.ones(len(test_label))*mode_label)

    # linear models
    # logistic regression
    Cs = np.logspace(-3., 3., num=10)
    LR_clf = linear_model.LogisticRegression()
    parameters = {'C':Cs}
    opt_LR_accu, opt_LR = grid_search_then_eval(train_data, train_label, test_data, test_label, LR_clf, parameters, score_criteria, num_cv)
    
    # linear SVM
    LinSVM_clf = svm.LinearSVC(loss='l1')
    parameters = {'C':Cs}
    opt_LinSVM_accu, opt_LinSVM = grid_search_then_eval(train_data, train_label, test_data, test_label, LinSVM_clf, parameters, score_criteria, num_cv)
    
    # non-linear models
    # RBF SVM
    gammas = np.logspace(-3., 3., num=10)
    RBFSVM_clf = svm.SVC(kernel='rbf')
    parameters = {'C':Cs, 'gamma':gammas}
    opt_RBFSVM_accu, opt_RBFSVM = grid_search_then_eval(train_data, train_label, test_data, test_label, RBFSVM_clf, parameters, score_criteria, num_cv)
    
    # Random Forest
    max_depths= range(2, 10, 2) 
    min_samples_splits= [10, 20, 40, 80, 120]
    RF_clf = ensemble.RandomForestClassifier()
    parameters = {'max_depth': max_depths, 'min_samples_split':min_samples_splits}
    opt_RF_accu, opt_RF = grid_search_then_eval(train_data, train_label, test_data, test_label, RF_clf, parameters, score_criteria, num_cv)
    
    # Adaboost Trees
    n_estimators = [100, 300, 1000]
    AdaTree_clf = ensemble.AdaBoostClassifier()
    parameters = {'n_estimators': n_estimators}
    opt_AdaTree_accu, opt_AdaTree = grid_search_then_eval(train_data, train_label, test_data, test_label, AdaTree_clf, parameters, score_criteria, num_cv)
    
    return [baseline_accu, opt_LR_accu, opt_LinSVM_accu, opt_RBFSVM_accu, opt_RF_accu, opt_AdaTree_accu], [opt_LR, opt_LinSVM, opt_RBFSVM, opt_RF, opt_AdaTree]

def multiTimeSplit_classifier_eval(features, labels, future_days, history_days, n_split=100):

    num_of_workers = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(num_of_workers)
    classifiers_output = pool.map(classifiers_train_and_eval, [(features[-history_days-i_split*future_days-1:-i_split*future_days-1],
                                                    labels[-history_days-i_split*future_days-1:-i_split*future_days-1],
                                                    features[-i_split*future_days-1:-(i_split-1)*future_days-1],
                                                    labels[-i_split*future_days-1:-(i_split-1)*future_days-1]) 
                                                   for i_split in range(1, n_split+1)])
    pool.terminate()
    pool.join()

    classification_accus_and_models = pd.DataFrame(classifiers_output, columns=['accus', 'models'])
    classification_accus = []
    for i in range(len(classification_accus_and_models)):
        classification_accus.append(classification_accus_and_models['accus'][i])
    classification_accus = pd.DataFrame(classification_accus, columns=['baseline', 'logistic_regression','linear_svm', 'rbf_svm', 'random_forrest', 'adaboost_trees'])
    classification_models = classification_accus_and_models['models'] 
    
    return classification_accus, classification_models