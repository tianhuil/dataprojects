
from urllib2 import urlopen
from urllib2 import URLError
from urllib2 import Request
from lxml.html import fromstring

class BACn(object):
  domain = 'http://www.beeradvocate.com'
  
  def __init__(self):
    self.connect = None
  
  def brewer_meta(self, brewer_id):
    url = 'http://www.beeradvocate.com/beer/profile/%i' % brewer_id
    return self.__open(url)
    
  def beer_meta(self, brewer_id, beer_id):
    url = 'http://www.beeradvocate.com/beer/profile/%i/%i' % (brewer_id, beer_id)
    return self.__open(url)
    
  def __open(self, url):
    req = Request(url, headers = {'User-Agent': 'Mozilla'})
    return urlopen(req)
    