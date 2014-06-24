

import pandas as pd
import numpy as np

from db.styles import Styles
from reviewvectorizer import ReviewTfidf

# dataframe index shuffler
def shuffle_ix(df):
  nix = np.random.permutation(df.index)
  df = df.reindex(index=nix, copy=False)
  return df.reset_index().drop('index',1)


class StyleVocab(object):
  
  def __init__(self, style_id=None, vectorizer=None):
    self.style_id = style_id
    self.vectorizer = vectorizer
    self.reviews = pd.DataFrame()

  def load_reviews(self, limit = 0):
    styles = Styles()
    dt = styles.beer_reviews(self.style_id, limit)
    self.reviews = pd.DataFrame.from_records((r for r in dt),
      columns=['style_id','beer_id','review'])
      
    return self.reviews

  def rollup_reviews(self, rev_rollup_ct = 10):
    r = shuffle_ix(self.reviews)
    r['rev_doc'] = r.index % rev_rollup_ct
    r = r.groupby(['style_id', 'beer_id', 'rev_doc']).apply(lambda x: ' '.join(x['review']))
    
    self.reviews = r.reset_index()
    self.reviews.columns = ['style_id', 'beer_id', 'rev_doc', 'review']

    return self.reviews
    
  def fit(self, train_ix = None):
    train_ix = train_ix if train_ix is not None else self.reviews.index
    self.vectorizer.fit(self.reviews['review'].ix[train_ix])
    return self.vectorizer
    
  def feature_vals(self, by_import = True):
    v = self.vectorizer
    idf = v._tfidf.idf_
    w_lst = zip(v.get_feature_names(), idf)
    if by_import:
      w_lst.sort(key = lambda x: -x[1])
      
    return { w[0]: w[1] for w in w_lst }
    
    



def asyncable_style_voc(voc):
  
  voc.load_reviews(limit=3000)
  voc.rollup_reviews(rev_rollup_ct=5)
  voc.fit()
  return voc.feature_vals()
    
    
def vocab_by_style(vectorizer, style_ids = [], **kwargs):
  from multiprocessing import Pool
  
  if not style_ids:
    styles = Styles()
    style_ids = styles.get_all().keys()

  p = Pool(min(30,len(style_ids)))
  
#  s_l = lambda sy: get_style_vocab(sy, vectorizer)
#  result = p.map(s_l, style_ids)
  result = p.map(get_style_vocab,
    [StyleVocab(style_id=s, vectorizer=vectorizer)  for s in style_ids])
    
  return result
  
  
  
def dummy_test():
  from reviewvectorizer import ReviewTfidf
  
  vectorizer = ReviewTfidf(
    max_features=50,
    ngram_range=(1,2),
    min_df=0.05,
    max_df=0.8)
  
  voc = StyleVocab(style_id=140, vectorizer=vectorizer)
  
  raw = voc.load_reviews(limit=300)
  print len(raw.index)
  print raw[:1]
  
  rollup = voc.rollup_reviews(rev_rollup_ct=5)
  print len(rollup.index)
  print rollup[:5]

  voc.fit()
  for k, v in voc.feature_vals().iteritems():
    print '{0}\t{1}'.format(k, v)
  
  
  

# test vocab by style builder
if __name__ == "__main__":
  from reviewvectorizer import ReviewTfidf

    
  res = vocab_by_style(
    ReviewTfidf(
      max_features=50,
      ngram_range=(1,2),
      min_df=0.05,
      max_df=0.8),
    [140, 84])
    
  for p in res:
    print type(p), len(p)