

# use the set to get the brewer/beer meta data from the web
# write info to brewerdata.txt and beerdata.txt
# write out production dictionary { brewer: [beers] } to products.json

import json
from scrapr.brewermeta import brewer_meta_parse
from scrapr.beermeta import beer_meta_parse

dirc = 'data/'

def pth(f):
  return dirc + f

with open(pth('product_ids.json'), 'r') as pids:
  prods = json.loads(pids.read())
    
print 'LOADED PRODUCTS'
print 'START SCRAPING META'

with open(pth('err_product_scrap.txt'),'w') as dum:
  # dummy open; either create or overwrite if exists
  # not worth leaving open since it will be written to infrequently
  pass

# check for encoding errors in foreign beer names
# brute force appears to be all that's working
def enc(s):
  return ''.join([x for x in s if ord(x) < 128])

# clean and dump
def cl_d(meta):
  m_dict = meta.__dict__
  m_dict["name"] = enc(meta.name)
  return json.dumps(m_dict)

# make url requests to retrieve meta data for each product (brewer,id) combo
with open(pth('brewers.json'), 'w') as brs, \
    open(pth('beers.json'), 'w') as bes:
      
  for brewer, beers in prods.iteritems():
    try:
      # json keys are strings
      brewer = int(brewer)
      meta = brewer_meta_parse(brewer)
      brs.write(cl_d(meta) + '\n')

      for beer in beers:
        try:
          meta = beer_meta_parse(brewer, beer)
          bes.write(cl_d(meta) + '\n')
        except:
          print "{0}:{1}:{2}\n".format(brewer, beer, e)
          with open(pth('err_product_scrap.txt'), 'a') as ert:
            ert.write("{0}:{1}:{2}\n".format(brewer, beer, e))
        
    except Exception as e:
      print "{0}:{1}:{2}\n".format(brewer, -1, e)
      with open(pth('err_product_scrap.txt'), 'a') as ert:
        ert.write("{0}:{1}:{2}\n".format(brewer, -1, e))
      

print 'DONE'
