import numpy as np
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.ensemble import RandomForestRegressor

import matplotlib.pyplot as plt

class PDFRandomForestRegressor(BaseEstimator, RegressorMixin):
    """A normal random forest, except that it stores the final leaf positions and delay times for each row of the training set. It will also have a specialized scoring method."""
    def __init__(self,delaymin,delaymax,**kwargs):
        self.rforest = RandomForestRegressor(**kwargs)
        #self.delay_range = np.arange(delaymin,delaymax+1)
        self.delay_min = delaymin
        self.delay_max = delaymax
        #For each random forest, a dictionary mapping node id numbers to numpy arrays is also stored. These numpy arrays contain a histogram of the number of training models which fell into that node and their delay times.
        self.node_delay_pdfs = [{}]*self.rforest.n_estimators
        #print len(self.node_delay_pdfs)
        #self.node_delay_pdfs = np.zeros((self.rforest.n_estimators,self.delay_max-self.delay_min),dtype = np.int32)

    def fit(self, X,y):
        y_fit = self.restrict_range(y)
        self.rforest.fit(X,y_fit)

        #Map the y values onto indices for the arrays:
        y_indices = self.map_delay_vals(y_fit)

        #Get the node ids for the training set:
        nodes = self.apply(X)
        #print y_indices.shape,nodes.shape

        # sorted_node_indices = np.argsort(nodes,axis=0)
        # print sorted_node_indices.shape
        # sorted_nodes = np.zeros(nodes.shape)
        # for i in range(nodes.shape[1]):
        #     sorted_nodes[:,i] = nodes[sorted_node_indices[:,i],i]

        #For each tree, make a 2D array containing the full range of integer target values along one axis (first axis), and the unique nodes along the other. Now, when the regression predicts a set of nodes for a given set of inputs, the full delay time distribution can be extracted by taking a slice along the unique node axis
        for i in range(nodes.shape[1]):
            unique_nodes,idxes = np.unique(nodes[:,i],return_inverse=True)
            unique_node_indices = np.arange(len(unique_nodes))
            node_dict = {unique_nodes[i]:unique_node_indices[i] for i in range(len(unique_node_indices))}
            node_indices = unique_node_indices[idxes]
            pdf_arr,xedges,yedges = np.histogram2d(y_indices,node_indices,bins=[np.arange(self.delay_max-self.delay_min+1),unique_node_indices])
            self.node_delay_pdfs[i] = {'node_dict':node_dict,'pdf_arr':pdf_arr}
            # if i == 0:
            #     print nodes[:,i]
            #     print unique_node_indices
            #     print y_indices
            #     print np.arange(self.delay_max-self.delay_min+1)
            #     print pdf_arr
            #     print node_dict
            #pdf_arr = np.zeros((len(unique_nodes),self.delay_max-self.delay_min+1),dtype=np.int32)
            #pdf_arr[node_indices,y_indices] += 1
            #if i == 0:
            #    print node_indices
            #    print y_indices
            #    print pdf_arr.shape
            # sorted_node_indices = np.argsort(nodes[:,i])
            # unique_nodes,idxes = np.unique(nodes[sorted_node_indices,i],return_index=True)
            # split_y_indices = np.split(y_indices[sorted_node_indices],idxes)[1:]
            # pdf_arr = np.zeros((len(unique_nodes),self.delay_max-self.delay_min),dtype=np.int32)
            # pdf_indices = np.array([(split_y_indices[j],j) for j in len(split_y_indices)])
            # pdf_ar
            # if i == 0:
            #     print split_y_indices

        
        return self

    def restrict_range(self,y):
        y_restrict = y.copy()
        y_restrict[y < self.delay_min] = self.delay_min
        y_restrict[y > self.delay_max] = self.delay_max
        return y_restrict
    
    def map_delay_vals(self,y):
        y_map = self.restrict_range(y)
        y_indices = y_map-self.delay_min
        return y_indices

    def predict(self,X):
        return self.rforest.predict(X)

    def apply(self,X):
        return self.rforest.apply(X)


if __name__ == "__main__":

    np.random.seed(4)
    
    # Create a random dataset
    rng = np.random.RandomState(1)
    X = np.sort(5 * rng.rand(80, 1), axis=0)
    y = 20*np.sin(X).ravel()
    print y.min(),y.max(),np.sin(X).min()
    y[::5] += 10 * (0.5 - rng.rand(len(y[::5])))
    y = y.astype(np.int)
    print y.min(),y.max()

    clf = PDFRandomForestRegressor(-20,20,n_estimators=3,max_depth=4)
    clf.fit(X,y)
    x_pred = np.linspace(X.min(),X.max(),100).reshape(100,1)
    y_pred = clf.predict(x_pred)

    ax = plt.figure().add_subplot(111)
    ax.plot(X.ravel(),y,ls='.',marker='o',ms=2,mec='black',mfc='black',alpha=0.5)
    ax.plot(x_pred,y_pred,ls='-',color='green',lw=2,alpha=0.5)
    ax.figure.savefig('train_streaming_rforest.jpg')
