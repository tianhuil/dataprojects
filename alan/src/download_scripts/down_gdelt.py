import sys
import os
import urllib2
from bs4 import BeautifulSoup
import pickle 

sys.path.append('../')
import settings

data_path = settings.project_path + 'data/gdelt_files/'

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


print "Looking for GDelt files"

update_complete = False
for a in divs:
    filename=a.text
    href = a.attrs['href']
    
    try:
        year = int(filename.split('.zip')[0])
    except:
        continue
    
    if year not in complete_files:
        print "Year %s not found, attempting to download" %year 
        os.system('wget -O ../data/gdelt_files/%s %s' %(filename,urlstem+href))
        complete_files.append(year)
        update_complete = True
    else:
        print "Year %s found in %s, skipping" %(year,gdelt_suc_file)

print "\n\nNOTE:"
print "If you wish to redownload gdelt, delete or modify %s\n\n" %gdelt_suc_file
if update_complete:
    outfile = open(gdelt_suc_file, 'w')
    pickle.dump(complete_files, outfile)
    outfile.close()



# now grab the webpages with the codes

urlstem = 'http://cameocodes.wikispaces.com/'

raw_page = urllib2.urlopen(urlstem).read()

soup = BeautifulSoup(raw_page)

divs = soup.find_all('a',attrs={'class': 'wiki_link'})
print "Fetching CAMEO Codes!"
for currfile in divs:
    filename = currfile.attrs['href'][1:]
    print filename
    raw_page = urllib2.urlopen(urlstem+filename).read()
    newsoup = BeautifulSoup(raw_page)
    if filename=='EventCodes':
        table = newsoup.find_all('div',attrs={'class':'wiki wikiPage'})
    else:
        table = newsoup.find_all('table',attrs={'class':'wiki_table'})
    outfile = open(data_path+filename, 'w')
    for line in table:
         outfile.write(str(line.contents))
    outfile.close()

