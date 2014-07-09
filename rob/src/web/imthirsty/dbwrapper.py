

# leverage db abstraction lib to make
# a web getter/json friendly db wrapper

# annoying boilerplate
# always make cmd line calls from parent of src and data
import sys
sys.path.append('src/')

# db abstraction lib
from db.locations import Locations
from db.beers import Beers
from db.brewers import Brewers
from db.styles import Styles


class PageData(object):
  def __init__(self):
    self.region = Locations()
    self.brewer = Brewers()
    self.style = Styles()
    self.beer = Beers()
  
  def __to_dict(self, field_dict, records):
    out = []
    for r in records:
      d = {}
      for k,v in field_dict.iteritems():
        d[k] = r[v]
        
      out.append(d)
      
    return out
  
  def brewer_regions(self):
    return self.__to_dict(
      { 'region_id': 0, 'name': 1},
      self.region.top_beer_ct(10))
      
  def styles(self):
    return self.__to_dict(
      { 'style_id': 0, 'name': 1 },
      self.style.top_reviewed_styles(10))
      
      
  def brewers_by_region(self, region_id):
    return self.__to_dict(
      { 'brewer_id': 0, 'name': 1 },
      self.brewer.has_recommended_beers_by_loc(region_id, order_by="name"))
      
  def beers_by_brewer(self, brewer_id):
    return self.__to_dict(
      { 'beer_id': 1, 'name': 2 },
      self.beer.has_rec_by_brewer(brewer_id))
  
  def recommendations(self, beer_id, style_id):
    return self.__to_dict(
      { 'brewer_id': 2, 'brewer_name': 3, 'beer_id': 4, 'name': 5, 'score': 6 },
      self.beer.recommendations(beer_id, style_id, 10))
  
