

from bawebcn import BACn
from lxml.html import fromstring
from collections import namedtuple

from urllib2 import HTTPError

import sys, getopt


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




# retrieve and store users in ID range specified in cli opts
def retrieve_users(argv):
  # data is serialized via json
  import json
  from multiprocessing import Pool
  
  # parse command line options
  def cli_opts(argv):
    def print_ft_exit():
      print 'userdat.py -s <starting_index> -f <ending_index> -o <out_file> -l <err_log_file>'
      sys.exit(2)
      
    def validate_ix(a):
      if a.isdigit() and int(a) > 0:
        return int(a)
      else:
        print_ft_exit()
      
    try:
      opts, args = getopt.getopt(argv,'s:f:o:l:')
    except getopt.GetoptError:
      print_ft_exit()
    
    if len(opts) != 4:
      print_ft_exit()
      
    for opt, arg in opts:
      if opt == '-s':
        s_ix = validate_ix(arg)
      elif opt == '-f':
        f_ix = validate_ix(arg)
      elif opt == '-o':
        out = arg
      elif opt == '-l':
        log = arg
        
    if s_ix > f_ix:
      print_ft_exit();
      
    return [s_ix, f_ix, out, log]
  
  # get all users in id range
  # save those that are found to file o
  # if access is forbidden write id to log
  # the log ids are actual users that weren't retrieved
  def get_users(s, f, o, l):
    for i in xrange(s,f+1):
      u, err = user_profile_parse(i, "")

      # record forbidden user
      if isinstance(err, HTTPError) and err.code == 403:
        with open(l, 'a') as log:
          log.write(str(u.id) + '\n')
      else:
        if u.name:
          with open(o, 'a') as out:
            out.write(json.dumps(u.__dict__) + '\n')

  # extract options
  opt = cli_opts(argv)
  # retrieve and store users in id range
  get_users(*opt)

# python scrapr/userdat.py -s 2 -f 5 -o u.json -l err_id.txt

# test parser
# runs when no cli opts are provided
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
  if len(sys.argv) > 1:
    retrieve_users(sys.argv[1:])
  else:
    run_dummy_test()