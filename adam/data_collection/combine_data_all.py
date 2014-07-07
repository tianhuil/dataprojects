##preprocess and save all data in a nice format.
import pandas as pd
import csv
import time
from numpy import *

start_time = time.time()

df1 = pd.read_csv('model_data/lf_hist.csv')
df2 = pd.read_csv('model_data/energy_RT.csv')
df3 = pd.read_csv('model_data/energy_DA.csv')
df4 = pd.read_csv('model_data/ml_RT.csv')
df5 = pd.read_csv('model_data/ml_DA.csv')
df6 = pd.read_csv('model_data/cong_RT.csv')
df7 = pd.read_csv('model_data/cong_DA.csv')
df8 = pd.read_csv('model_data/load_hist.csv')
df8['HOUR'] = df8['HOUR']/100
df9 = pd.read_csv('model_data/opres_hist.csv')

#LOAD FORECAST FORMAT
b= (df1.values[:][:,1].astype(int)-1).astype(str) #HE indexing
t = pd.to_datetime( df1['day'].values  +' ' +b + ':00')
df1.index = t
df1 = df1.iloc[:,2:]

def price_formatter( df ):
    y = array(df['DATE'].values).astype(str)
    y = array( y,dtype = object)
    b= (df.values[:][:,1].astype(int)).astype(str) #HE indexing
    t = pd.to_datetime( y +' ' + b + ':00')
    df.index = t
    df = df.iloc[:,2:]
    return df
    
df2 = price_formatter(df2)
df3 = price_formatter(df3)
df4 = price_formatter(df4)
df5 = price_formatter(df5)
df6 = price_formatter(df6)
df7 = price_formatter(df7)
df9 = price_formatter(df9)

#load FORMAT (COMPLETE)
b = (df8.values[:][:,1].astype(int)-1).astype(str) #HE indexing
t = pd.to_datetime( df8['DAY'].values  +' ' + b + ':00')
df8.index = t
df8 = df8.iloc[:,2:]

#merge everything into a single data frame where all data is present
df1 = pd.merge(df1, df2, left_index=True, right_index=True, how='inner')
df1 = pd.merge(df1, df3, left_index=True, right_index=True, how='inner')
df1 = pd.merge(df1, df4, left_index=True, right_index=True, how='inner')
df1 = pd.merge(df1, df5, left_index=True, right_index=True, how='inner')
df1 = pd.merge(df1, df6, left_index=True, right_index=True, how='inner')
df1 = pd.merge(df1, df7, left_index=True, right_index=True, how='inner')
df1 = pd.merge(df1, df8, left_index=True, right_index=True, how='inner')
df1 = pd.merge(df1, df9, left_index=True, right_index=True, how='inner')

pd.DataFrame.to_csv( df1, 'processed_Df.csv' )
print 'done!'

end_time = time.time()
print("Elapsed time was %g seconds" % (end_time - start_time))