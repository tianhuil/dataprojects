import numpy as np
import sys

sys.path.append('../')
import settings


datadir = '../data/'
countryfile  = 'countries_new.txt'

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

outfile = open(countryfile, 'w')

for stock in settings.to_use:
    for ending in ['Export.csv', 'Import.csv']:
        filename = datadir + stock+ending
        to_add = top_list(filename, 0.9, 2010)
        for a in to_add:
            outfile.write(a+'\n')

outfile.close()

