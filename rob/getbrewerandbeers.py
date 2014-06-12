
# scan the beeradvocate data reviews to retrieve the brewer and beer ids used
# use the set to get the brewer/beer meta data from the web
# write info to brewerdata.txt and beerdata.txt
# write out production dictionary { brewer: [beers] } to products.json

import json
from scrapr.brewermeta import brewer_meta_parse
from scrapr.beermeta import beer_meta_parse

prods = { }
all_beers = []
with open('data/beeradvocate.json', 'r') as revs, \
    open('data/brewerdata.json', 'w') as brs, \
    open('data/beerdata.json', 'w') as bes:
      
  for rev in revs:
    try:
      r = json.loads(rev)
      br_id = r["beer"]["brewer_id"]
      if br_id not in prods:
        meta = brewer_meta_parse(br_id)
        prods[br_id] = []
        
        brs.write(json.dumps(meta.__dict__) + '\n')
        
        
        
      be_id = r["beer"]["id"]
      if be_id not in prods[br_id]:
        if be_id in all_beers:
          # this beer id already assigned to another brewer
          # report br_id, be_id combo error
          with open('data/err_product_id.txt', 'a') as ert:
            ert.write("{0},{1}".format(br_id, be_id))
        else:
          meta = beer_meta_parse(br_id, be_id)
          prods[br_id].append(be_id)
          all_beers.append(be_id)
          bes.write(json.dumps(meta.__dict__) + '\n')
    except:
      with open('data/err_product_scrap.txt', 'a') as ert:
        ert.write("{0},{1}".format(br_id, be_id))
    
# write out product code combos
with open('data/products.json', 'w') as p:
  p.write(json.dumps(prods))
    
print 'DONE'
