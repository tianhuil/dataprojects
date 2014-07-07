import numpy as np
import sys
sys.path.append('../')
import settings
import pandas as pd

datadir = settings.project_path+'data/trademap/'
countryfile  = 'Trade_Map_oil_balance.txt'

def top_list(filename, percent, year):
    infile = open(filename)
    header = infile.readline()
    allyears = np.array([int(a) for a in header.split(',')[1:]])
    colnum = np.where(np.abs(allyears - year)== np.min(np.abs(allyears - year)))[0][0]
    
    value = np.loadtxt(filename, usecols=[colnum], delimiter=',')
    nation = []
    for line in infile.readlines():
        nation.append()
        

    totals = np.cumsum(value)
    totals = totals/totals[-1]
    good_countries = np.where(totals <percent, True, False)
    good_countries = [ a[0]  for a in zip(nation,good_countries) if a[1]==True]
    return good_countries


import_df = pd.read_csv(datadir+countryfile, skiprows=1, delimiter = '\t') 

print import_df

print import_df.sort(column=import_df.columns[1])

print import_df.sort(column=import_df.columns[1],ascending=False)
