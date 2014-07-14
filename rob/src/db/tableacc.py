

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
  
  def _view(self, view_name, distinct=False, cols="", where="", order_by="", limit=0, param = []):
    res = None
    if not any(s in view_name for s in ['drop', 'truncate']):
      old = self.__table_name
      try:
        self.__table_name = view_name
        
        res = self._select(
          distinct=distinct,
          cols=cols,
          where=where,
          order_by=order_by,
          limit=limit,
          param=param)
      except Exception as e:
        print e
      
      self.__table_name = old
      
    return res
  
  # not intended for outside use
  def _select(self, distinct=False, cols="", where="", order_by="", limit=0, param = []):
    """ query builder """
    
    # prevent out of scope update
    # python default values are dumb
    alt_param = param[:]
    
    # check for injection
    inj_keys = ['drop', 'truncate']
    check = [cols, where, order_by]
    for k in inj_keys:
      for c in check:
        if k in c:
          raise ValueError('No drop or truncate statements allowed in select')
    
    sel = ["select"]
    
    if distinct:
      sel.append("distinct")
    
    cols = cols if cols != "" else self.__cols
    if len(cols) > 1:
      sel.append(", ".join(cols))
    
    sel.append("from")
    sel.append(self.__table_name)
    
    if where != "":
      sel.append("where")
      sel.append(where)
      
    if order_by != "":
      sel.append("order by")
      sel.append(order_by)
      
    if limit:
      sel.append('limit %s')
      alt_param.append(limit)
      
    if alt_param and len(alt_param) == 1:
      alt_param = (alt_param[0],)
    else:
      alt_param = tuple(alt_param)
      
    res = None
    sel = ' '.join(s for s in sel)
    with Beerad() as dbc:
      cur = dbc.cursor()
      cur.execute(sel, alt_param)
      res = cur.fetchall()
      cur.close()
      
    return res
  
  def _exec_proc(self, proc, inputs):
    qry = ["call", proc, "("]
    ps = ', '.join('%s' for i in range(len(inputs)))
    qry.append(ps)
    qry.append(')')
    
    res = None
    with Beerad() as dbc:
      cur = dbc.cursor()
      
      cur.execute(' '.join(qry), inputs)
      res = cur.fetchall()
      
      #dbc.commit()
      cur.close()
      
    return res
      
  def _exec_many_procs(self, proc, records):
    qry = ["call", proc, "("]
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
  
  def row_count(self):
    return self._select(cols=["count(*)"])[0]
    
  def load_all(self):
    self.__rows = []
    all_r = self._select()
    if all_r is not None:
      self.__rows.extend(all_r)
      
    return self
    
  def add_record(self, rec_tup):
    try:
      d = len(rec_tup)
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
    self._exec_many_procs(self.__upsert_proc, records)

