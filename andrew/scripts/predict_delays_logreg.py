import sys
import os
import numpy as np
import pandas as pd
import datetime as dt
import cPickle as pickle

import flightfuncs as ff    

#Unpickle the model and compute the delay probability:
def predict_delay(data,model_pickle_file):
    f = open(model_pickle_file,'rb')
    model_dict = pickle.load(f)
    f.close()
    data_coded = model_dict['predictor_coder'].code_data(data)
    probabilities = model_dict['model'].predict_proba(data_coded)
    #print "debug: ",probabilities
    timecodes = [model_dict['target_coder'].bin_text_dict[key] for key in range(probabilities.shape[1])]
    #timecodes = [model_dict['target_coder'].bin_text_name_list[i] for i in range(probabilities.shape[1])]
    output_df = pd.DataFrame(probabilities,columns=timecodes)
    return output_df

if __name__ == "__main__":
    if len(sys.argv) != 5:
        sys.exit("Syntax: [date (mm/dd)] [time (hh:mm, 24 hour clock)] [CSV list of predictor names] [CSV list of predictor values]")

    predictorlist = sys.argv[3].split(',')
    predictorvals = sys.argv[4].split(',')
    
    if len(predictorlist) != len(predictorvals):
        sys.exit("Predictor IDs and values must have same length! Exiting...")
    predictordict = {predictorlist[i]:pd.Series(predictorvals[i]) for i in range(len(predictorlist))}
    predictor_df = pd.DataFrame(predictordict)
    try:
        predictor_df['dayofweek(flightdate)'] = predictor_df['dayofweek(flightdate)'].astype(np.int)
    except:
        pass
        
    #Get the date into a datetime object:
    try:
        dt_date = dt.datetime.strptime(sys.argv[1] + " " + sys.argv[2],'%m/%d %H:%M')
    except(ValueError):
        sys.exit("Cannot process time and/or date! Check format and try again!")

    #Get the filename of the pickle we should be using:
    pkl_filename = ff.get_model_filename(dt_date,predictorlist)

    #Check if it exists:
    if not os.path.isfile(pkl_filename):
        sys.exit("Pickled model file {0:s} does not exist! Exiting...".format(pkl_filename))

    predicted_df = predict_delay(predictor_df,pkl_filename)
    print predicted_df

    print list(predicted_df.columns)
    print list(predicted_df.irow(0))
