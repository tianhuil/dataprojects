import numpy as np
import pandas as pd
import MySQLdb as mdb
import sys
import time
import cPickle as pickle

import load_credentials_nogit as creds


#Takes in the database, optionally randomizes it, then goes chunk by chunk through the db and codes up the predictors into another db.

#These classes are similar to those in flightfuncs, but they are designed for the streaming data and I'm trying to keep the old stuff that works separate from the new stuff that might break everything, so I'm putting them in here.
class timecode:
    def __init__(self,threshold_times):
        self.threshold_times = threshold_times

    def encode(self,timearray,cancelled):
        encoded_array = np.zeros(len(timearray))
        count = 1
        for i in range(0,len(self.threshold_times)):
            encoded_array[(timearray>=self.threshold_times[i])] = count
            count += 1
        encoded_array[(cancelled == True)] = count
        return encoded_array

    def decode(self,encoded_array):
        codelist = ["<{0:d}".format(self.threshold_times[0])]
        for i in range(1,len(self.threshold_times)):
            codelist.append("{0:d}-{1:d}".format(self.threshold_times[i-1],self.threshold_times[i]))
        codelist.append(">{0:d}".format(self.threshold_times[-1]))
        codelist.append("Cancelled")
        codearr = np.array(codelist)
        return codearr[encoded_array.astype(np.int)]
            
class predictorcode:
    def __init__(self,discrete_predictors,unique_discrete_predictors,continuous_predictors):
        self.continuous_predictors = continuous_predictors
        self.discrete_predictors = discrete_predictors
        self.discrete_predictor_mapping = [None]*len(self.discrete_predictors)
        for i,predname in enumerate(self.discrete_predictors):
            #print i,unique_discrete_predictors[i],range(len(unique_discrete_predictors[i]))
            self.discrete_predictor_mapping[i] = dict(zip(unique_discrete_predictors[i],range(len(unique_discrete_predictors[i]))))

    def code_data(self,data):
        #Assumes data is a pandas dataframe, so first check to make sure it's all there:
        self.check_predictors(data)
        
        #Prep the 2D array:
        coded_arr = np.zeros((1,data.shape[0]))

        #First do any continuous predictors (easy):
        if self.continuous_predictors:
            coded_arr = np.vstack((coded_arr,data[self.continuous_predictors].values.T))

        #Next, do the discrete predictors (harder):
        for i, pred in enumerate(self.discrete_predictors):
            stacked_codes = self.one_hot_code(data[pred].values,i)
            #print pred,stacked_codes.shape
            coded_arr = np.vstack((coded_arr,stacked_codes[1:,:]))#Remove the first code to prevent issues with dummy variables

        return coded_arr[1:,:].T#Strip out the initial line of zeros

    #One-hot coding of discrete predictors:
    def one_hot_code(self,values,prednum):
        if self.discrete_predictor_mapping[prednum] == None:
            unique_values = np.unique(values)
            self.discrete_predictor_mapping[prednum] = dict(zip(unique_values,range(len(unique_values))))

        codes = [self.discrete_predictor_mapping[prednum][key] for key in values]
        code_arr = np.zeros((len(self.discrete_predictor_mapping[prednum].keys()),len(values)))
        code_arr[codes,range(len(values))] = 1.

        return code_arr

    #Make sure that the predictors the coder is designed for are actually present.
    def check_predictors(self,data):
        datacols = data.columns.values
        if self.continuous_predictors != None:
            if np.sum(np.in1d(self.continuous_predictors,datacols)) < len(self.continuous_predictors):
                raise KeyError("Some continuous predictors are missing from your data.")
        if self.discrete_predictors != None:
            if np.sum(np.in1d(self.discrete_predictors,datacols)) < len(self.discrete_predictors):
                raise KeyError("Some discrete predictors are missing from your data.")
        
    
