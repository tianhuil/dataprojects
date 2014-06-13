

from bawebcn import BACn
from lxml.html import fromstring
from collections import namedtuple


User = namedtuple('User', 'id, name, title, location, sex')

def user_profile_parse(u_id, u_name = ""):
  
  try:
    ba_connect = BACn()
    burl = ba_connect.user_profile(u_id, u_name)
    lx_doc = fromstring(burl.read())
  except Exception as e:
    return User(u_id, None, None, None, None), e
  
  if not u_name:
    u_name = lx_doc.xpath('//*[@class="username"]')[0].text
  
  title = lx_doc.xpath('//*[@class="userTitle"]')[0].text
  
  loc = lx_doc.xpath('//a[contains(@href,"misc/location-info?")]')
  u_loc = loc[0].text if loc else "Unknown"
  
  blurb = lx_doc.xpath('//*[@class="userBlurb"]/text()')
  if any(s for s in blurb if 'Male' in s):
    sex = "Male"
  elif any(s for s in blurb if 'Female' in s):
    sex = "Female"
  else:
    sex = "Unspecified"
    
  return User(u_id, u_name, title, u_loc, sex), None




# test parser
def run_dummy_test():
  def print_u_prof(user):
    print "User Name  : %s" % user.name
    print "User ID    : %i" % user.id
    print "Title/Rank : %s" % user.title
    print "Location   : %s" % user.location
    print "Sex        : %s" % user.sex
    
  # test with my two dummy accounts
  rob_t_id = 804276
  rob_t = user_profile_parse(rob_t_id)
  print_u_prof(rob_t)
  
  rob_h_id = 804253
  rob_h = user_profile_parse(rob_h_id)
  print_u_prof(rob_h)
  
  nonexistent_id = 80000
  fake = user_profile_parse(nonexistent_id)
  print_u_prof(fake)
  
  
  
if __name__ == '__main__':
  run_dummy_test()