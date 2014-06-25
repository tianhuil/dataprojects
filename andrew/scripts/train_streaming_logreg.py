import numpy as np
import pandas as pd
import cPickle as pickle
import MySQLdb as mdb
import sys
import time

import train_streaming_funcs as tsf
import flightfuncs as ff
from code_predictors import timecode,predictorcode
import load_credentials_nogit as creds

from sklearn.linear_model import SGDClassifier


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit("Syntax: [Table info pickle file] [Number of rows per iteration] [Fraction of data set for validation]")
    #This should probably be an argument but it's not likely to change, so w/e:
    table = 'coded_flightdelays'
    
    #Compute all permutations of classifier options you want to vary:
    option_dict = {'loss':np.array(['log']),'penalty':np.array(['l2']),'alpha':np.array([1.e-7,1.e-4,1e-2]),'n_iter':np.array([20,80]),'learning_rate':np.array(['constant']),'eta0':np.array([1e-2,1e-1,1.])}
    combined_args_df = tsf.combine_args(**option_dict)
    #print combined_args_df
    #print combined_args_df.dtypes
    #sys.exit(1)

    #Initialize the SGD models:
    sgd_models = []
    for i in range(combined_args_df.shape[0]):
        sgd_models.append(SGDClassifier(**(combined_args_df.irow(i).to_dict())))

    #Load up dictionary of predictors:
    info_dict = {}#Temporary due to broken pickling in code_predictors
    info_dict['target_coded_col'] = 'target_coded'
    info_dict['predictor_col_list'] = ['hour_{0:d}'.format(i) for i in range(23)]
    info_dict['predictor_col_list'].extend(['origin_{0:d}'.format(i) for i in range(103)])
    info_dict['predictor_col_list'].extend(['dest_{0:d}'.format(i) for i in range(103)])
    info_dict['predictor_col_list'].extend(['uniquecarrier_{0:d}'.format(i) for i in range(23)])
    info_dict['predictor_col_list'].extend(['dayofweek_{0:d}'.format(i) for i in range(6)])
    info_dict['predictor_col_list'].extend(['monthnum_{0:d}'.format(i) for i in range(11)])
    info_dict['id_col'] = 'fid'
    info_pkl = open(sys.argv[1],'rb')
    #info_dict = pickle.load(info_pkl)
    info_pkl.close()
    #The other command line arguments
    numrows = int(sys.argv[2])
    valfrac = float(sys.argv[3])

    #Connect to the db:
    con = ''
    try:
        con = mdb.connect(host=creds.host,user=creds.user,db=creds.database,passwd=creds.password,local_infile=1)
        cur = con.cursor()
        
        #Since in this database the primary key will be sequential, it's very fast to get the range I need to loop through:
        minid,maxid = tsf.get_col_range(cur,table,info_dict['id_col'])
        #Since the database has been shuffled already, I can just leave out the last N rows as my validation set.
        train_maxid = int((maxid-minid)*(1.-valfrac))
        train_minid = minid
        val_minid = train_maxid + 1
        val_maxid = maxid

        #For testing purposes:
        train_maxid = train_minid + 5*numrows
        val_maxid = val_minid + 5*numrows
        
        #Split up training set ids:
        id_chunks = np.arange(train_minid,train_maxid+1,numrows)
        if id_chunks[-1] < train_maxid:
            id_chunks = np.append(id_chunks,train_maxid)

        #Get all unique values of the predictor in the table:
        #unique_targets = (tsf.get_distinct(cur,table,info_dict['target_coded_col'])).sort()
        unique_targets = np.array([0.,1.,2.,3.,4.,5.])#For testing
            
        #prep the queries (as much as possible):
        query_prefix = '''SELECT {0:s},{1:s} from {2:s}'''.format(",".join(info_dict['predictor_col_list']),info_dict['target_coded_col'],table)
        #print query_prefix

        #Iterate through the chunks:
        start = time.time()
        for i in range(1,len(id_chunks)):
            query_suffix = ' WHERE {0:s} >= {1:d} AND {0:s} < {2:d}'.format(info_dict['id_col'],id_chunks[i-1],id_chunks[i])
            #print query_prefix + query_suffix
            full_df = pd.io.sql.read_sql(query_prefix+query_suffix,con)
            target_arr = full_df[info_dict['target_coded_col']].values.astype(np.float)
            predictor_arr = full_df.drop(info_dict['target_coded_col'],axis=1).values.astype(np.float)
            del full_df
            
            for j,model in enumerate(sgd_models):
                model.partial_fit(predictor_arr,target_arr,classes=unique_targets)
                #print "Model {0:d}: {1:.2f}s elapsed".format(j,time.time()-start)
            print "Training iteration {0:d} of {1:d} finished; total elapsed time = {2:.2f}s".format(i,len(id_chunks)-1,time.time()-start)

        #Validate the models on the OoS data:
        score_arr = np.zeros(len(sgd_models),dtype=np.float)
        
        #Split up validation set ids:
        id_chunks = np.arange(val_minid,val_maxid+1,numrows)
        if id_chunks[-1] < val_maxid:
            id_chunks = np.append(id_chunks,val_maxid)
            
        #Iterate through the chunks:
        start = time.time()
        for i in range(1,len(id_chunks)):
            query_suffix = ' WHERE {0:s} >= {1:d} AND {0:s} < {2:d}'.format(info_dict['id_col'],id_chunks[i-1],id_chunks[i])
            full_df = pd.io.sql.read_sql(query_prefix+query_suffix,con)
            target_arr = full_df[info_dict['target_coded_col']].values.astype(np.float)
            predictor_arr = full_df.drop(info_dict['target_coded_col'],axis=1).values.astype(np.float)
            del full_df
            
            for j,model in enumerate(sgd_models):
                #probs = model.predict_proba(predictor_arr)
                #Now that I have the probabilities, I can generate a score:
                score_arr[j] += ff.pdf_scoring(model,predictor_arr,target_arr)
                # if j == 0:
                #     print "  ",probs[:10,:]
                #     print "  ",target_arr[:10]
            print "Validation iteration {0:d} of {1:d} finished; total elapsed time = {2:.2f}s".format(i,len(id_chunks)-1,time.time()-start)
        #Normalize the scoring array for easier display:
        score_arr = score_arr/float(val_maxid-val_minid)
        combined_args_df['score'] = score_arr

        print combined_args_df
    
    except mdb.Error, e:
        print "Error %d: %s" % (e.args[0],e.args[1])
        sys.exit(1)
    finally:
        if con:
            con.close()
