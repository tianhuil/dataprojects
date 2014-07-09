
import pandas as pd
import numpy as np

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
  
  # put two column results in dict
  def __res_as_dict(self,res):
    if res is not None:
      return { int(r[0]): r[1] for r in res }
    else:
      return { }
      
  def __limit_param_tup(self, limit):
    param = ()
    try:
      limit = int(limit)
      if limit > 0:
        param = (limit, )
    except:
      pass
    
    return param
      
  # dataframe index shuffler
  def __shuffle_ix(self, df):
    nix = np.random.permutation(df.index)
    df = df.reindex(index=nix, copy=False)
    return df.reset_index().drop('index',1)
      
  def get_all(self):
    qry = "select id, name from styles"
    s = self.__select(qry, ())
    return self.__res_as_dict(s)
      
  def beer_counts(self, limit = 0):
    qry = "select style_id, beer_ct from beerctbystyle"
    
    param = self.__limit_param_tup(limit)
    if len(param):
      qry = '{0} {1}'.format(qry, 'limit %s')
    s = self.__select(qry, param)
    return self.__res_as_dict(s)
    
  def review_counts(self, limit = 0):
    qry = "select style_id, rev_ct from reviewctbystyle"
    
    param = self.__limit_param_tup(limit)
    if len(param):
      qry = '{0} {1}'.format(qry, 'limit %s')
    s = self.__select(qry, param)
    return self.__res_as_dict(s)
    
  def top_reviewed_styles(self, limit = 0):
    qry = """select s.id, s.name
      from reviewctbystyle r inner join styles s
        on r.style_id = s.id"""
    
    param = self.__limit_param_tup(limit)
    if len(param):
      qry = '{0} {1}'.format(qry, 'limit %s')
      
    return self.__select(qry, param)

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
        and char_length(replace(trim(review),'\n','')) > 30 """
      
    try:
      style_id = int(style_id)
      limit = int(limit)
    except:
      return None
      
    if limit:
      params = (style_id, limit)
      qry = '{0} {1}'.format(qry, 'limit %s')
    else:
      params = (style_id,)
      
    return self.__select(qry, params)

  def beer_reviews_df(self, style_id, limit=0):
    dt = self.beer_reviews(style_id, limit)
    reviews = pd.DataFrame.from_records((r for r in dt),
      columns=['style_id','beer_id','review'])
      
    return reviews
      
  def beer_reviews_rollup(self, style_ids, limit=0, rev_rollup_ct=10, shuffle=True):
    """Get rolled up beer review docs for a list of style ids. More memory efficient
    than getting a bunch of style reviews and then rolling them all up"""
    
    r = { s: pd.DataFrame() for s in style_ids }
    for s in style_ids:
      r[s] = self.beer_reviews_df(s, limit)           # get data
      if shuffle:
        r[s] = self.__shuffle_ix(r[s])                  # shuffle it
      r[s]['rev_doc'] = r[s].index % rev_rollup_ct    # set rev_rollup_ct indices
      
      # combine the reviews into rev_rollup_ct docs
      r[s] = r[s].groupby(['style_id', 'beer_id', 'rev_doc']).apply(lambda x: ' '.join(x['review']))
    
    r = pd.concat([r[s] for s in style_ids])
    r = r.reset_index()
    if shuffle:
      r = self.__shuffle_ix(r)
    r.columns = ['style_id', 'beer_id', 'rev_doc', 'review']
    
    return r
