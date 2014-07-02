import numpy as np
import pandas as pd
import sys
import os
import time
import cPickle as pickle
import MySQLdb as mdb
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.ensemble import RandomForestRegressor
from sklearn.cross_validation import train_test_split
from sklearn.externals import joblib

import matplotlib.pyplot as plt
import train_streaming_funcs as tsf
from code_predictors import timecode,predictorcode
import load_credentials_nogit as creds

class PDFRandomForestRegressor(BaseEstimator, RegressorMixin):
    """A normal random forest, except that it stores the final leaf positions and delay times for each row of the training set. It will also have a specialized scoring method."""
    def __init__(self,delaymin,delaymax,**kwargs):
        self.rforest = RandomForestRegressor(**kwargs)
        self.delay_min = delaymin
        self.delay_max = delaymax
        self.delay_bin_indices = np.arange(self.delay_max-self.delay_min+1)
        self.delay_bin_values = np.arange(self.delay_min,self.delay_max+1)
        #For each random forest, a dictionary mapping node id numbers to numpy arrays is also stored. These numpy arrays contain a histogram of the number of training models which fell into that node and their delay times.
        self.node_delay_pdfs = [{}]*self.rforest.n_estimators

    def fit(self, X,y,compute_pdf = False):
        y_fit = self.restrict_range(y)
        self.rforest.fit(X,y_fit)

        if compute_pdf == True:
            #Get the node ids for the training set:
            self.set_node_pdfs(X,y_fit)
        
        return self

    def set_node_pdfs(self,X,y):
        y_fit = self.restrict_range(y)
        #Map the y values onto indices for the arrays:
        y_indices = self.map_y_vals(y_fit)
        nodes = self.apply(X)

        #For each tree, make a 2D array containing the full range of integer target values along one axis (first axis), and the unique nodes along the other. Now, when the regression predicts a set of nodes for a given set of inputs, the full delay time distribution can be extracted by taking a slice along the unique node axis
        for i in range(nodes.shape[1]):
            unique_nodes,idxes = np.unique(nodes[:,i],return_inverse=True)
            unique_node_indices = np.arange(len(unique_nodes)+1)
            node_dict = {unique_nodes[i]:unique_node_indices[i] for i in range(len(unique_node_indices)-1)}
            node_indices = unique_node_indices[idxes]
            pdf_arr,xedges,yedges = np.histogram2d(y_fit,node_indices,bins=[self.delay_bin_values,unique_node_indices])
            #print 'testing',np.sum(pdf_arr)
            self.node_delay_pdfs[i] = {'node_dict':node_dict,'pdf_arr':pdf_arr}

    def restrict_range(self,y):
        y_restrict = y.copy()
        y_restrict[y < self.delay_min] = self.delay_min
        y_restrict[y > self.delay_max-1] = self.delay_max-1
        return y_restrict
    
    def map_y_vals(self,y):
        y_map = self.restrict_range(y)
        y_indices = y_map-self.delay_min
        return y_indices

    def predict(self,X):
        return self.rforest.predict(X)

    #Instead of just the normal prediction, which I believe just gives the average value of everything in the leaf node, predict a set of quantiles:
    def predict_percentiles(self,X,percentiles):
        p_nodes = self.apply(X)
        pdf_arr = self.get_node_pdfs(p_nodes)
        #print np.sum(pdf_arr,axis=1)
        sys.exit
        cdf_arr = np.cumsum(pdf_arr,axis=1)
        cdf_arr_frac = (cdf_arr.T/cdf_arr[:,-1].astype(np.float)).T
        #print pdf_arr[0,:]
        #print cdf_arr_frac[0,:]
        #sys.exit(1)
        #print "test",cdf_arr_frac.shape,len(percentiles)
        percentile_yvals = np.zeros((cdf_arr_frac.shape[0],len(percentiles)),dtype=np.int)
        for i,ptile in enumerate(percentiles):
            temp_cdf_arr_frac = cdf_arr_frac.copy()#These steps ensure that the y value is taken as the first index where the cdf goes above the percentile
            temp_cdf_arr_frac[temp_cdf_arr_frac < ptile/100.] = 1000
            indices = np.argmin(temp_cdf_arr_frac-ptile/100.,axis=1)
            #indices = np.argmin(np.abs(cdf_arr_frac-ptile/100.),axis=1)
            #print indices[0]
            percentile_yvals[:,i] = self.delay_bin_values[indices]
            #print i,self.delay_bin_values[indices]

        #print pdf_arr[0,:]
        #print cdf_arr_frac[0,:]
        #print percentile_yvals[0,:],percentile_yvals.shape
        #sys.exit(1)
        return percentile_yvals

    def compute_percentiles(self,X,y):
        y_fit = self.restrict_range(y)
        y_indices = self.map_y_vals(y_fit).astype(np.int)
        p_nodes = self.apply(X)
        pdf_arr = self.get_node_pdfs(p_nodes)
        cdf_arr = np.cumsum(pdf_arr,axis=1)
        cdf_arr_frac = (cdf_arr.T/cdf_arr[:,-1].astype(np.float)).T
        #print cdf_arr_frac[0,:]
        #print self.delay_bin_values
        #print cdf_arr_frac.shape,y_fit.shape,y_fit[0]
        #print 'test',cdf_arr_frac.shape,y_fit.shape,y_indices.min(),y_indices.max(),self.delay_bin_values.shape
        #Now just need to compute the percentiles for all the y_indices
        cdf_at_y = cdf_arr_frac[np.arange(len(y_indices)),y_indices]
        #print "debug",cdf_at_y[0]
        return cdf_at_y
        # print cdf_at_y[:10],cdf_at_y.shape

    def get_node_pdfs(self,nodes):
        pdf_arr = np.zeros((nodes.shape[0],len(self.delay_bin_values)-1),dtype=np.int)
        #print nodes.shape,pdf_arr.shape
        for i,node_info in enumerate(self.node_delay_pdfs):
            #print i,node_info['node_dict']
            node_ids = [node_info['node_dict'][node] for node in nodes[:,i]]
            #print node_ids
            #print node_info['pdf_arr'].shape
            #print 'debug',node_info['pdf_arr'][:,node_ids[0]]
            temp_arr = np.array([node_info['pdf_arr'][:,node_id] for node_id in node_ids],dtype=pdf_arr.dtype)
            pdf_arr += temp_arr
            #print 'temp',temp_arr[0,:]
            #print ""
        return pdf_arr

    def apply(self,X):
        return self.rforest.apply(X)

    def score(self,X,y):
        return self.rforest.score(X,y)

    #Compute how good each predicted value is based on how far away it is from the median value in percentiles:
    def score_percentiles(self,X,y):
        #First, compute the medians:
        y_med = self.predict_percentiles(X,[50]).ravel()
        #print y_med.shape
        percentiles = self.compute_percentiles(X,y)
        med_percentiles = self.compute_percentiles(X,y_med)#Have to do this step to take into account the discrete nature of the y values.
        #print med_percentiles[:10],percentiles[:10]
        return 1.-np.sum((med_percentiles-percentiles)**2)/float(len(y))
    
