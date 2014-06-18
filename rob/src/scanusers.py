
import sys, getopt
from urllib2 import HTTPError

# command line proc that retrieves users in a given user_id range
# users are stored in <out_file> using json
# ids that yield HTTP Forbidden errors are stored in <err_log_file>
# syntax: python scanusers.py -s <starting_index> -f <ending_index> -o <out_file> -l <err_log_file>

# retrieve and store users in ID range specified in cli opts
def retrieve_users(argv):
  # data is serialized via json
  import json
  
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
    except Exception as e:
      print e
    
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
  
  
  

if __name__ == '__main__':
  retrieve_users(sys.argv[1:])