if __name__ == "__main__":
    if len(sys.argv) != 6:
        sys.exit("Syntax: [minimum number of flights from a given airport] [number of rows to query at a time] [randomize flights yes/no] [CSV list of delay time bin edges (e.g. 15,45)] [prep/numiters]")

    output_dict = {}
    target_col = 'target'
    target_coded_col = 'target_coded'
    id_col = 'fid'
    
    min_flights = int(sys.argv[1])
    query_chunksize = int(sys.argv[2])
    randomize_flights = sys.argv[3]
    delay_time_bins = np.array(sys.argv[4].split(','),dtype=np.int)
    prepbool = False
    numiters = 0
    if sys.argv[5].lower() == 'prep':
        prepbool = True
    else:
        numiters = int(sys.argv[5])+1
    target_name = 'arrdelay'
    cancelled_name = 'cancelled'
    diverted_name = 'diverted'
    flightfile = 'fids_to_code.txt'
    tc = timecode(delay_time_bins)
    output_dict['target_coder']=tc
    
    table = 'flightdelays'
    #table = 'flightdelays_jun_afternoon'#For testing
    
    #Connect to the db:
    con = ''
    try:
        con = mdb.connect(host=creds.host,user=creds.user,db=creds.database,passwd=creds.password,local_infile=1)
        cur = con.cursor()

        #Get the airports that have had more than min_flights departures:
        start = time.time()
        cur.execute('select origin from {1:s} group by origin having count(origin) > {0:d} order by count(origin);'.format(min_flights,table))
        bestairports = np.array(cur.fetchall()).reshape(-1)
        bestairports_str = '"'+'","'.join(bestairports)+'"'
        print "Figured out which airports are good in {0:.2f}s".format(time.time()-start)

        if prepbool:
            cur.execute('drop table if exists used_airports')
            cur.execute('create table used_airports select * from airports where origin in ({bestairports})'.format(bestairports=bestairports_str))

        #Getting all the unique airlines:
        start = time.time()
        cur.execute('select uniquecarrier from {0:s} group by uniquecarrier'.format(table))
        goodairlines = np.array(cur.fetchall()).reshape(-1)
        goodairlines_str = '"'+'","'.join(goodairlines)+'"'
        print "Got all unique airlines in {0:.2f}s".format(time.time()-start)

        if prepbool:
            cur.execute('drop table if exists used_airlines')
            cur.execute('create table used_airlines select * from airlinenames where uniquecarrier in ({goodairlines})'.format(goodairlines=goodairlines_str))
        
        conditional_str = '{diverted} < 1e-4 and origin in ({bestairports}) and dest in ({bestairports}) and uniquecarrier in ({goodairlines})'.format(diverted=diverted_name,bestairports=bestairports_str,goodairlines=goodairlines_str)

        #print conditional_str

        #Getting all the months in the table:
        #cur.execute('select month(flightdate) month from {0:s} group by month'.format(table))
        #goodmonths = np.array(cur.fetchall(),dtype=np.int).reshape(-1)
        goodmonths = np.arange(12)+1#Assuming all the months are present:
        
        #Getting all the days of the week in the table:
        #cur.execute('select dayofweek(flightdate) dayofweek from {0:s} group by dayofweek'.format(table))
        #gooddays = np.array(cur.fetchall(),dtype=np.int).reshape(-1)
        gooddays = np.arange(1,8)#Assuming all the days of the week are present

        #Getting all the hours in the table:
        #cur.execute('select round((crsdeptime+20)/100.)%24 dep_round from {0:s} group by dep_round'.format(table))#This is nice because it will round to the closest hour, all within the query.
        #goodhours = np.array(cur.fetchall(),dtype=np.int).reshape(-1)
        goodhours = np.arange(0,24)#Assuming all the hours are present
        
        #Get the ids of all the flights meeting that criteria:
        start = time.time()
        if prepbool:
            cur.execute("select fid from {1:s} where {0:s}".format(conditional_str,table))
            good_fids = np.array(cur.fetchall(),dtype=np.int).reshape(-1)
            print "Got good flight ids in {0:.2f}s".format(time.time()-start)

            #If necessary, randomize the db order:
            if randomize_flights.lower() == 'yes':
                start = time.time()
                np.random.shuffle(good_fids)
                print "Shuffled flight ids in {0:.2f}s".format(time.time()-start)
            np.savetxt(flightfile,good_fids,fmt="%d")
        else:
            good_fids = np.loadtxt(flightfile,dtype=np.int)
            print "Loaded good flight ids in {0:.2f}s".format(time.time()-start)
            if len(good_fids) == 0:
                print "All fids have already been loaded"
        
            
        #Figure out the coding schema, create the new database. Here we only have discrete predictors, this would need minor modifications/additions if there were also continuous variables:
        discrete_predictors = ['origin','dest','uniquecarrier','dayofweek','monthnum','hour']
        discrete_predictors_addedsql = ['','','','dayofweek(flightdate) ','month(flightdate) ','round((crsdeptime+20)/100.)%24 ']
        unique_discrete_predictors = [bestairports,bestairports,goodairlines,gooddays,goodmonths,goodhours]
        pc = predictorcode(discrete_predictors,unique_discrete_predictors,None)
        
        if prepbool:
            cur.execute('drop table if exists coded_flightdelays')
        table_fields_str = 'CREATE TABLE coded_flightdelays({0:s} INT PRIMARY KEY AUTO_INCREMENT, {1:s} INT NOT NULL DEFAULT 1440, {2:s} TINYINT NOT NULL DEFAULT -1'.format(id_col,target_col,target_coded_col)
        table_fields_list = []
        for i,predictor in enumerate(unique_discrete_predictors):
            if len(predictor) > 0:
                table_fields_list += ['{0:s}_{1:d}'.format(discrete_predictors[i],j) for j in range(len(predictor)-1)]#-1 is to prevent dummy variable issues
                table_fields_str = table_fields_str + ', ' + ','.join([' {0:s}_{1:d} TINYINT NOT NULL DEFAULT -1'.format(discrete_predictors[i],j) for j in range(len(predictor)-1)])#-1 is to prevent dummy variable issues
        table_fields_str = table_fields_str + ')'
        if prepbool:
            cur.execute(table_fields_str)
        
        output_dict['discrete_predictors'] = discrete_predictors
        output_dict['discrete_predictors_addedsql'] = discrete_predictors_addedsql
        output_dict['predictor_coder']=pc
        output_dict['target_col'] = target_col
        output_dict['target_coded_col'] = target_coded_col
        output_dict['id_col'] = id_col
        output_dict['predictor_col_list'] = table_fields_list
        
        pkl_file = open('code_predictors.pkl','wb')
        pickle.dump(output_dict,pkl_file)
        pkl_file.close()

        if prepbool == False and len(good_fids) > 0:
            #Now, iterate through the database, querying on the shuffled fids, coding the data up, and then inserting it:
            query_syntax_prefix = "select {0:s},{1:s},".format(target_name,cancelled_name) + ','.join([discrete_predictors_addedsql[i]+discrete_predictors[i] for i in range(len(discrete_predictors))])+ " from {0:s}".format(table)
            #print query_syntax_prefix
            chunk_idxes = np.arange(0,len(good_fids),query_chunksize)
            #print len(good_fids),query_chunksize
            if chunk_idxes[-1] < len(good_fids):
                chunk_idxes = np.append(chunk_idxes,len(good_fids))#Don't need -1 here because numpy slicing will take care of it.

            start = time.time()
            if numiters > len(chunk_idxes):
                numiters = len(chunk_idxes)
            for i in range(1,numiters):
                curr_fids = good_fids[chunk_idxes[i-1]:chunk_idxes[i]]
                fid_string = ','.join(curr_fids.astype(np.str))
                query_syntax = query_syntax_prefix + ' where fid in ({0:s})'.format(fid_string)
                curr_df = pd.io.sql.read_sql(query_syntax,con)
                actual_targets = curr_df[target_name]
                actual_targets[curr_df[cancelled_name] > 1.e-4] = 1440

                target_coded = tc.encode(curr_df[target_name].values,curr_df[cancelled_name].values)
                # for j,code in enumerate(target_coded):
                #     print j,code,curr_df[target_name].values[j],curr_df[cancelled_name].values[j]

                curr_coded_data = pc.code_data(curr_df.drop([target_name,cancelled_name],axis=1))
                curr_df = None
                curr_coded_df = pd.DataFrame(curr_coded_data,columns=table_fields_list)
                curr_coded_df['target_coded'] = target_coded
                curr_coded_df['target'] = actual_targets
                #print curr_coded_df.values.nbytes/1024.**3
                curr_coded_df.to_sql('coded_flightdelays',con,flavor='mysql',if_exists='append')
                print "Iteration {0:d} of {1:d}: {2:.2f} seconds elapsed, {3:d} entries loaded".format(i,numiters-1,time.time()-start,len(curr_fids))
                #sys.exit(1)
            if numiters == len(chunk_idxes):
                print "Finished all flights!"
            
            np.savetxt(flightfile,good_fids[chunk_idxes[numiters-1]:],fmt='%d')
            
           
    except mdb.Error, e:
        print "Error %d: %s" % (e.args[0],e.args[1])
        sys.exit(1)
    finally:
        if con:
            con.close()
        
