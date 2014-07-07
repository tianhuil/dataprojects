import numpy as np
import MySQLdb as mdb
import pandas as pd
import sklearn.feature_extraction
import sys

import load_credentials_nogit as creds
import global_vars as gv
#This file contains useful classes and functions for doing querying, encoding, and modeling of my flight data.

class TimeCoder:
    '''
    Bin up delay times/cancellations. It's designed to be portable, so you can set it up with your training data and then use it later.
    
    '''
    def __init__(self,timebins):
        '''
        Instantiate the class.

        Arguments:
        timebins -- a list of times (in minutes) that make your bin edges. Note that the TimeCoder will automatically add bin edges at - and + infinity.
        '''
        self.timebins = timebins
        self.bin_text_dict = {}
        self.bin_text_name_list = []#Can't use this until I retrain the model
    def time_encode(self,times,cancellations):
        '''
        Encode the times and cancellations.

        Arguments:
        times -- an array of delay times (in minutes).
        cancellations -- a boolean array of cancellation information.

        Returns:
        coded_array -- an array containing the proper codes for each element in the input arrays.
        '''
        if self.timebins:
            coded_array = np.zeros(len(times),dtype=np.int)
            self.bin_text_dict[0] = '<{0:d}'.format(self.timebins[0])
            self.bin_text_name_list.append('<{0:d}'.format(self.timebins[0]))
            currcode = 1
            for i in range(1,len(self.timebins)):
                coded_array[(times >= self.timebins[i-1]) & (times < self.timebins[i])] = currcode
                self.bin_text_dict[currcode] = '{0:d}-{1:d}'.format(self.timebins[i-1],self.timebins[i])
                self.bin_text_name_list.append('{0:d}-{1:d}'.format(self.timebins[i-1],self.timebins[i]))
                currcode += 1
            coded_array[(times >= self.timebins[-1])] = currcode
            self.bin_text_dict[currcode] = '>={0:d}'.format(self.timebins[-1])
            self.bin_text_name_list.append('>={0:d}'.format(self.timebins[-1]))
            currcode += 1
            coded_array[(cancellations > 1.e-5)] = currcode
            self.bin_text_dict[currcode] = 'Cancelled'
            return coded_array.astype(np.str)
        else:
            raise ValueError("TimeCoder.timebins is empty!")

class PredictorCoder:
    '''
    Preps a dataframe of predictors, including doing fast one-hot encoding of categorical variables.
    Can also be used to code features after the model has been trained.
    
    '''
    def __init__(self):
        '''
        Instantiate the class.
        
        '''
        self.continuous_predictors = None
        self.discrete_predictors = None
        self.discrete_predictor_mapping = None

    def train(self,data,continuous_predictors,discrete_predictors):
        '''
        Code the predictors on a training set. This set will then define all the values any categorical variables can take.
        
        Arguments:
        data -- a Pandas dataframe, with column labels corresponding to the names of the predictors.
        continuous_predictors -- a list of names for predictors which are continuous.
        discrete_predictors -- a list of names for predictors which are discrete.
        
        Returns:
        coded_arr -- a 2D numpy array containing the coded predictors
        
        '''
        #Make sure the predictors are in the data:
        self.check_predictors(data,continuous_predictors)
        self.check_predictors(data,discrete_predictors)

        #Assuming that's all kosher, save the predictors:
        self.continuous_predictors = continuous_predictors
        self.discrete_predictors = discrete_predictors
        self.discrete_predictor_mapping = [None]*len(discrete_predictors)

        #Code up the data:
        coded_arr = self.code_data(data)
        return coded_arr

    def code_data(self,data):
        '''
        Do the actual encoding. This is called as part of the train function above, but after the coder has been
        trained this function can be called independently.
        
        Arguments:
        data -- a Pandas dataframe, with column labels corresponding to the names of the predictors.
        
        Returns:
        coded_arr -- a 2D numpy array containing the coded predictors
        '''
        if self.continuous_predictors == None or self.discrete_predictors == None or self.discrete_predictor_mapping == None:
            raise TypeError("Must train predictor before you can code on it!")
        
        #Prep the 2D array:
        coded_arr = np.zeros((1,data.shape[0]))

        #First do any continuous predictors (easy):
        if self.continuous_predictors:
            coded_arr = np.vstack((coded_arr,data[self.continuous_predictors].values.T))

        #Next, do the discrete predictors (harder):
        for i, pred in enumerate(self.discrete_predictors):
            stacked_codes = self.one_hot_code(data[pred].values,i)
            coded_arr = np.vstack((coded_arr,stacked_codes))

        return coded_arr[1:,:].T

    def one_hot_code(self,values,prednum):
        '''
        Does the actual one-hot coding of discrete predictors, and is not designed to be called on its own.
        
        '''
        if self.discrete_predictor_mapping[prednum] == None:
            unique_values = np.unique(values)
            self.discrete_predictor_mapping[prednum] = dict(zip(unique_values,range(len(unique_values))))

        codes = [self.discrete_predictor_mapping[prednum][key] for key in values]
        code_arr = np.zeros((len(self.discrete_predictor_mapping[prednum].keys()),len(values)))
        code_arr[codes,range(len(values))] = 1.

        return code_arr
    
    def check_predictors(self,data,predictors):
        '''
        Checks to see if the predictors aren't in the dataframe, raises an exception in that case.
        '''
        datacols = data.columns.values
        if np.sum(np.in1d(predictors,datacols)) < len(predictors):
            raise ValueError("Not all predictors in dataframe!")

