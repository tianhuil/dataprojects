import numpy as np
import pandas as pd
import cPickle as pickle
import MySQLdb as mdb
import sys
import glob
import time
from sklearn.externals import joblib

import train_streaming_funcs as tsf
from code_predictors import timecode,predictorcode
import load_credentials_nogit as creds
from train_streaming_rforest import PDFRandomForestRegressor


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit("Syntax: [Table info pickle file] [Training pickle file ][Number of rows per iteration]")

    info_pickle_file = sys.argv[1]
    training_pickle_file = sys.argv[2]
    numrows = int(sys.argv[3])

    info_pkl = open(info_pickle_file,'rb')
    info_dict = pickle.load(info_pkl)
    info_pkl.close()
    training_pkl = open(training_pickle_file,'rb')
    training_dict = pickle.load(training_pkl)
    training_pkl.close()

    #1: Get all possible combinations of parameter pickle files:
    model_pkl_filenames = np.array(glob.glob('{0:s}rforest__*pkl'.format(training_dict['model_dir'])))
    model_pkl_fileprefixes = np.array(['__'.join(fname.split('__')[:-1]) for fname in model_pkl_filenames])
    unique_models,return_indices = np.unique(model_pkl_fileprefixes,return_inverse=True)
    model_filename_lists = []
    model_lists = []
    start = time.time()
    for i in range(len(unique_models)):
        model_filename_lists.append(model_pkl_filenames[(model_pkl_fileprefixes == unique_models[i])])
        temp_model_list = []
        for model_filename in model_filename_lists[-1]:
            #f = open(model_filename,'rb')
            temp_model_list.append(joblib.load(model_filename))
            #f.close()
        model_lists.append(temp_model_list)
    print "Took {0:.2f}s to load models in".format(time.time()-start)
        
    #2: Compute how many iterations will be needed to get through the validation set:
    iterarr = np.arange(training_dict['val_minid'],training_dict['val_maxid']+1,numrows)
    if iterarr[-1] != training_dict['val_maxid']:
        iterarr = np.append(iterarr,training_dict['val_maxid'])

    #4: Set up running counter of scores:
    cumscores = np.zeros(len(model_filename_lists))
    scorecounter = np.zeros(len(model_filename_lists),dtype=np.int)

    #5: Connect to the database:
    con = ''
    try:
        con = mdb.connect(host=creds.host,user=creds.user,db=creds.database,passwd=creds.password,local_infile=1)
        cur = con.cursor()
    
        #6: Iterate through the database, querying chunks and fitting them:
        select_clause = "select {0:s},{1:s} from {2:s}".format(','.join(info_dict['predictor_col_list']),info_dict['target_col'],training_dict['table'])
        iterstart = time.time()
        #for i in range(1,len(iterarr)):
        for i in range(1,5):
            #6a: Query the database:
            print "Iteration {0:d} of {1:d}:".format(i,len(iterarr)-1)
            where_clause = "where {0:s} > {1:d} and {0:s} <= {2:d}".format(info_dict['id_col'],iterarr[i-1],iterarr[i])
            full_query = select_clause + " " + where_clause
            querystart = time.time()
            full_df = pd.io.sql.read_sql(full_query,con)
            print "   Time to query db = {0:.2f}s".format(time.time()-querystart)
            #6b: Split the data into predictor and target:
            target_arr = full_df[info_dict['target_col']].values
            predictor_arr = full_df.drop(info_dict['target_col'],axis=1).values.astype(np.float32)
            del full_df

            #6c: Iterate over the unique model types:
            allmodelstart = time.time()
            for j,model_list in enumerate(model_lists):
                currmodelstart = time.time()
                #6c_a: Iterate through each model in that set:
                for k,currmodel in enumerate(model_list):
                    #6c_a_a: Load the model in:
                    #f = open(model_fname,'rb')
                    #currmodel = pickle.load(f)
                    #f.close()
                    #6c_a_b: Compute the score of the model:
                    score = currmodel.score(predictor_arr,target_arr)
                    #print "        ",k,predictor_arr.shape
                    cumscores[j] += score
                    scorecounter[j] += 1
                print "        Model iteration {0:d} of {1:d}: Time = {2:.2f}s".format(j+1,len(model_filename_lists),time.time()-currmodelstart)
            print "    Time to do all models = {0:.2f}s".format(time.time()-allmodelstart)
        print "Total iteration time: {0:.3f} hours".format((time.time()-iterstart)/3600.)
            
        
    except mdb.Error, e:
        print "Error %d: %s" % (e.args[0],e.args[1])
        sys.exit(1)
    finally:
        if con:
            con.close()

    # print model_filename_lists[0]
    # print model_filename_lists[1]
