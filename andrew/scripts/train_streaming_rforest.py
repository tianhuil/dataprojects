import numpy as np
import sys
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.ensemble import RandomForestRegressor
from sklearn.cross_validation import train_test_split

import matplotlib.pyplot as plt

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
    


if __name__ == "__main__":

    np.random.seed(4)
    
    # Create a random dataset
    X = 5*np.random.rand(1000,1)
    y = 30*np.sin(X).ravel()
    y[::2] += 30*(0.5-np.random.rand(len(y[::2])))
    y = y.astype(np.int)
    X_train,X_test,y_train,y_test = train_test_split(X,y,test_size=0.30)
    #train_indices = np.argsort(X_train,axis=0)
    # rng = np.random.RandomState(1)
    # X = np.sort(5 * rng.rand(1000, 1), axis=0)
    # y = 50*np.sin(X).ravel()
    # y[::2] += 50 * (0.5 - rng.rand(len(y[::2])))

    for depth in range(2,40):
        clf = PDFRandomForestRegressor(-50,50,n_estimators=10,max_depth=depth)
        clf.fit(X,y,compute_pdf=True)
        x_pred = np.linspace(X_train.min(),X_train.max(),17)
        y_pred = clf.predict(x_pred[:,np.newaxis])
        y_pred_25_75 = clf.predict_percentiles(x_pred[:,np.newaxis],[25.,50.,75.])
        y_score = clf.score_percentiles(X_test,y_test)
        print depth,
        print "Regular Score=",clf.score(X_test,y_test),
        print "Percentile Score=",y_score

    #print help(clf.rforest.score)

    ax = plt.figure().add_subplot(111)
    ax.fill_between(x_pred,y_pred_25_75[:,0],y_pred_25_75[:,2],color='gray',alpha=0.25)
    ax.plot(X_train.ravel(),y_train,ls='.',marker='o',ms=2,mec='black',mfc='black',alpha=0.5)
    ax.plot(x_pred,y_pred_25_75[:,1],ls='-',color='green',lw=2,alpha=0.5)
    ax.plot(x_pred,y_pred,ls='-',color='orange',lw=2,alpha=0.5)
    ax.figure.savefig('train_streaming_rforest.jpg')
