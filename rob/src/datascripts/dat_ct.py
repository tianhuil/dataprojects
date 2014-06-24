
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
    
def pth(f):
  return 'data/' + f


ct_lines(pth('users.json'), 'users')
ct_lines(pth('beeradvocate.json'), 'reviews')
ct_lines(pth('styles.json'), 'styles')
ct_lines(pth('brewers.json'), 'brewers')
ct_lines(pth('beers.json'), 'beers')
ct_prod_data(pth('product_ids.json'), 'product_ids') # should be same as beers

ct_lines(pth('err_ids.txt'), 'err_ids')
ct_lines(pth('err_product_id.txt'), 'err_prod')
ct_lines(pth('err_product_scrap.txt'), 'err_prod_scrap')
ct_lines(pth('dberr_beers.txt'), 'dberr_beers')
ct_lines(pth('dberr_brewers.txt'), 'dberr_brewers')
ct_lines(pth('dberr_styles.txt'), 'dberr_styles')
ct_lines(pth('dberr_revs.txt'), 'dberr_revs')

pp = pprint.PrettyPrinter(indent=4)
pp.pprint(d)
