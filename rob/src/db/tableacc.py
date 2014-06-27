

# generic interface to a database table
# requires an update/insert stored procedure

from beeradcn import Beerad


class TableAcc(object):
  
  def __init__(self, table_name, cols, upsert_proc):
    self.__table_name = table_name
    self.__cols = cols
    self.__upsert_proc = upsert_proc
    self.__rows = []
    
  def __iter__(self):
    for r in self.__rows:
      yield r
      
  def __len__(self): return len(self.__rows)
      
  def _enc(self, s):
    return ''.join([x for x in s if ord(x) < 128])
  
  # not intended for outside use
  def _select(self, cols="", where = "", limit = 0, param = []):
    """ query builder """
    
    sel = ["select"]
    
    cols = cols if cols != "" else self.__cols
    sel.append(", ".join(s in self.__cols))
    
    sel.append("from")
    sel.append(self.__table_name)
    
    if where != "":
      sel.append("where")
      sel.append(where)
      
    if limit:
      sel.append('limit %s')
      param.append(limit)
    
    if param and len(param) == 1:
      param = (param[0],)
    else:
      param = tuple(param)
    
    res = None
    sel = ' '.join(s for s in sel)
    with Beerad() as dbc:
      cur = dbc.cursor()
      cur.execute(sel, param)
      res = cur.fetchall()
      cur.close()
      
    return res
    
  def load_all(self):
    self.__rows = []
    all_r = self._select()
    if wcs is not None:
      self.__rows.extend([r in all_r])
      
    return self
    
  def add_record(self, rec_tup):
    try:
      d = len(tup)
    except:
      # must not be a tuple
      rec_tup = (rec_tup,)
    
    res = None
    with Beerad() as dbc:
      cur = dbc.cursor()
      cur.callproc(self.__upsert_proc, rec_tup)
      res = cur.fetchone()
      
      dbc.commit()
      cur.close()
      
    return res
    
  def remove_all(self):
    with Beerad() as dbc:
      cur = dbc.cursor()
      cur.execute(' '.join(["truncate table", self.__table_name]))
      dbc.commit()
      cur.close()
      
    self.__rows = { }

  def add_many(self, records):
    qry = ["call", self.__upsert, "("]
    ps = ', '.join('%s' for i in range(len(records[0])))
    qry.append(ps)
    qry.append(')')
    
    res = None
    with Beerad() as dbc:
      cur = dbc.cursor()
      cur.executemany(' '.join(qry), records)
      res = cur.fetchone()
      
      dbc.commit()
      cur.close()

