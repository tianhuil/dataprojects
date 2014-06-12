import numpy as np
import MySQLdb as mdb
import pandas as pd

import load_credentials_nogit as creds
#This file contains useful classes and functions for doing querying, encoding, and modeling of my flight data.

class time_coder:
    def __init__(self,timebins):
        self.timebins = timebins
        self.bin_text_dict = {}
    def time_encode(self,times,cancellations):
        if self.timebins:
            coded_array = np.zeros(len(times),dtype=np.int)
            self.bin_text_dict[0] = '<{0:d}'.format(self.timebins[0])
            currcode = 1
            for i in range(1,len(self.timebins)):
                coded_array[(times >= self.timebins[i-1]) & (times < self.timebins[i])] = currcode
                self.bin_text_dict[currcode] = '{0:d}-{1:d}'.format(self.timebins[i-1],self.timebins[i])
                currcode += 1
            coded_array[(times >= self.timebins[-1])] = currcode
            self.bin_text_dict[currcode] = '>={0:d}'.format(self.timebins[-1])
            currcode += 1
            coded_array[(cancellations > 1.e-5)] = currcode
            self.bin_text_dict[currcode] = 'Cancelled'
            return coded_array.astype(np.str)
        else:
            raise ValueError("time_coder.timebins is empty!")

#Vectorize a set of predictors from a Pandas dataframe into a sparse matrix:
def vectorize_data(data,vectorizer,fit_transform = False):
    datadict = data.T.to_dict().values()
    pred_vec = None
    if fit_transform:
        pred_vec = vectorizer.fit_transform(datadict)
    else:
        pred_vec = vectorizer.transform(datadict)
    return pred_vec,vectorizer
        
#Get selected columns and put them into a Pandas Dataframe:
def query_into_pd(con,table,columnlist,subset=None):
    if columnlist:
        syntax = "Select {table}.{cols} from {table}".format(table=table,cols=', {table}.'.format(table=table).join(columnlist))
        df = pd.io.sql.frame_query(syntax,con)
        try:
            if int(subset) > 0:
                df = df.ix[np.random.choice(np.arange(len(df)),replace=False,size=subset)]
        except TypeError:
            pass
        return df
    else:
        raise IndexError("No columns to be selected!")
        

if __name__ == "__main__":
    #Testing the functions as I go:
    con = mdb.connect(host=creds.host,user=creds.user,db=creds.database,passwd=creds.password,local_infile=1)
    df = query_into_pd(con,'flightdelays_mar_early',['origin','dest','uniquecarrier','arrdelay','cancelled','diverted'],subset=None)
    print df.shape
