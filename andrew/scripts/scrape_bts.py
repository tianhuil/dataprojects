import numpy as np
import csv
import urllib
import sys

def download_bts(download_dir,years=np.arange(2003,2015),months=np.arange(1,13)):
    '''Downloads historical flight data from the BTS system. 
    arguments:
    download_dir -- where you want the files to get downloaded to
    
    keyword arguments:
    years -- the range of years to download (default: 2003-2014)
    months -- the range of months to download (default: 1-12)
    '''
    for year in years:
        for month in months:
            url = "http://www.transtats.bts.gov/Download/On_Time_On_Time_Performance_{0:d}_{1:d}.zip".format(year,month)
            urllib.urlretrieve(url,"{0:s}/bts_ontime_{1:d}_{2:d}.zip".format(download_dir,year,month))

    
if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Syntax: [Directory tree to download data to (absolute or relative, go nuts)]")
    

    download_bts(sys.argv[1])
