import pandas as pd
import Quandl
import pylab as pl
import sys
import datetime as dt
import numpy as np

sys.path.append('../')
import settings 

def todate(date):
    date = np.array([int(a) for a in date.split('-')],dtype='int')
    return date 

def main():
    for stock in settings.to_use:
        mydata = Quandl.get(settings.indicators[stock], 
                            trim_start=settings.start_date,
                            trim_end=settings.end_date,
                            authtoken=settings.authtoken, returns="numpy")

        outfile = open('%s/data/quandl/%s.csv' %(settings.project_path,stock), 'w')
        outfile.write('# YYYYMMDD, open, high,low, last, change, settle, volume, open interest\n') 
        for row in mydata:
            row[0] = row[0].replace('-','')
            outstr = str(row)
            print outstr
            for bad,good in [('(',''),(')',''),("'",''),('-',','),
                             ('False','NULL')]:
                outstr = outstr.replace(bad,good)
            outfile.write(outstr+'\n')
        outfile.close()

if __name__ == "__main__":
    main()
