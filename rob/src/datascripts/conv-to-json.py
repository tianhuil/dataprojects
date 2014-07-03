

#!/usr/bin/python

import json

# read raw data and convert to json

# raw data fields
# map for renaming some fields
field_map = {
  'name': "name",
  'beerid': "id",
  'brewerid': "brewer_id",
  'abv': "abv",
  'style': "style",
  "appearance": "appearance",
  "aroma": "aroma",
  "palate":"palate",
  "taste":"taste",
  "overall": "overall",
  "time":"date",
  "profilename": "user_name",
  "text": "review",
  "review": "review"
}

# build json format w two subcategories
# one for beer info and other for the review
def def_container():
  return {
    "beer": {
      "id": 0,
      "name":"",
      "brewer_id": 0,
      "abv": 0,
      "style": ""
    },
    "review": {
      "user_name": "",
      "date": 0,
      "aroma": 0,
      "palate": 0,
      "taste": 0,
      "overall": 0,
      "review": ""
    }
  }
  
  
def clean(field, value):
  def enc(s):
    return ''.join([x for x in s if ord(x) < 128])
  
  ints = [ "id", "brewer_id" ]
  dec = [ "abv", "appearance", "aroma", "palate", "taste", "overall" ]
  chk_enc = [ "style", "text", "review" ]
  rem_nl = [ "name", "user_name", "date" ]
  rem_nl.extend(ints)
  rem_nl.extend(dec)
  rem_nl.extend(chk_enc)

  if field in rem_nl:
    value = value.strip().replace('\n','')
  
  if field in chk_enc:
    value = enc(value.replace('\t',' '))

  if field in ints:
    value = int(value) if value.isdigit() else 0
    
  if field in dec:
    try:
      value = float(value)
    except:
      value = 0
    
  return value
  
                  
with open('data/beeradvocate.txt', 'r') as raw, open('data/beeradvocate.json', 'w') as j:
  d = None
  for row in raw:
    if row not in ['','\n']:
      # review begins w a beer/name
      if 'beer/name' in row:
        # save prior review
        if d is not None:
          j.write(json.dumps(d) + '\n')
        
        d = def_container()
        
      try:
        r = row.split(":")
        c, f = r[0].split('/')
        
        # review text has ':' in it
        if len(r) > 2:
          r = [r[0], ': '.join(r[1:])]
        
        new_f = field_map[f.lower()]
        d[c][new_f] = clean(new_f, r[1])
      except Exception as e:
        pass
