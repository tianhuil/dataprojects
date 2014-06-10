
# beer page format
# http://www.beeradvocate.com/beer/profile/brewery_id/beer_id


# div class="mainContent"
#   div id="titleBar"
#     <h1> "beer name in quotes <span> - brewery name
#
#   div class="baContent"
#     table->tbody->tr-> second td is table of meta info

from urllib2 import urlopen
from urllib2 import URLError
from urllib2 import Request
from lxml.html import fromstring

# test with Long Trail (94) Blackberry Wheat (3636)
# fyi: the rating here is too generous
url = 'http://www.beeradvocate.com/beer/profile/157/127'
url = 'http://www.beeradvocate.com/beer/profile/94/3636'
req = Request(url, headers = {'User-Agent': 'Mozilla'})
burl = urlopen(req)
lx_doc = fromstring(burl.read())
burl.close()

main = lx_doc.xpath('//div[@class="mainContent"]')[0]

beer_name = main.xpath('//div[@class="titleBar"]')[0][0].text.strip()
print beer_name

metatab = main.xpath('//div[@id="baContent"]')[0].xpath('child::table')[0]

print "BA " + metatab.xpath('//span[@class="BAscore_big"]')[0].text
print "bros " + metatab.xpath('//span[@class="BAscore_big"]')[1].text

style = metatab.xpath('//a[contains(@href, "/beer/style")]')[0]
print "Style Num: " + style.xpath('@href')[0].split('/')[3]
print "Style    : " + style.xpath('b')[0].text

import re
qual_dat = style.xpath('..//text()')

rec_notes = False
notes = []
for t in qual_dat:
  if '|' in t and 'Style' not in t:
    ti = re.findall(r'\d+', t)
    print "ABV: " + ".".join(ti) + '%'
  elif 'IBU' in t:
    ti = re.findall(r'\d+', t)
    print "IBU: " + str(int(ti[0]) if ti[0].isdigit() else -1)
  elif 'added' in t:
    print "Added: " + t.split("on")[1].replace(')', '')
  elif 'Notes' in t:
    rec_notes = True
  elif rec_notes and t.strip() != '\n':
    notes.append(t.strip())
      
notes = ' '.join(notes)
print "Notes: " + notes

if __name__ == '__main__':
  brewer_id = 94
  beer_id = 3636