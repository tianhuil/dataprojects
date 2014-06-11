import re
import sys
import os


infile = open('../data/gdelt_files/2000.csv')

for line in infile.readlines():
    print line
    print len(line.split('\t'))
    raw_input()