def make_model_pickle_filename(tablename,predlist,dir_structure="../saved_models/"):
    '''
    Get the filename of the saved pickle file based on some inputs.

    Arguments:
    tablename -- the name of the sql table.
    predlist -- a list of feature names.
    dir_structure -- a path to the directory the pickle files are saved in (default = ../saved_models/).

    Returns:
    A string with the proper filename.
    '''
    return "{dir}{table}_{preds}.pkl".format(dir=dir_structure,table=tablename,preds='-'.join(np.sort(predlist)).replace('(','~').replace(')','~'))

#A function to take in a date, time, and predictors and determine the proper model to use:
def get_model_filename(datetime_obj,predictorlist,tableprefix='flightdelays',dir_structure="../saved_models/"):
    '''
    A wrapper around make_model_pickle_filename for a little ease-of-use.

    Arguments:
    datetime_obj -- a python datetime object.
    predictorlist -- a list of feature names.
    tableprefix -- the root of the table names (for the sharded tables) (default = flightdelays).
    dir_structure -- the path of the files (default = ../saved_models/).

    Returns:
    filename -- the model filename.
    '''
    #Convert the time into the proper format:
    int_time = datetime_obj.hour*100 + datetime_obj.minute
    time_name = get_time_name(datetime_obj)

    #Convert the month into the proper format:
    month_name = get_month_name(datetime_obj)

    #Get the required filename:
    filename = make_model_pickle_filename(tableprefix+"_"+month_name+"_"+time_name,predictorlist,dir_structure=dir_structure)
    return filename

def get_time_name(datetime_obj):
    '''
    Converts a time to the english names I've assigned each part of the day.

    Argument:
    datetime_obj -- a python datetime object.

    Returns:
    time_name -- the name bin that the time falls into.
    '''
    int_time = datetime_obj.hour*100 + datetime_obj.minute
    time_name = None
    for key in gv.hours.keys():
        if int_time >= gv.hours[key][0] and int_time < gv.hours[key][1]:
            time_name = key
            break
    if time_name == None:
        raise ValueError("get_model_filename: Time {0:d} outside of allowed range!".format(int_time))

    return time_name
    
    
def get_month_name(datetime_obj):
    '''
    Converts a month number to it's actual name.

    Argument:
    datetime_obj -- a python datetime object.

    Returns:
    month_name -- the name of the month.
    '''
    month_name = None
    for key in gv.months.keys():
        if datetime_obj.month == gv.months[key]:
            month_name = key
            break
    if month_name == None:
        raise ValueError("get_model_filename: Month {0:d} outside of allowed range!".format(datetime_obj.month))

    return month_name
    
def pdf_scoring(estimator, X, y):
    '''
    A cross-validation estimator based on the sum of squared label probabilities.

    Arguments:
    estimator -- the trained scikit-learn estimator to use.
    X -- 2D numpy array of features.
    y -- 1D numpy array of class labels.

    Returns:
    The sum of the squared probabilities given to the correct class for each entry in the data.
    '''
    integer_y = y.astype(np.int16)
    probs = estimator.predict_proba(X)[range(len(integer_y)),integer_y]
    #print "Debug:",probs.min(),probs.max()
    return np.sum(probs**2)

def query_into_pd(con,table,columnlist,subset=None,randomize=False):
    '''
    Queries a database into a Pandas Dataframe.

    Arguments:
    con -- the database connection.
    table -- the name of the table to query.
    columnlist -- a list of column names to query.
    subset -- return only a subset of the total query (default = None).
    randomize -- should the function shuffle the rows of the query (default = False).

    Returns:
    df -- a Pandas dataframe.
    '''
    if columnlist:
        syntax = "Select {cols} from {table}".format(table=table,cols=', '.format(table=table).join(columnlist))
        df = pd.io.sql.read_sql(syntax,con)
        try:
            if int(subset) > 0:
                if int(subset) >= len(df):
                    print "Warning: Requested subset larger than queried data. Using full dataset..."
                else:
                    df = df.ix[np.random.choice(np.arange(len(df)),replace=False,size=int(subset))]
        except TypeError:
            pass
        if randomize:
            indices = df.index.values.copy()
            np.random.shuffle(indices)
            df.reindex(indices)
        return df
    else:
        raise IndexError("No columns to be selected!")
        

if __name__ == "__main__":
    #Testing the functions as I go:
    con = mdb.connect(host=creds.host,user=creds.user,db=creds.database,passwd=creds.password,local_infile=1)
    df = query_into_pd(con,'flightdelays_mar_early',['origin','dest','uniquecarrier','arrdelay','cancelled','diverted'],subset=None)
    print df.shape
