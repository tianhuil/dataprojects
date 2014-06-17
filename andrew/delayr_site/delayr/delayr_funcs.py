import sys
import os
import numpy as np
import datetime as dt
import pandas as pd

#This little bit of code lets me import from the project's scripts directory.
projectdir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))#the main project directory
scriptsdir = os.path.join(projectdir,'scripts')
sys.path.append(scriptsdir)
import flightfuncs as ff
import predict_delays_logreg as pdl

def make_prediction(inpdict):
    print inpdict
    datestring = inpdict['date'][0]
    timestring = inpdict['time'][0]
    date = dt.datetime.strptime(datestring + " " + timestring,'%m/%d/%Y %I:%M %p')
    predictorlist = ['origin','dest','dayofweek(flightdate)','uniquecarrier']
    predictorvals = [inpdict['origin'],inpdict['dest'],date.weekday()+2,inpdict['uniquecarrier']]#The +2 is to put the day of the week in the right MySQL units.
    predictordict = {predictorlist[i]:pd.Series(predictorvals[i]) for i in range(len(predictorlist))}
    predictor_df = pd.DataFrame(predictordict)
    try:
        predictor_df['dayofweek(flightdate)'] = predictor_df['dayofweek(flightdate)'].astype(np.int)
    except:
        pass
    

    #Get the filename of the pickle we should be using:
    directory = os.path.join(projectdir,'saved_models/')
    pkl_filename = ff.get_model_filename(date,predictorlist,dir_structure=directory)
    print pkl_filename

    output_df = pdl.predict_delay(predictor_df,pkl_filename)

    return_dict = {}
    return_dict['user_prediction'] = output_df

    return return_dict
    

if __name__ == "__main__":
    pass
