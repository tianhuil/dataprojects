testfile=open("/home/tobias/BigHarvest/oai:arXiv.org:0704.0001.arXiv.xml","r")
from bs4 import BeautifulSoup
import re
class Paper:
  def __init__(self, paperfile):
    names= paperfile.select('authors author')
    authors=[]
    for i in range(0,len(keyname)):
      key = re.match( r"<author><keyname>(.+)</keyname>", str(keyname[i]) )
      fore = re.match(r"<author><keyname>.+</keyname><forenames>(.+)</forenames>", str(keyname[i]))
      if (key and fore):
        authors.append((key.group(1), fore.group(1)))
      elif key:
        authors.append(key.group(1))
      else:
        print 'ERROR- no authors'      
    self.title = re.sub( '\n', ' ', paperfile.select('title')[0].text)
    self.ident = paperfile.select('id')[0].text
    self.authors = authors
    self.abstract = re.sub('\n', ' ', paperfile.select('abstract')[0].text)
    self.categories = paperfile.select('categories')[0].text.split() 
    self.create = paperfile.select('created')[0].text 
    self.mscclass = temp
    self.summary = (self.ident, self.create, self.title) 
