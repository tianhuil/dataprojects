
# connection to beerad database
# inspired by pure laziness
# use as follows
# with Beerad() as dbc:
#   do some stuff like
#   cur = dbc.cursor()
#   dbc.commit()
#   cur.close()
# auto opens and closes connection with credential file

import json
import MySQLdb as mdb
  
  
class DbCon(object):
  
  def __init__(self, db):
    self.con = None
    self.db_name = db
  
  def open_cn(self, cred_f):
    with open(cred_f) as c:
      creds = json.load(c)
  
    self.con = mdb.connect(host='localhost', user=creds["uname"], passwd=creds["pwd"], db=self.db_name)
    
  def cursor(self):
    if self.con is not None:
      return self.con.cursor()
    else:
      return None
      
  def commit(self):
    self.con.commit()
    
  def close(self):
    self.con.close()
    
  def __enter__(self):
    self.open_cn()
    return self
    
  def __exit__(self, type, value, traceback):
    self.close()


class Beerad(DbCon):
  
  def __init__(self):
    super(Beerad, self).__init__('beerad')
    
  def open_cn(self):
    super(Beerad, self).open_cn('creds.json')