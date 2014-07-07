import sys
import os
import numpy as np
import datetime as dt
import pandas as pd
import importlib
from django.db import connection
from delayr.forms import AirportForm,AirlineForm,DateTimeForm

#delayr_funcs contains a bunch of useful functions for getting between my web frontend and the ML backend.

#This little bit of code lets me import from the project's scripts directory. This is probably not the ideal way to do it, but it was certainly the easiest!
projectdir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))#the main project directory
scriptsdir = os.path.join(projectdir,'scripts')
sys.path.append(scriptsdir)
import flightfuncs as ff
import predict_delays_logreg as pdl
import global_vars as gv
#import login_credentials as creds

def prep_passed_df(input_string,row_order_column=None,column_order_row=None,remove_row_order_column=True,remove_column_order_row=True):
    '''
    Converts a dataframe passed as json back into a dataframe.

    Arguments:
    input_string -- the input json.
    row_order_column -- if there is a column which contains how the rows should be ordered, name it (default = None).
    column_order_row -- if there is a row which contains how the columns should be ordered, name it (default = None).
    remove_row_order_column -- strip the row ordering column after using it (default = True).
    remove_column_order_row -- strip the column ordering row after using it (default = True).

    Returns:
    df -- the dataframe.
    '''
    #Get the string into a pandas dataframe:
    df = pd.read_json(eval(input_string))

    #Sort the data frame if necessary:
    if row_order_column != None:
        df = df.sort(columns=row_order_column)
        if remove_row_order_column:
            df = df.drop(row_order_column,1)
    if column_order_row != None:
        df = df.T.sort(columns=column_order_row).T
        if remove_column_order_row:
            df = df[df.index.values != column_order_row]
    return df

def fix_weekday(dayofweek,offset=2):
    '''
    Converts between datetime's notion of the day of the week and MySQL's:
    '''
    dayofweek += offset
    if dayofweek > 7:
        dayofweek -= 7
    return dayofweek

def get_full_names(origin,dest,uniquecarrier):
    '''
    A kludge to map the values of the select choiceboxes back to full names.

    Arguments:
    origin -- the 3 character origin airport code.
    dest -- the 3 character destination airport code.
    uniquecarrier -- the 2 character carrier code.

    Returns:
    a tuple containing the full names of the origin airport, destination airport, and carrier.

    '''
    origin_full = [entry[1] for entry in AirportForm.airport_choice_tup if entry[0] == origin]
    dest_full = [entry[1] for entry in AirportForm.airport_choice_tup if entry[0] == dest]
    carrier_full = [entry[1] for entry in AirlineForm.airline_choice_tup if entry[0] == uniquecarrier]
    return origin_full[0],dest_full[0],carrier_full[0]

