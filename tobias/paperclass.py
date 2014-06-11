testfile=open("/home/tobias/BigHarvest/oai:arXiv.org:0704.0001.arXiv.xml","r")
from bs4 import BeautifulSoup
souptest = BeautifulSoup(testfile)    
class Paper:
  def __init__(self, paperfile):
    keyname = paperfile.select('authors author keyname')
    forename = paperfile.select('authors author forenames')
    namelist=[]
    for i in range(0,len(keyname)):
      namelist.append((keyname[i].text, forename[i].text))        
    self.title = paperfile.select('title')[0].text
    self.ident = paperfile.select('id')[0].text
    self.authors = namelist
    self.abstract = paperfile.select('abstract')[0].text
    self.categories = paperfile.select('categories')[0].text 
    self.create = paperfile.select('created')[0].text
    
    
x = Paper(souptest)
#print x.title
#print x.ident
#print x.authors
#print x.abstract
print x.categories
print x.create
