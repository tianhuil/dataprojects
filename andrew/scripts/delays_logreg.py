import numpy as np
import pandas as pd
import MySQLdb as mdb

import flightfuncs as ff
import load_credentials_nogit as creds

#Train and fit a logarithmic regression classifier.
def train_tree(tablename,subset=None,timesplit = [15,45],filename = None):
    #Connect to the database and download the data:
    con = mdb.connect(host=creds.host,user=creds.user,db=creds.database,passwd=creds.password,local_infile=1)
    data = ff.query_into_pd(con,tablename,['origin','dest','uniquecarrier','arrdelay','cancelled','diverted'],subset=subset)

    #Select only data that wasn't diverted:
    diverted_bool = (data.diverted > 1.e-5)
    print data.shape
    data = data[(diverted_bool == False)]
    print data.shape
    
if __name__ == "__main__":
    train_tree('flightdelays_mar_early',subset=10000)