def make_predictions(inpdict,pickle_dict,other_times=True,date_range=3,other_options=3):
    '''
    Predict the user's itinerary, as well as itineraries at nearby times/dates, and if similar
    itineraries exist predict them too. This is the main function in the site, and it powers
    the calculations behind the data shown to the user.

    Arguments:
    inpdict -- a dictionary containing the parameters of the user's search.
    pickle_dict -- a dictionary containing the model pickles, keyed on the filenames of the pickles.
    other_times -- Predict delays for other times-of-day (default=True).
    date_range -- how many days before/after the selected day to predict (default = 3).
    other_options -- maximum number of alternative itineraries to display (default = 3).

    Returns:
    return_dict -- a dictionary containing all the results of the predictions.
    '''
    #Some prepwork, with the location of the learned models (the pickles) hardcoded in:
    tableprefix = 'flightdelays'
    pkl_directory = os.path.join(projectdir,'saved_models/')
    return_dict = {}
    #Reading in the date and time and making a datetime object:
    datestring = inpdict['date'][0]
    timestring = inpdict['time'][0]
    date = dt.datetime.strptime(datestring + " " + timestring,'%m/%d/%Y %I:%M %p')
    #What things we're going to base our prediction on (the month and time of day are encoded in the different pickles):
    predictorlist = ['origin','dest','dayofweek(flightdate)','uniquecarrier']

    #Get the delay time prediction the user asked for:
    user_predictorvals = [inpdict['origin'],inpdict['dest'],fix_weekday(date.weekday()),inpdict['uniquecarrier']]
    user_predictor_df = make_predictor_df(predictorlist,user_predictorvals)
    #Get the filename of the pickle we should be using:
    user_pkl_filename = ff.get_model_filename(date,predictorlist,tableprefix=tableprefix,dir_structure=pkl_directory)
    
    user_output_df = pdl.predict_delay(user_predictor_df,user_pkl_filename,pickle_obj=pickle_dict[user_pkl_filename])

    return_dict['user_prediction'] = user_output_df

    #Get predicted delay times for the other times of the day:
    if other_times:
        #Figure out what the times actually *are*:
        all_time_keys = np.array(gv.hours.keys())
        time_period_start = np.array([gv.hours[key][0] for key in all_time_keys])
        sorted_idxs = np.argsort(time_period_start)
        sorted_time_keys = all_time_keys[sorted_idxs]
        all_time_df_list = []
        #Find the pickle file for each time and compute the prediction:
        for i,time_period in enumerate(sorted_time_keys):
            time_table_name = tableprefix+"_"+ff.get_month_name(date)+"_"+time_period
            time_pkl_filename = ff.make_model_pickle_filename(time_table_name,predictorlist,dir_structure=pkl_directory)
            time_df = pdl.predict_delay(user_predictor_df,time_pkl_filename,pickle_obj=pickle_dict[time_pkl_filename])
            all_time_df_list.append(time_df)
        #Put the predictions all together into a dataframe, add it to the returned dictionary:
        all_time_df = combo_dfs(*all_time_df_list)
        all_time_df = all_time_df.set_index(sorted_time_keys)
        col_index_df = pd.DataFrame(np.arange(len(all_time_df.columns.values)).reshape(1,len(all_time_df.columns.values)),index=['col_order'],columns=all_time_df.columns.values)
        all_time_df = all_time_df.append(col_index_df)
        all_time_df['order'] = range(all_time_df.shape[0])#Add column to order the rows
        return_dict['all_time_prediction'] = all_time_df

    #Get predicted delay times for the days around the selected date:
    if date_range != None:
        all_date_df_list = []
        all_date_strings = []
        #Get the right pickle files, make the prediction:
        for i in range(-date_range,date_range+1):
            offsetdate = date + dt.timedelta(days=i)
            time_predictorvals = [inpdict['origin'],inpdict['dest'],fix_weekday(offsetdate.weekday()),inpdict['uniquecarrier']]#The +2 is to put the day of the week in the right MySQL units.
            date_predictor_df = make_predictor_df(predictorlist,time_predictorvals)
            date_pkl_filename = ff.get_model_filename(offsetdate,predictorlist,tableprefix=tableprefix,dir_structure=pkl_directory)

            date_df = pdl.predict_delay(date_predictor_df,date_pkl_filename,pickle_obj=pickle_dict[date_pkl_filename])
            all_date_df_list.append(date_df)
            #all_date_strings.append(offsetdate.strftime('%B'))
            all_date_strings.append(offsetdate.strftime('%m-%d'))
        #Put in a dataframe for output:
        all_date_df = combo_dfs(*all_date_df_list)
        all_date_df = all_date_df.set_index(np.array(all_date_strings))
        col_index_df = pd.DataFrame(np.arange(len(all_date_df.columns.values)).reshape(1,len(all_date_df.columns.values)),index=['col_order'],columns=all_date_df.columns.values)
        all_date_df = all_date_df.append(col_index_df)
        all_date_df['order'] = range(all_date_df.shape[0])
        return_dict['all_date_prediction'] = all_date_df

    #Check if there are other itineraries in the database that are similar to the one the user chose, then make predictions for those:
    if other_options != None:
        #Query the db to find market ids for the two airports. Make sure both are found.
        #First, figuring out what the database is. This is going to be kludgey as balls, but I think it'll work (note 7/3/14: yep, works):
        monthname = ff.get_month_name(date)
        timename = ff.get_time_name(date)
        dbname = 'Flightdelays{month}{time}'.format(month=monthname[:1].upper()+monthname[1:],time=timename[:1].upper()+timename[1:])
        dbname_sql = 'flightdelays_{month}_{time}'.format(month=monthname,time=timename)
        #print dbname
        #Importing the database class:
        model_module = importlib.import_module('delayr.models')
        flightclass = getattr(model_module,dbname)

        #Get the market ids for the origin and destination airports:
        market_ids_qset = flightclass.objects.raw("""select fid,origin,origincitymarketid from {0:s} where origin = '{1:s}' or origin = '{2:s}' group by origin""".format(dbname_sql,inpdict['origin'][0],inpdict['dest'][0]))
        market_ids = dict([(entry.origin,entry.origincitymarketid) for entry in market_ids_qset])
        origin_market_id = market_ids[inpdict['origin'][0]]
        dest_market_id = market_ids[inpdict['dest'][0]]
        #Query the db to find all distinct flights with the same origin and destination market ids. if it returns zero (user could ask for hawaii air flights between newark and jfk, for instance, which is nonsensical but will output a prediction) exit.
        cursor = connection.cursor()
        columns = ['origin','dest','uniquecarrier','orig_airportname','dest_airportname','airlinename']
        cursor.execute("""select distinct fd.origin,fd.dest,fd.uniquecarrier,aorig.airportname,adest.airportname,aline.fullname from {0:s} as fd join airports as aorig on fd.origin=aorig.origin join airports as adest on fd.dest=adest.origin join airlinenames as aline on fd.uniquecarrier=aline.uniquecarrier where origincitymarketid={1:d} and destcitymarketid={2:d} and year(fd.flightdate) > 2012""".format(dbname_sql,origin_market_id,dest_market_id))
        result = list(cursor.fetchall())
        if len(result) > 0:
            #print len(result)
            result_df = pd.DataFrame(result,columns=columns)
            #Cut out the itinerary that the user selected, if necessary:
            searched_itinerary = (result_df['origin'] == inpdict['origin'][0]) & (result_df['dest'] == inpdict['dest'][0]) & (result_df['uniquecarrier'] == inpdict['uniquecarrier'][0])
            pd.set_option('display.max_columns',10)
            pd.set_option('display.width',1000)
            #print result_df
            result_df = result_df[searched_itinerary == False]
            result_df['delay'] = 0.
            #print result_df
            if result_df.shape[0] > 0:
                #Predict the delay time for each other itinerary:
                for i in result_df.index.values:
                    #Only have to change a few values from the original searched itinerary, so make a copy of that dataframe and edit what you need to:
                    temp_predictor_df = user_predictor_df.copy()
                    temp_predictor_df.xs('origin',axis=1,copy=False)[0] = result_df.xs('origin',axis=1,copy=False)[i]
                    temp_predictor_df.xs('dest',axis=1,copy=False)[0] = result_df.xs('dest',axis=1,copy=False)[i]
                    temp_predictor_df.xs('uniquecarrier',axis=1,copy=False)[0] = result_df.xs('uniquecarrier',axis=1,copy=False)[i]
                    temp_output_df = pdl.predict_delay(temp_predictor_df,user_pkl_filename,pickle_obj=pickle_dict[user_pkl_filename])
                    result_df.xs('delay',axis=1,copy=False)[i] = temp_output_df.icol(0)
                #Adjust the naming of the dataframe columns:
                all_result_cols = result_df.columns.values
                all_result_cols[-1] = temp_output_df.columns.values[0]
                result_df.columns = all_result_cols
                #Sort the predictions, take the N best:
                sorted_result_df = result_df.sort(all_result_cols[-1],ascending=False)
                trimmed_sorted_result_df = sorted_result_df[:other_options]
                #print "test1",trimmed_sorted_result_df
                #print "test2",user_output_df
                #Get the full names for the itinerary the user searched for, add to the output dataframe:
                user_origin,user_dest,user_carrier = get_full_names(inpdict['origin'][0],inpdict['dest'][0],inpdict['uniquecarrier'][0])
                full_user_output_df = pd.DataFrame([[inpdict['origin'][0],inpdict['dest'][0],inpdict['uniquecarrier'][0],user_origin,user_dest,user_carrier,user_output_df[user_output_df.columns.values[0]].values[0]]],columns=trimmed_sorted_result_df.columns)
                trimmed_sorted_result_df = trimmed_sorted_result_df.append(full_user_output_df,ignore_index=True)
                #Determine what color to make the user's itinerary:
                other_option_colorname = 'warning'
                if trimmed_sorted_result_df[trimmed_sorted_result_df.columns.values[-1]].values[-1] > trimmed_sorted_result_df[trimmed_sorted_result_df.columns.values[-1]].values[0]:
                    other_option_colorname = 'success'
                elif trimmed_sorted_result_df[trimmed_sorted_result_df.columns.values[-1]].values[-2] > trimmed_sorted_result_df[trimmed_sorted_result_df.columns.values[-1]].values[-1]:
                    other_option_colorname = 'danger'
                return_dict['other_option_colorname'] = other_option_colorname
                stringlist = []
                #fill out the list of the best alternate options, put it in the output dictionary:
                for i in range(trimmed_sorted_result_df.shape[0]):
                    rowvals = trimmed_sorted_result_df.irow(i)
                    testdict = {'display_string':"{0:s} to {1:s} on {2:s} (prediction: {3:.2f}% chance of delay {4:s} minutes)".format(rowvals['orig_airportname'],rowvals['dest_airportname'],rowvals['airlinename'],rowvals[all_result_cols[-1]]*100.,all_result_cols[-1]),'orig':rowvals['origin'],'dest':rowvals['dest'],'uniquecarrier':rowvals['uniquecarrier']}
                    stringlist.append(testdict)
                return_dict['other_option_prediction'] = stringlist
            
    return return_dict

