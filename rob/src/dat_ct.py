
import json
import pprint

d = { }

def ct_lines(file, label):
  d[label] = 0
  with open(file, 'r') as f:
    for r in f:
      d[label] += 1

def ct_prod_data(file, label):
  d[label] = 0
  with open(file, 'r') as f:
    bs = json.loads(f.read())
    beers = 0
    for k, v in bs.iteritems():
      beers += len(v)
      
    d[label] = {
      "brewers": len(bs),
      "beers": beers
    }

ct_lines('data/users.json', 'users')
ct_lines('data/beeradvocate.json', 'reviews')
ct_lines('data/styles.json', 'styles')
ct_lines('data/brewers.json', 'brewers')
ct_lines('data/beers.json', 'beers')
ct_prod_data('data/product_ids.json', 'product_ids') # should be same as beers
ct_lines('data/err_product_scrap.txt', 'err_prod')
ct_lines('data/err_ids.txt', 'err_ids')

pp = pprint.PrettyPrinter(indent=4)
pp.pprint(d)