def make_tree_filename(output_dir,min_delay,max_delay,argsdict):
    keys = sorted(argsdict.keys())
    fname = "{0:s}rforest__min_delay-{1:d}__max_delay-{2:d}__".format(output_dir,min_delay,max_delay)
    for key in keys:
        fname += "{0:s}-{1}__".format(key,argsdict[key])
    fname += "{0:.0f}.pkl".format(time.time())
    return fname

if __name__ == "__main__":

    #np.random.seed(4)

    if len(sys.argv) != 5:
        sys.exit("Syntax: [Table info pickle file] [Number of rows per iteration] [Number of iterations] [Fraction of data set for validation]")

    info_pickle_file = sys.argv[1]
    numrows = int(sys.argv[2])
    numiters = int(sys.argv[3])
    valfrac = float(sys.argv[4])
        
    #Some constants that likely will not change, but are all listed up here for easy dealing with if that's a bad assumption:
    table = 'coded_flightdelays'
    n_jobs = 2
    output_dir = "../rforest_models/"
    min_delay = -20#minutes
    max_delay = 150#minutes
    option_dict = {'n_estimators':np.array([10]),'max_features':np.array(["auto","sqrt"]),'max_depth':np.array([8,12,16])}
    #option_dict = {'n_estimators':np.array([10]),'max_features':np.array(["auto","sqrt"]),'max_depth':np.array([4,8])}
    info_pkl = open(info_pickle_file,'rb')
    info_dict = pickle.load(info_pkl)
    info_pkl.close()

    
    #1: Figure out how many different random forests will be run per iteration and what their hyperparameters will be (for cross validation later)
    combined_args_df = tsf.combine_args(**option_dict)
    #print combined_args_df

    #connect to the db:
    con = ''
    try:
        con = mdb.connect(host=creds.host,user=creds.user,db=creds.database,passwd=creds.password,local_infile=1)
        cur = con.cursor()
        #2: Determine the split between training and cross validation FIDs. Since the database has been pre-shuffled, this should be easy.
        minid,maxid = tsf.get_col_range(cur,table,info_dict['id_col'])
        id_range = maxid-minid
        train_minid = minid
        train_maxid = minid + np.round(id_range*(1.-valfrac)).astype(np.int)
        val_minid = train_maxid + 1
        val_maxid = maxid
        training_info = {}
        training_info['model_dir'] = output_dir
        training_info['table'] = table
        training_info['val_minid'] = val_minid
        training_info['val_maxid'] = val_maxid
        training_pkl = open('train_streaming_rforest.pkl','wb')
        pickle.dump(training_info,training_pkl)
        training_pkl.close()

        select_clause = "select {0:s},{1:s} from {2:s}".format(','.join(info_dict['predictor_col_list']),info_dict['target_col'],table)
        for count in range(numiters):
            start = time.time()
            #3: Query the database for a random sample from the training set, and fit it to all the random forests.
            rows_to_query = np.random.random_integers(train_minid,train_maxid,numrows)
            where_clause = "where {0:s} in ({1:s})".format(info_dict['id_col'],','.join(rows_to_query.astype(np.str)))
            full_query = select_clause + " " + where_clause
            query_construct_time = time.time()-start
            full_df = pd.io.sql.read_sql(full_query,con)
            query_execute_time = time.time()-(start+query_construct_time)

            target_arr = full_df[info_dict['target_col']].values
            predictor_arr = full_df.drop(info_dict['target_col'],axis=1).values.astype(np.float32)
            del full_df
            for i in range(combined_args_df.shape[0]):
                argsdict = combined_args_df.irow(i).to_dict()
                for key in argsdict.keys():
                    if type(argsdict[key]) == np.bool_:
                        argsdict[key] = np.asscalar(argsdict[key])
                clf = PDFRandomForestRegressor(min_delay,max_delay,n_jobs=n_jobs,**argsdict)
                clf.fit(predictor_arr,target_arr,compute_pdf=True)
                #4: Save each of the random forests as a pickle, with the pickle filename indicating the state of the hyperparameters
                tree_filename = make_tree_filename(output_dir,min_delay,max_delay,argsdict)
                #f = open(tree_filename,'wb')
                joblib.dump(clf,tree_filename)
                #pickle.dump(clf,f)
                #f.close()
            tree_train_time = time.time()-(start+query_execute_time)
                

            print "Iteration {0:d} of {1:d}: {2:.2f}s total ({3:.2f}s to build query, {4:.2f}s to execute query, {5:.2f}s to train {6:d} random forests)".format(count+1,numiters,time.time()-start,query_construct_time,query_execute_time,tree_train_time,combined_args_df.shape[0])
    
    except mdb.Error, e:
        print "Error %d: %s" % (e.args[0],e.args[1])
        sys.exit(1)
    finally:
        if con:
            con.close()

    
    # # Create a random dataset
    # X = 5*np.random.rand(1000,1)
    # y = 30*np.sin(X).ravel()
    # y[::2] += 30*(0.5-np.random.rand(len(y[::2])))
    # y = y.astype(np.int)
    # X_train,X_test,y_train,y_test = train_test_split(X,y,test_size=0.30)
    # #train_indices = np.argsort(X_train,axis=0)
    # # rng = np.random.RandomState(1)
    # # X = np.sort(5 * rng.rand(1000, 1), axis=0)
    # # y = 50*np.sin(X).ravel()
    # # y[::2] += 50 * (0.5 - rng.rand(len(y[::2])))

    # for depth in range(2,40):
    #     clf = PDFRandomForestRegressor(-50,50,n_estimators=10,max_depth=depth)
    #     clf.fit(X,y,compute_pdf=True)
    #     x_pred = np.linspace(X_train.min(),X_train.max(),17)
    #     y_pred = clf.predict(x_pred[:,np.newaxis])
    #     y_pred_25_75 = clf.predict_percentiles(x_pred[:,np.newaxis],[25.,50.,75.])
    #     y_score = clf.score_percentiles(X_test,y_test)
    #     print depth,
    #     print "Regular Score=",clf.score(X_test,y_test),
    #     print "Percentile Score=",y_score

    # #print help(clf.rforest.score)

    # ax = plt.figure().add_subplot(111)
    # ax.fill_between(x_pred,y_pred_25_75[:,0],y_pred_25_75[:,2],color='gray',alpha=0.25)
    # ax.plot(X_train.ravel(),y_train,ls='.',marker='o',ms=2,mec='black',mfc='black',alpha=0.5)
    # ax.plot(x_pred,y_pred_25_75[:,1],ls='-',color='green',lw=2,alpha=0.5)
    # ax.plot(x_pred,y_pred,ls='-',color='orange',lw=2,alpha=0.5)
    # ax.figure.savefig('train_streaming_rforest.jpg')
