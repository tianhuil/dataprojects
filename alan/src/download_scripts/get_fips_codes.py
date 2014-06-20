import sys
import os
import urllib2
from bs4 import BeautifulSoup
import pickle 

sys.path.append('../')
import settings

data_path = settings.project_path + 'data/gdelt_files/'

urlstem = 'http://en.wikipedia.org/wiki/List_of_FIPS_country_codes'
raw_page = urllib2.urlopen(urlstem).read()

soup = BeautifulSoup(raw_page)

divs = soup.find_all('tr')


print divs
