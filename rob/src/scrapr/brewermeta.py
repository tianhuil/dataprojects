
# brewery page format
# http://www.beeradvocate.com/beer/profile/brewery_id

# div class="titleBar"
#   <h1> brewery name </h1>

# div id="baContent"
#  ...
#  <td align="left">
    # should return two tds
    # first beer stats, beer ratings, beer avg
    # second should have location

    # find <a href http://www.beeradvocate.com/place/directory/


from bawebcn import BACn
from lxml.html import fromstring
from collections import namedtuple

def brewer_meta_parse(brewer_id):
  
  BrewerMeta = namedtuple('BrewerMeta', 'id, name, location')
  
  ba_connect = BACn()
  burl = ba_connect.brewer_meta(brewer_id)
  lx_doc = fromstring(burl.read())
  burl.close()

  name = lx_doc.xpath('//div[@class="titleBar"]')[0].xpath('h1/text()')[0]

  loc_inf = lx_doc.xpath('//a[contains(@href, "/place/directory")]')
  loc = ', '.join(l.text for l in loc_inf if l.xpath('@href')[0] != '/place/directory/')
  
  return BrewerMeta(brewer_id, name, loc)
  
  
if __name__ == '__main__':
  # test with Long Trail (94)
  brewer_id = 94
  brewer = brewer_meta_parse(brewer_id)
  print "ID       : %i" % brewer.id
  print "Name     : %s" % brewer.name
  print "Location : %s" % brewer.location
