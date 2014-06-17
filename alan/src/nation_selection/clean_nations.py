import os

repstrings = [('"Virgin Islands, U.S."', 'US Virgin Islands'),
              ('"Virgin Islands, British"', 'British Virgin Islands'),
              ('"Gambia, The"', 'Gambia'),
              ('"China, Hong Kong SAR"', 'Hong Kong'),
              ('"China, Taiwan Province of"', 'Taiwan'),
              ('"China, Macao SAR"', 'Macao')]

filenames = ['../data/cornExport.csv','../data/oilExport.csv',
             '../data/natural_gasExport.csv' , '../data/oilProduction.csv',
             '../data/natural_gasImport.csv' , '../data/wheatExport.csv',
             '../data/oilConsumption.csv'  ,   '../data/wheatImport.csv']


for curfile in filenames:
    infile = open(curfile).read()
    for tmpstr in repstrings:
        infile = infile.replace(tmpstr[0],tmpstr[1])

    outfile = open(curfile, 'w')
    outfile.write(infile)
    outfile.close()
