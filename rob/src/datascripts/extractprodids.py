
# scan the beeradvocate data reviews to retrieve the brewer and beer ids used
import json

dirc = 'data/'

def pth(f):
  return dirc + f
  
prods = { }
all_beers = []

with open(pth('err_product_id.txt'), 'w') as dum:
  # dummy open; either create or overwrite if exists
  # not worth leaving open since it will be written to infrequently
  # track beers assigned to multiple breweries
  pass

# first compile list of valid product offerings
with open(pth('beeradvocate.json'), 'r') as revs:
      
  for rev in revs:
    try:
      r = json.loads(rev)
      br_id = r["beer"]["brewer_id"]
      be_id = r["beer"]["id"]
      
      if br_id not in prods:
        prods[br_id] = []
      
      if be_id not in prods[br_id]:
        if be_id in all_beers:
          # this beer id already assigned to another brewer
          # report br_id, be_id combo error
          with open(pth('err_product_id.txt'), 'a') as ert:
            ert.write("{0},{1}\n".format(br_id, be_id))
        else:
          prods[br_id].append(be_id)
          all_beers.append(be_id)
    except Exception as e:
      with open(pth('err_product_id.txt'), 'a') as ert:
        ert.write("{0},{1}\n".format(e,rev))

# save products in { "brew_id": [beers] } json format
# brew_id as a string for a key is a bit annoying, but required
with open(pth('product_ids.json'), 'w') as pid:
  pid.write(json.dumps(prods) + '\n')
  
print 'EXTRACTED ALL PRODUCTS'