import sys
import os
import urllib2
from bs4 import BeautifulSoup
import pickle 

data_path = '../gdelt_files/'

urlstem = 'http://data.gdeltproject.org/events/'
index = 'index.html'

raw_page = urllib2.urlopen(urlstem+index).read()

soup = BeautifulSoup(raw_page)

divs = soup.find_all('a')

gdelt_suc_file = 'gdelt_success_files.pickle'

try:
    infile = open(gdelt_suc_file)
    complete_files = pickle.load(infile)
    infile.close()
except IOError:
    complete_files = []


print complete_files


update_complete = False
for a in divs:
    filename=a.text
    href = a.attrs['href']
    
    try:
        year = int(filename.split('.zip')[0])
    except:
        continue
    
    print year
    if year not in complete_files:
        os.system('wget -O ../data/gdelt_files/%s %s' %(filename,urlstem+href))
        complete_files.append(year)
        update_complete = True
        
if update_complete:
    outfile = open(gdelt_suc_file, 'w')
    pickle.dump(complete_files, outfile)
    outfile.close()





