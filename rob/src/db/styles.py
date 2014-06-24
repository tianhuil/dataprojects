

from beeradcn import Beerad


class Styles(object):
  
  def __init__(self):
    pass
  
  def __select(self, qry, params):
    res = None
    with Beerad() as dbc:
      cur = dbc.cursor()
      cur.execute(qry, params)
      res = cur.fetchall()
      cur.close()
      
    return res
  
  def __res_as_dict(res)
    if s is not None:
      return { int(r[0]): r[1] for r in s }
    else:
      return { }
      
  def get_all(self):
    qry = "select id, name from styles"
    s = self.__select(qry, ())
    return self.__res_as_dict(s)
      
  def beer_counts(self):
    qry = "select style_id, beer_ct from beerctbystyle"
    s = self.__select(qry, ())
    return self.__res_as_dict(s)

  def style_name(self, style_id):
    


