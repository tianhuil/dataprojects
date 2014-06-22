import sys
import os
import numpy as np
import datetime as dt
import pandas as pd
import importlib
from django.db import connection

#This little bit of code lets me import from the project's scripts directory.
projectdir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))#the main project directory
scriptsdir = os.path.join(projectdir,'scripts')
sys.path.append(scriptsdir)
import flightfuncs as ff
import predict_delays_logreg as pdl
import global_vars as gv
#import login_credentials as creds

#Reads a df passed as a json string (to pass info through urls):
def prep_passed_df(input_string,row_order_column=None,column_order_row=None,remove_row_order_column=True,remove_column_order_row=True):
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

#Convert between datetime's notion of the day of the week and MySQL's:
def fix_weekday(dayofweek,offset=2):
    dayofweek += offset
    if dayofweek > 7:
        dayofweek -= 7
    return dayofweek

#Predict what the user wants, as well as some other interesting things:
def make_predictions(inpdict,other_times=True,date_range=3,other_options=3):
    tableprefix = 'flightdelays'
    pkl_directory = os.path.join(projectdir,'saved_models/')
    return_dict = {}
    datestring = inpdict['date'][0]
    timestring = inpdict['time'][0]
    date = dt.datetime.strptime(datestring + " " + timestring,'%m/%d/%Y %I:%M %p')
    predictorlist = ['origin','dest','dayofweek(flightdate)','uniquecarrier']

    #Get the delay time prediction the user asked for:
    user_predictorvals = [inpdict['origin'],inpdict['dest'],fix_weekday(date.weekday()),inpdict['uniquecarrier']]#The +2 is to put the day of the week in the right MySQL units.
    user_predictor_df = make_predictor_df(predictorlist,user_predictorvals)
    #Get the filename of the pickle we should be using:
    user_pkl_filename = ff.get_model_filename(date,predictorlist,tableprefix=tableprefix,dir_structure=pkl_directory)

    user_output_df = pdl.predict_delay(user_predictor_df,user_pkl_filename)

    return_dict['user_prediction'] = user_output_df

    if other_times:
        #Get predicted delay times for the other times of the day:
        all_time_keys = np.array(gv.hours.keys())
        time_period_start = np.array([gv.hours[key][0] for key in all_time_keys])
        sorted_idxs = np.argsort(time_period_start)
        sorted_time_keys = all_time_keys[sorted_idxs]
        all_time_df_list = []
        for i,time_period in enumerate(sorted_time_keys):
            time_table_name = tableprefix+"_"+ff.get_month_name(date)+"_"+time_period
            time_pkl_filename = ff.make_model_pickle_filename(time_table_name,predictorlist,dir_structure=pkl_directory)
            time_df = pdl.predict_delay(user_predictor_df,time_pkl_filename)
            all_time_df_list.append(time_df)
        all_time_df = combo_dfs(*all_time_df_list)
        all_time_df = all_time_df.set_index(sorted_time_keys)
        col_index_df = pd.DataFrame(np.arange(len(all_time_df.columns.values)).reshape(1,len(all_time_df.columns.values)),index=['col_order'],columns=all_time_df.columns.values)
        all_time_df = all_time_df.append(col_index_df)
        all_time_df['order'] = range(all_time_df.shape[0])#Add column to order the rows
        return_dict['all_time_prediction'] = all_time_df

    if date_range != None:
        all_date_df_list = []
        all_date_strings = []
        #Get predicted delay times for the days around the selected date:
        for i in range(-date_range,date_range+1):
            offsetdate = date + dt.timedelta(days=i)
            time_predictorvals = [inpdict['origin'],inpdict['dest'],fix_weekday(offsetdate.weekday()),inpdict['uniquecarrier']]#The +2 is to put the day of the week in the right MySQL units.
            date_predictor_df = make_predictor_df(predictorlist,time_predictorvals)
            date_pkl_filename = ff.get_model_filename(offsetdate,predictorlist,tableprefix=tableprefix,dir_structure=pkl_directory)

            date_df = pdl.predict_delay(date_predictor_df,date_pkl_filename)
            all_date_df_list.append(date_df)
            #all_date_strings.append(offsetdate.strftime('%B'))
            all_date_strings.append(offsetdate.strftime('%m-%d-%Y'))
        all_date_df = combo_dfs(*all_date_df_list)
        all_date_df = all_date_df.set_index(np.array(all_date_strings))
        col_index_df = pd.DataFrame(np.arange(len(all_date_df.columns.values)).reshape(1,len(all_date_df.columns.values)),index=['col_order'],columns=all_date_df.columns.values)
        all_date_df = all_date_df.append(col_index_df)
        all_date_df['order'] = range(all_date_df.shape[0])
        return_dict['all_date_prediction'] = all_date_df

    if other_options != None:
        #Query the db to find market ids for the two airports. Make sure both are found.
        #First, figuring out what the database is. This is going to be kludgey as balls, but I think it'll work:
        monthname = ff.get_month_name(date)
        timename = ff.get_time_name(date)
        dbname = 'Flightdelays{month}{time}'.format(month=monthname[:1].upper()+monthname[1:],time=timename[:1].upper()+timename[1:])
        dbname_sql = 'flightdelays_{month}_{time}'.format(month=monthname,time=timename)
        print dbname
        #Importing the database class:
        model_module = importlib.import_module('delayr.models')
        flightclass = getattr(model_module,dbname)

        #Get the market ids for the origin and destination airports:
        market_ids_qset = flightclass.objects.raw("""select fid,origin,origincitymarketid from {0:s} where origin = '{1:s}' or origin = '{2:s}' group by origin""".format(dbname_sql,inpdict['origin'][0],inpdict['dest'][0]))
        market_ids = dict([(entry.origin,entry.origincitymarketid) for entry in market_ids_qset])
        origin_market_id = market_ids[inpdict['origin'][0]]
        dest_market_id = market_ids[inpdict['dest'][0]]
        print inpdict['origin'][0],origin_market_id
        print inpdict['dest'][0],dest_market_id
        cursor = connection.cursor()
        columns = ['origin','dest','uniquecarrier','orig_airportname','dest_airportname','airlinename']
        cursor.execute("""select distinct fd.origin,fd.dest,fd.uniquecarrier,aorig.airportname,adest.airportname,aline.fullname from {0:s} as fd join airports as aorig on fd.origin=aorig.origin join airports as adest on fd.dest=adest.origin join airlinenames as aline on fd.uniquecarrier=aline.uniquecarrier where origincitymarketid={1:d} and destcitymarketid={2:d} and year(fd.flightdate) > 2012""".format(dbname_sql,origin_market_id,dest_market_id))
        result = list(cursor.fetchall())
        result_df = pd.DataFrame(result,columns=columns)
        #flight_options_qset = flightclass.objects.raw("""select distinct fd.origin,fd.dest,fd.uniquecarrier,aorig.airportname,adest.airportname,aline.fullname from {0:s} as fd join airports as aorig on fd.origin=aorig.origin join airports as adest on fd.dest=adest.origin join airlinenames as aline on fd.uniquecarrier=aline.uniquecarrier where origincitymarketid={1:d} and destcitymarketid={2:d} and year(fd.flightdate) > 2012""".format(dbname_sql,origin_market_id,dest_market_id))
        #testlist = [entry for entry in flight_options_qset]
        searched_itinerary = (result_df['origin'] == inpdict['origin'][0]) & (result_df['dest'] == inpdict['dest'][0]) & (result_df['uniquecarrier'] == inpdict['uniquecarrier'][0])
        pd.set_option('display.max_columns',10)
        pd.set_option('display.width',1000)
        print result_df
        print result_df[searched_itinerary == False]
        #Query the db to find all distinct flights with the same origin and destination market ids. if it returns zero (user could ask for hawaii air flights between newark and jfk, for instance, which is nonsensical but will output a prediction) exit.

        #select distinct aorig.airportname,adest.airportname,aline.fullname from flightdelays_sep_early as fd join airports as aorig on fd.origin=aorig.origin join airports as adest on fd.dest=adest.origin join airlinenames as aline on fd.uniquecarrier=aline.uniquecarrier where origincitymarketid=31703 and destcitymarketid=30977 and year(fd.flightdate) > 2012;
        
        #cut out the flight that the user queried. if that was the one entry in the dataframe, exit.
        
        #Estimate the delay times for each of the remaining flights.

        #Sort the delay times (probably based on on-time percentage) and report the top N alternatives. Perhaps a stacked bar chart, with your flight in there as well?
        pass
            
    return return_dict

def combo_dfs(*args):
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
    predictordict = {predictorlist[i]:pd.Series(predictorvals[i]) for i in range(len(predictorlist))}
    predictor_df = pd.DataFrame(predictordict)
    try:
        predictor_df['dayofweek(flightdate)'] = predictor_df['dayofweek(flightdate)'].astype(np.int)
    except:
        pass
    return predictor_df
    

#Predict what the user wants:
def make_prediction(inpdict):
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
