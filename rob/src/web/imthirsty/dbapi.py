
# restful resource api that pulls db info

from imthirsty import app
from imthirsty.dbwrapper import PageData

from flask.ext import restful

api = restful.Api(app)

disp = PageData()

class Regions(restful.Resource):
  def get(self):
    return disp.brewer_regions()
    

class Styles(restful.Resource):
  def get(self):
    return disp.styles()


class Brewers(restful.Resource):
  def get(self, region_id):
    return disp.brewers_by_region(region_id)


class Beers(restful.Resource):
  def get(self, brewer_id):
    return disp.beers_by_brewer(brewer_id)


class Recommendations(restful.Resource):
  def get(self, beer_id, style_id):
    return disp.recommendations(beer_id, style_id)
    
class BeerMeta(restful.Resource):
  def get(self, beer_id):
    return disp.beer_meta(beer_id)



api.add_resource(Regions, '/brewer_regions')
api.add_resource(Styles, '/styles')
api.add_resource(Brewers, '/brewers/<string:region_id>')
api.add_resource(Beers, '/beers/<string:brewer_id>')
api.add_resource(Recommendations, '/recommend/<string:beer_id>/<string:style_id>')
api.add_resource(BeerMeta, '/beer_meta/<string:beer_id>')