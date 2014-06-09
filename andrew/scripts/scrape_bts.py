import numpy as np
import csv
import urllib

years = np.arange(2003,2015)
months = np.arange(1,13)

for year in years:
    for month in months:
        url = "http://www.transtats.bts.gov/Download/On_Time_On_Time_Performance_{0:d}_{1:d}.zip".format(year,month)
        urllib.urlretrieve(url,"/Users/Rook/Incubator/flight_data/bts_ontime_data/bts_ontime_{0:d}_{1:d}.zip".format(year,month))
