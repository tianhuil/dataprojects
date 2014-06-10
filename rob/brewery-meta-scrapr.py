
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


from urllib2 import urlopen
from urllib2 import URLError
from urllib2 import Request
from lxml.html import fromstring

# test with Long Trail, id = 94
url = 'http://www.beeradvocate.com/beer/profile/94/'
req = Request(url, headers = {'User-Agent': 'Mozilla'})
burl = urlopen(req)
lx_doc = fromstring(burl.read())
burl.close()

loc = lx_doc.xpath('//div[@id="baContent"]')[0].xpath('//a[contains(@href, "/place/directory")]')
print loc
for l in loc:
  if l.xpath('@href')[0] != '/place/directory':
    print l.text