def combo_dfs(*args):
    '''
    Combine multiple dataframes with identical column headings.

    Arguments:
    *args -- individual dataframes.

    Returns:
    out_df -- a combined dataframe.
    '''
    if args:
        #print 'debug',args[0]
        out_df = pd.DataFrame(columns=args[0].columns.values)
        #print out_df.columns.values
        for i,arg in enumerate(args):
            #print arg
            #if i == 0:
            #    out_df = pd.DataFrame(columns=arg.columns.values)
            out_df = out_df.append(arg)
            #print 'test',out_df
        return out_df


def make_predictor_df(predictorlist,predictorvals):
    '''
    Prepare a dataframe of all the predictors.

    Arguments:
    predictorlist -- a list of predictor names.
    predictorvals -- a list of predictor values.

    Returns:
    predictor_df -- a 1-row dataframe of the predictors.
    '''
    predictordict = {predictorlist[i]:pd.Series(predictorvals[i]) for i in range(len(predictorlist))}
    predictor_df = pd.DataFrame(predictordict)
    try:
        predictor_df['dayofweek(flightdate)'] = predictor_df['dayofweek(flightdate)'].astype(np.int)
    except:
        pass
    return predictor_df
    

#Predict what the user wants:
def make_prediction(inpdict):
    '''
    Run the predictive model on a user's input. I believe this has been superseded by make_predictions.

    Arguments:
    inpdict -- a dictionary containing the parameters of the user's search.

    Returns:
    return_dict -- a dictionary containing the result of the prediction.
    '''
    #print inpdict
    datestring = inpdict['date'][0]
    timestring = inpdict['time'][0]
    date = dt.datetime.strptime(datestring + " " + timestring,'%m/%d/%Y %I:%M %p')
    predictorlist = ['origin','dest','dayofweek(flightdate)','uniquecarrier']
    predictorvals = [inpdict['origin'],inpdict['dest'],date.weekday()+2,inpdict['uniquecarrier']]#The +2 is to put the day of the week in the right MySQL units.
    predictor_df = make_predictor_df(predictorlist,predictorvals)
    
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
