
# restful resource api that pulls db info

from imthirsty import app
from flask.ext import restful

api = restful.Api(app)

class Regions(restful.Resource):
  def get(self):
    return [
      {'region_id':1, 'name':'region 1'},
      {'region_id':2, 'name':'region 2'},
      {'region_id':3, 'name':'region 3'}
    ]
    

class Styles(restful.Resource):
  def get(self):
    return [
      {'style_id':1, 'name':'style 1'},
      {'style_id':2, 'name':'style 2'},
      {'style_id':3, 'name':'style 3'}
    ]


class Brewers(restful.Resource):
  def get(self, region_id):
    return [
      {'brewer_id':1, 'name':'brewer 1'},
      {'brewer_id':2, 'name':'brewer 2'},
      {'brewer_id':3, 'name':'brewer 3'}
    ]


class Beers(restful.Resource):
  def get(self, brewer_id):
    return [
      {'beer_id':1, 'style_id':1, 'name':'beer 1'},
      {'beer_id':2, 'style_id':2, 'name':'beer 2'},
      {'beer_id':3, 'style_id':3, 'name':'beer 3'}
    ]


class Recommendations(restful.Resource):
  def get(self, beer_id, style_id):
    return [
      {'beer_id':1, 'name':'beer rec 1'},
      {'beer_id':2, 'name':'beer rec 2'},
      {'beer_id':3, 'name':'beer rec 3'}
    ]



api.add_resource(Regions, '/brewer_regions')
api.add_resource(Styles, '/styles')
api.add_resource(Brewers, '/brewers/<string:region_id>')
api.add_resource(Beers, '/beers/<string:brewer_id>')
api.add_resource(Recommendations, '/recommend/<string:beer_id>/<string:style_id>')