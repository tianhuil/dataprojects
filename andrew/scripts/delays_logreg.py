import sys
import numpy as np
import pandas as pd
import MySQLdb as mdb
import sklearn.feature_extraction
import sklearn.linear_model
import time

import flightfuncs as ff
import load_credentials_nogit as creds

#Train and fit a logarithmic regression classifier.
def train_log(tablename,subset=None,timesplit = [15,45],filename = None):
    #Connect to the database and download the data:
    con = mdb.connect(host=creds.host,user=creds.user,db=creds.database,passwd=creds.password,local_infile=1)
    data = ff.query_into_pd(con,tablename,['origin','dest','uniquecarrier','arrdelay','cancelled','diverted'],subset=subset)
    print "Finished querying data ({0:.2f}s)".format(time.time()-start)
    
    #Select only flights that weren't diverted:
    diverted_bool = (data.diverted > 1.e-5)
    data = data[(diverted_bool == False)]

    #Code up the delay times:
    tc = ff.time_coder(timesplit)
    coded_delays = tc.time_encode(data.arrdelay.values,data.cancelled.values)
    print "Finished coding the targets ({0:.2f}s)".format(time.time()-start)

    #Code up the predictors. All of the ones I'm currently dealing with are categorical and strings, so I think Dictvectorizer will just work
    test = data[['origin','dest','uniquecarrier']]
    vectorizer = sklearn.feature_extraction.DictVectorizer()
    pred_vec,vectorizer = ff.vectorize_data(data[['origin','dest','uniquecarrier']],vectorizer,fit_transform=True)
    print "Finished vectorizing the predictor ({0:.2f}s)".format(time.time()-start)

    #Free up memory by chucking the data
    data = None

    #Train the logistic regression model:
    logreg = sklearn.linear_model.LogisticRegression(C=1.e5)
    logreg.fit(pred_vec,coded_delays)
    print "Finished training the model ({0:.2f}s)".format(time.time()-start)

    #This is just some testing stuff to make sure I can get out probabilities that make sense. It'll go away soon, when I fully separate out the training from the testing.
    sampledict = {'origin': pd.Series(['MSN','DEN','LAX']),
                  'dest': pd.Series(['ORD','JFK','ORD']),
                  'uniquecarrier': pd.Series(['UA','UA','UA']),
                  'label': pd.Series(['United - MSN->ORD','United - DEN->JFK','United - LAX->ORD'])
                  }
    sampledf = pd.DataFrame(sampledict)
    sample_vec,crap = ff.vectorize_data(sampledf[['origin','dest','uniquecarrier']],vectorizer,fit_transform=False)
    sample_probabilities = logreg.predict_proba(sample_vec)
    print sample_probabilities
    
    
if __name__ == "__main__":
    #np.random.seed(1)
    if len(sys.argv) != 3:
        sys.exit("Syntax: [Shard name] [subset (integer or 'none')]")
    tablename = sys.argv[1]
    subset = None
    try:
        subset = int(sys.argv[2])
    except ValueError:
        subset = None
    train_log(tablename,subset=subset)
