import numpy as np
import MySQLdb as mdb
import pandas as pd

import load_credentials_nogit as creds
#This file contains useful functions for doing querying, encoding, and modeling of my flight data.

#Get selected columns and put them into a Pandas Dataframe:
def query_into_pd(con,table,columnlist,subset=None):
    if columnlist:
        syntax = "Select {table}.{cols} from {table}".format(table=table,cols=', {table}.'.format(table=table).join(columnlist))
        df = pd.io.sql.frame_query(syntax,con)
        try:
            if int(subset) > 0:
                df = df.ix[np.random.random_integers(0,len(df),subset)]
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
