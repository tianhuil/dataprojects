

# leverage db abstraction lib to make
# a web getter/json friendly db wrapper

# annoying boilerplate
# always make cmd line calls from parent of src and data
import sys
sys.path.append('src/')

# db abstraction lib
from db.beers import Beers
from db.brewers import Brewers
from db.styles import Styles


class PageData(object):
  def __init__(self):
    pass
  
  
