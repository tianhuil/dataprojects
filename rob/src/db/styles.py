

from db.beeradcn import Beerad


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
  
  def __res_as_dict(res):
    if s is not None:
      return { int(r[0]): r[1] for r in s }
    else:
      return { }
      
  def get_all(self):
    qry = "select id, name from styles"
    s = self.__select(qry, ())
    return self.__res_as_dict(s)
      
  def beer_counts(self, limit = 0):
    qry = "select style_id, beer_ct from beerctbystyle"
    
    param = ()
    try:
      limit = int(limit)
      if limit > 0:
        param = (limit, )
    except:
      pass
    
    s = self.__select(qry, param)
    return self.__res_as_dict(s)

  def style_name(self, style_id):
    qry = "select name from styles where id = %s"
    s = self.__select(qry, (style_id, ))
    if s is not None:
      return s[0][0]
      
  def beer_reviews(self, style_id, limit = 0):
    qry = """
      select be.style_id, r.beer_id, r.review
      from reviews r inner join beers be
        on r.beer_id = be.id
      where be.style_id = %s
        and char_length(replace(trim(review),'\n','')) > 30
      limit %s """
      
    try:
      style_id = int(style_id)
      limit = int(limit)
    except:
      return None
      
    params = (style_id, limit) if limit else (style_id,)
    return self.__select(qry, params)


