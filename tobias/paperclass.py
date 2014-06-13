from bs4 import BeautifulSoup
import re

class Paper:
  def __init__(self, paperfile):
    names= paperfile.select('authors author')
    authors=[]
    for i in range(0,len(names)):
      key = re.match( r"<author><keyname>(.+)</keyname>", str(names[i]) )
      fore = re.match(r"<author><keyname>.+</keyname><forenames>(.+)</forenames>", str(names[i]))
      if (key and fore):
        authors.append((key.group(1), fore.group(1)))
      elif key:
        authors.append(key.group(1))
      else:
        print 'ERROR- no authors'  
    tempclass= None
    if paperfile.find('msc-class') is None:
        tempclass= None
    else:
        tempclass = paperfile.find('msc-class').text.split(';')
    self.title = paperfile.select('title')[0].text
    self.ident = paperfile.select('id')[0].text
    self.authors = authors
    self.abstract = re.sub('\n', ' ', paperfile.select('abstract')[0].text)
    self.categories = paperfile.select('categories')[0].text.split()
    self.mscclass = tempclass
    self.create = paperfile.select('created')[0].text 
    self.summary = (self.ident, self.title, self.abstract, self.categories, self.mscclass) 
