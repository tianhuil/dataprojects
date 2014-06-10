
#!/usr/bin/python

from urllib2 import urlopen
from urllib2 import URLError
from lxml.html import fromstring

class Airplane(object):
  """Scrapr interface to planefinder.net for plane information by plane registratation number"""
  
  def __init__(self, reg_num):
    """Specific aircraft is identified by registration number"""
    self.reg_num = reg_num
    
    self.data_dict = { }
  
  def plane_info_url(self):
    """URL where aircraft info is located"""
    return "http://planefinder.net/data/aircraft/" + self.reg_num
    
  @property
  def aircraft(self):
    return self.data_dict["Aircraft"]
    
  @property
  def age(self):
    return self.data_dict["Age"]
    
  @property
  def model(self):
    return self.data_dict["Model"]
  
  @property
  def airline(self):
    return self.data_dict["Airline name"]
    
  def load(self):
    """Connect to webpage and retrieve info"""
    try:
      pf = urlopen(self.plane_info_url())
    except:
      raise URLError("Airplane.load(): " + self.plane_info_url())
    else:
      lx_doc = fromstring(pf.read())
      pf.close()
    
    pi = lx_doc.xpath('//td[@class = "stacked-stat"]')
    for p in pi:
      t = p.xpath('./*')
      if '\n' in t[0].text:
        t[0].text = "Jet engines"
      if t and t[0].text:
        
        if t[1].xpath('./*'):
          val = t[1].xpath('./*')[0].text
        elif "old" in t[1].text:
          val = int(t[1].text.split(' ')[0].strip())
        else:
          val = t[1].text.replace('\n', ' ').strip()
        
        self.data_dict[t[0].text] = val
      
      
      
      
if __name__ == '__main__':
  plane = Airplane("PR-AVL")
  print "Registration Number: " + plane.reg_num
  print "Info URL: " + plane.plane_info_url()
  plane.load()
  print plane.data_dict
  print plane.reg_num + " " + plane.airline + " " + plane.model + " " + str(plane.age)