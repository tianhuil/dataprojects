
from urllib2 import urlopen
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
    
  def user_profile(self, u_id, u_name = ""):
    url = 'http://www.beeradvocate.com/community/members/%s.%i/' % (u_name, u_id)
    return self.__open(url)
    
  def __open(self, url):
    req = Request(url, headers = {
      'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
      'Accept-Encoding': 'none',
      'Accept-Language': 'en-US,en;q=0.8',
      'Connection': 'keep-alive'})
    return urlopen(req)
    