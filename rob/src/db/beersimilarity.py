

# access to the beer similarity table
# cli: truncate beersimilarity, load unique feature set
# and recompute all beer similarities

from tableacc import TableAcc

class BeerSimilarity(TableAcc):
  
  def __init__(self):
    
    super(BeerSimilarity, self).__init__(
      table_name='beersimilarity',
      cols=['beer_id_ref', 'beer_id_comp', 'similarity'],
      upsert_proc='featureupsert')

  def similarity(self, beer_id_ref, beer_id_comp):
    return self._select(
      cols=["similarity"],
      where="beer_id_ref = %s and beer_id_comp = %s",
      params=(beer_id_ref,beer_id_comp) )

  def similar_beers(self, beer_id, ordered=True, top=0):
    return self._select(
      cols=["beer_id_comp","similarity"],
      where="beer_id_ref = %s",
      order_by="similarity desc",
      limit=top,
      params=(beer_id,) )
      
  def smooth_similarity(self, similarity_records):
    self._exec_many_procs("similaritysmooth", similarity_records)
      

if __name__ == "__main__":
  import numpy as np
  import pandas as pd

  # get access to custom vectorizer
  import sys
  sys.path.append('src/')
  
  from reviewvectorizer import ReviewTfidf
  from styles import Styles
  from basewordcts import expanded_stop_words
  from reviewfeatures import ReviewFeatures
  
  # same as cosine_similarity for normalized vectors
  from sklearn.metrics.pairwise import linear_kernel
  
  
  def recompute_and_populate():
    """
      - get unique feature list
      - load reviews for all styles with features in db
      - vectorize and transform docs
      - compute cosine similarity for all vector pairs
      - there will be rev_rollup_ct worth of duplicates
      - take average of similarity between two beers (need something better)
    """
    
    # load features from file or db
    print 'Loading styles with features and associated review docs'
    feat = ReviewFeatures()
    
    # load data for styles with feature sets
#    X = styles.beer_reviews_rollup(feat.style_ids(), limit=0)
    # overridden until full feature table is populated
    styles = Styles()
    X = styles.beer_reviews_rollup([159, 84, 157, 56, 58, 9, 128, 97, 116, 140], limit=0)
    
    # vectorize full review set with vocab
    vec = ReviewTfidf(
      ngram_range=(1,2),
      min_df=0.05,
      max_df=0.8,
      stop_words=expanded_stop_words(),
      vocabulary=feat.unique_feat())
      
    print 'Vectorizing: Start'
    # vectorize reviews
    X_t = vec.fit_transform(X['review'])
    print 'Vectorizing: Done'
    
    print 'Truncating similarity table'
    bs = BeerSimilarity()
    bs.remove_all()
    
    print 'Computing similarities and saving to db %s' % X_t.shape[0]
    print 'Nonzero elements %s' % len(X_t.data)
    for i in xrange(X_t.shape[0]):
      print 'iter %s' % i
      r = X_t[i].toarray().flatten()
      lk = linear_kernel(r, X_t).flatten()
      
      print 'Beer id %s' % X.ix[i,]['beer_id']
      be_id_ref = X.ix[i,]['beer_id']
      print 'building input records'
      sims = [ (be_id_ref, X.ix[j,]['beer_id'], lk[j]) for j in xrange(1,len(lk)) if be_id_ref != X.ix[j,]['beer_id']  ]
      print 'saving to db'
      bs.smooth_similarity(sims)
      print 'saved'
    
    
  
  # start main
  while (True):
    inp = raw_input("Are you sure you want to overwrite beerad.beersimilarity? [y/n] ")
    inp = inp.strip().lower()
    if inp == 'n':
      break
    elif inp == 'y':
      recompute_and_populate()
      break