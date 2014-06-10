import numpy as np
import csv
import urllib
import sys

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Syntax: [Directory tree to download data to (absolute or relative, go nuts)]")
    
    years = np.arange(2003,2015)
    months = np.arange(1,13)

    for year in years:
        for month in months:
            url = "http://www.transtats.bts.gov/Download/On_Time_On_Time_Performance_{0:d}_{1:d}.zip".format(year,month)
            urllib.urlretrieve(url,"{0:s}/bts_ontime_{1:d}_{2:d}.zip".format(sys.argv[1],year,month))
