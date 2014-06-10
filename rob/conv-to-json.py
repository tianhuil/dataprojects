

#!/usr/bin/python

import json

# read raw data and convert to json

# raw data fields
beer_fields = [ "beer_name", "beer_id", "brewer_id", "abv", "style" ]
rev_fields = [  "appearance", "aroma", "palate", "taste", "overall", "date",
                "prof_name", "review" ]

# map data to field
def parse(file, row, fields):
  d = { }
  for f in fields:
    r = row.split(":")
    d[f] = r[1]
    row = file.next()
    
  return d

j_lst = []
with open('beeradvocate.txt', 'r') as file:
  row = file.next()
  for row in file:
    # review begins w a beer/name
    if 'beer/name' in row:
      # build json format w two subcategories
      # one for beer info and other for the review
      d = {
        "beer": parse(file, row, beer_fields),
        "review": parse(file, row, rev_fields)
      }
      
      j_lst.append(d)
      
# write out json data file
with open('beeradvocate.json', 'w') as wr:
  json.dump(j_lst, wr)
