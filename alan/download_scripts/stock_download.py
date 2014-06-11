import pandas as pd
import Quandl
import pylab as pl
import sys
import datetime as dt
import numpy as np

sys.path.append('../')
from settings import *

start_date = '2000-01-01'
end_date = '2010-12-31'
           
def todate(date):
    date = np.array([int(a) for a in date.split('-')],dtype='int')
    return date 


def main():

    for stock in to_use:
        mydata = Quandl.get(indicators[stock], trim_start=start_date,
                            trim_end=end_date,
                            authtoken="ZwZp5EomA34QgSDRezss", returns="numpy")

        outfile = open('../data/quandl/%s.csv' %stock, 'w')
        outfile.write('# year, month, day, open, high, low, settle, volume, open interest\n') 
        for row in mydata:
            outstr = str(row)
            for bad,good in [('(',''),(')',''),("'",''),('-',','),
                             ('False','-999')]:
                outstr = outstr.replace(bad,good)

            outfile.write(outstr+'\n')
        outfile.close()


if __name__ == "__main__":
    main()
