import sys
import os


for count in range(2002, 2006):
    os.system('wget -c http://data.gdeltproject.org/events/%d.zip' %count)

