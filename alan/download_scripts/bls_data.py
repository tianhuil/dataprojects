import requests
import json
import prettytable
import pandas as pd
import Quandl
import  numpy as np
import sys

sys.path.append('../')
from settings import *


def is_leapyear(year):
    leap = np.logical_and(year%4==0,np.logical_or(year%100 >0,year%400==0))
    return int(leap)

months = [np.array([0,31,28,31,30,31,30,31,31,30,31,30,31], dtype=int),
          np.array([0,31,29,31,30,31,30,31,31,30,31,30,31], dtype=int)]

print months
print len(months)

quandel_start = '1999-01-01'
quandel_end = '2010-12-31'

step = 4 #years
start = 2005
end = 2014


def main():
    outfile = open('../data/quandl/cpi.csv' , 'w')
    outfile.write('# year, month, day, value\n') 

    for st_yr in range(start,end,step):
        headers = {'Content-type': 'application/json'} 
        data = json.dumps({"seriesid": ['CUUR0000SA0L1E'],"startyear":str(st_yr), "endyear":str(end)}) 
        p = requests.post('http://api.bls.gov/publicAPI/v1/timeseries/data/', data=data, headers=headers) 
        json_data = json.loads(p.text) 
        print p.text
        for series in json_data['Results']['series']:
            x=prettytable.PrettyTable(["series id","year","period","value","footnotes"])
            seriesId = series['seriesID']
            for item in series['data']:
                print item
                year = int(item['year'])
                period = int(item['period'][1:])
                value = float(item['value'])
                footnotes=""
                for footnote in item['footnotes']:
                    if footnote:
                        footnotes = footnotes + footnote['text'] + ','
                if period <= 12:
                    print period, year, is_leapyear(year)
                    day = months[is_leapyear(year)][period]
                    outfile.write('%d,%d,%d,%f\n' %(year, period, day,value))


    mydata = Quandl.get('WORLDBANK/USA_GFDD_OE_02', trim_start=quandel_start,
                        trim_end=quandel_end, returns="numpy",
                        authtoken="ZwZp5EomA34QgSDRezss")
                              
    for row in mydata:
        outstr = str(row)
        for bad,good in [('(',''),(')',''),("'",''),('-',','),
                         ('False','-999')]:
            outstr = outstr.replace(bad,good)

        outfile.write(outstr+'\n')
    outfile.close()

if __name__=="__main__":
    main()


    



