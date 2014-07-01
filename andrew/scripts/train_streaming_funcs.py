import numpy as np
import pandas as pd
import cPickle as pickle
import MySQLdb as mdb

import sys

from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import SGDClassifier,LogisticRegression
from sklearn.utils.extmath import cartesian
from code_predictors import timecode,predictorcode

#Gets the min/max for a column in a database table. It's designed to get the primary key range which should be fast, but could work for any column:
def get_col_range(cur,table_name,col_name):
    cur.execute('SELECT MIN({0:s}),MAX({0:s}) FROM {1:s}'.format(col_name,table_name))
    data = cur.fetchall()[0]
    return data[0],data[1]#min,max

#Get all the unique entries in a table:
def get_distinct(cur,table_name,col_name):
    cur.execute('SELECT DISTINCT({0:s}) FROM {1:s}'.format(col_name,table_name))
    data = cur.fetchall()
    return np.array(data).reshape(-1)
                
    
def combine_args(**argarrs):#argarrs are [arg name]=[list of values]
    #Get all permutations of the arguments. Returns a pandas data frame with the argument names as the columns and the cartesian product of all their possible values.
    #Note that this can't handle None values (at least not yet)
    arg_keys = argarrs.keys()
    if len(arg_keys) == 0:
        raise ValueError("Must be at least one keyword argument (if you don't want to train multiple models just use lists with single entries")
    arg_tup = ()
    str_lens = []
    type_list = []
    M = 1
    for key in arg_keys:
        str_vals = [str(entry) for entry in argarrs[key]]
        str_lens.extend([len(entry) for entry in str_vals])
        type_list.append(argarrs[key].dtype)
        #print key,str_vals,str_lens
        M *= len(argarrs[key])
        #print str_vals,str_lens
        arg_tup += (str_vals,)
    #print 'debug',type_list
    max_str_lens = max(str_lens)
    all_arg_combos = np.zeros((M,len(arg_keys)),dtype='S{0:d}'.format(max_str_lens))
    all_arg_combos = pd.DataFrame(cartesian(arg_tup,all_arg_combos),columns=arg_keys)
    for i,currtype in enumerate(type_list):
        if currtype == np.bool:
            all_arg_combos[arg_keys[i]] = (all_arg_combos[arg_keys[i]] == 'True')
        else:
            all_arg_combos[arg_keys[i]] = all_arg_combos[arg_keys[i]].astype(currtype)
    return all_arg_combos

def run_all_args(predictors,target,option_df,func):#option_df is a dataframe containing all permutations of the fit options, func is a function that will fit a sklearn model (e.g. run_rforest below)
    
    for i in range(option_df.shape[0]):
        func(predictors,target,option_df[i:i+1].to_dict())

def run_rforest(predictors,target,forest_arg_dict):
    rforest = RandomForestRegressor(**forest_arg_dict)
    rforest.fit(predictors,target)
    return rforest

def run_logreg(predictors,target,logreg_arg_dict):
    logreg = LogisticRegression(**logreg_arg)
    logreg.fit(predictors,target)
    return logreg

def run_svg(predictors,target,unique_targets,svginstance):#Note the difference here; the SVG is a streaming algorithm so it must already be instantiated
    svginstance.partial_fit(predictors,target,unique_targets)


if __name__ == "__main__":
    if len(sys.argv) != 5:
        sys.exit("Syntax: [Table info pickle file] [Number of rows per forest] [Number of forest iterations] [Fraction of data set for validation]")
    #Compute all permutations of regressor options you want to vary:
    option_dict = {'n_estimators':[10],'criterion':['mse'],'max_depth':[5,6],'min_samples_split':[2],'min_samples_leaf':[1],'max_features':['auto','sqrt'],'n_jobs':[1]}
    combined_args_df = combine_args(**option_dict)

    info_dict = {}#Temporary due to broken pickling in code_predictors
    info_dict['target_col'] = 'target'
    info_dict['predictor_col_list'] = ['origin_{0:d}'.format(i) for i in range(103)]
    info_dict['predictor_col_list'].extend(['dest_{0:d}'.format(i) for i in range(103)])
    info_dict['predictor_col_list'].extend(['uniquecarrier_{0:d}'.format(i) for i in range(23)])
    info_dict['predictor_col_list'].extend(['dayofweek_{0:d}'.format(i) for i in range(6)])
    info_dict['predictor_col_list'].extend(['monthnum_{0:d}'.format(i) for i in range(11)])
    info_dict['predictor_col_list'].extend(['hour_{0:d}'.format(i) for i in range(23)])
    #print len(info_dict['predictor_col_list'])
    info_pkl = open(sys.argv[1],'rb')
    #info_dict = pickle.load(info_pkl)
    info_pkl.close()

    numrows = int(sys.argv[2])
    numiters = int(sys.argv[3])
    valfrac = float(sys.argv[4])
    #run_all_args(None,None,combined_args_df,run_rforest)
