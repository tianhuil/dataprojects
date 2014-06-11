
# beer page format
# http://www.beeradvocate.com/beer/profile/brewery_id/beer_id


# div class="mainContent"
#   div id="titleBar"
#     <h1> "beer name in quotes <span> - brewery name
#
#   div class="baContent"
#     table->tbody->tr-> second td is table of meta info

import re
from bawebcn import BACn
from lxml.html import fromstring
from collections import namedtuple

def beer_meta_parse(brewer_id, beer_id):
  def int_or_def(nstr, nerr):
    return int(nstr) if nstr.isdigit() else nerr
    
  BeerMeta = namedtuple('BeerMeta',
    'beer_name, style_num, style, abv, ibu, date_added, ba_score, bros_score, notes')

  ba_connect = BACn()
  burl = ba_connect.beer_meta(brewer_id, beer_id)
  lx_doc = fromstring(burl.read())
  burl.close()
    
  main = lx_doc.xpath('//div[@class="mainContent"]')[0]
  beer_name = main.xpath('//div[@class="titleBar"]')[0][0].text.strip()
  metatab = main.xpath('//div[@id="baContent"]')[0].xpath('child::table')[0]
  ba_scr = int_or_def(metatab.xpath('//span[@class="BAscore_big"]')[0].text,-1)
  bro_scr = int_or_def(metatab.xpath('//span[@class="BAscore_big"]')[1].text,-1)
  style_link = metatab.xpath('//a[contains(@href, "/beer/style")]')[0]
  style_num = int_or_def(style_link.xpath('@href')[0].split('/')[3],-1)
  style = style_link.xpath('b')[0].text
  
  
  qual_dat = style_link.xpath('..//text()')
  
  rec_notes = False
  notes = []
  for t in qual_dat:
    if '|' in t and 'Style' not in t:
      ti = re.findall(r'\d+', t)
      abv = ".".join(ti) + '%'
    elif 'IBU' in t:
      ti = re.findall(r'\d+', t)
      ibu = int_or_def(ti[0], -1)
    elif 'added' in t:
      date_add = t.split("on")[1].replace(')', '')
    elif 'Notes' in t:
      rec_notes = True
    elif rec_notes and t.strip() != '\n':
      notes.append(t.strip())
        
  notes = ' '.join(notes)
  
  return BeerMeta(
    beer_name, style_num, style, abv, ibu,
    date_add, ba_scr, bro_scr, notes)
  

if __name__ == '__main__':
  # test with Long Trail (94) Blackberry Wheat (3636)
  # fyi: the BA rating is too generous
  brewer_id = 94
  beer_id = 3636
  
  beer = beer_meta_parse(brewer_id, beer_id)
  print "Beer Name  : %s" % beer.beer_name
  print "BA Score   : %i" % beer.ba_score
  print "Bros Score : %i" % beer.bros_score
  print "Style Num  : %i" % beer.style_num
  print "Style      : %s" % beer.style
  print "ABV        : %s" % beer.abv
  print "IBU        : %i" % beer.ibu
  print "Notes      : %s" % beer.notes
  print "Date Added : %s" % beer.date_added
