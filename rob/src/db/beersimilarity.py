

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


def __asyncable_similarity(tup):
  from datetime import datetime as dt
  
#  bs, beer_id_ref, ref_vect, s_ids, b_ids, X_t, top = tup
  
  # bs: beer similarity object for db commit
  # ref_vects from one style
  # ref_b_ids: beer ids for ref vecs
  # s_ids, b_ids: style and beer indices of X_t
  # X_t for beers in other styles to be compared to
  # keep top similarities by style
  bs, b_refs, X_t_ref, b_comps, X_t_comp, top = tup

  start = dt.now()
  print 'Beers %s vs %s: Compute Similarity' % (b_refs.values.ravel(),b_comps.values.ravel())
  try:
    for i in xrange(len(b_refs)):
      
      # compute similarity between beer_ref[i] and all b_comps
      lk = linear_kernel(X_t_ref.getrow(i), X_t_comp).flatten()
      
      # take #top of largest similarities
      n = len(lk)
      kp = min(top, n)
      m_ixs = lk.argsort()[-kp:]
      
      sims = [ (b_refs.values[i], b_comps.values[j], lk[j]) for j in m_ixs ]
      bs.smooth_similarity(sims)
    
    print 'Comparison Complete: %s' % (dt.now() - start)
    return (b_refs, None)
  except Exception as e:
    return (b_refs, e)
      

def __asyncable_transform(tup):
  
  vectorizer, style_id, X = tup
  
  return {
    'style_id': style_id,
    'beer_ids': X['beer_id'].values,
    'X_t': vectorizer.transform(X['review'])
  }


if __name__ == "__main__":
  import pickle
  import numpy as np
  import pandas as pd
  from multiprocessing import Pool
  from datetime import datetime as dt

  # get access to custom vectorizer
  import sys
  sys.path.append('src/')
  
  from reviewvectorizer import ReviewTfidf
  from styles import Styles
  from basewordcts import expanded_stop_words
  from reviewfeatures import ReviewFeatures
  
  # same as cosine_similarity for normalized vectors
  from sklearn.metrics.pairwise import linear_kernel
  
  
  # pickling helper funcs
  def pkl_l(src):
    with open(src, 'rb') as f:
      res = pickle.loads(f.read())
    return res
  
  def pkl_d(obj, dest):
    with open(dest, 'wb') as f:
      pickle.dump(obj,  f)
  
  # loading/building vectorizer
  def load_vec(vec_pkl):
    # load features from db
    print 'Loading features'
    feat = ReviewFeatures()
      
    try:
      # load pickled vectorizer if available
      return True, pkl_l(vec_pkl), feat.style_ids()
    except Exception as e:
      print "Pickled vectorizer not found."
      print "Must run styletfidfnb.py to build model"
      
      # vectorize full review set with vocab
      return False, ReviewTfidf(
          ngram_range=(1,2),
          min_df=0.05,
          max_df=0.8,
          stop_words=expanded_stop_words(),
          vocabulary=feat.unique_feat()), feat.style_ids()
  
  
  def recompute_and_populate():
    """
      - get unique feature list
      - load reviews for all styles with features in db
      - vectorize and transform docs
      - compute cosine similarity for all vector pairs
      - there will be rev_rollup_ct worth of duplicates
      - take average of similarity between two beers (need something better)
    """
    
    vec_pkl = "src/vocab/review_vectorizer.p"
    was_pkl, vec, style_ids = load_vec(vec_pkl)
    
    # load data for styles with feature sets
#    X = styles.beer_reviews_rollup(style_ids, limit=0)
    # overridden until full feature table is populated
    styles = Styles()
    top_sy = [159, 84, 157, 56, 58, 9, 128, 97, 116, 140]
    print 'Comparing the top %s styles: %s' % (len(top_sy), ', '.join(str(s) for s in top_sy))
    X = styles.beer_reviews_rollup(top_sy, limit=1000, rev_rollup_ct=1, shuffle=False)
    
    if was_pkl:
      print "Loaded pickled vectorizer."
      print "Feature count: %s" % len(vec.get_feature_names())
      print "Transforming reviews"
      start = dt.now()
      X_t = vec.transform(X['review'])
      print "Transform time %s" % (dt.now()-start)
    else:
      print "Recomputing fit"
      start = dt.now()
      X_t = vec.fit_transform(X['review'])
      print "Transform time %s" % (dt.now()-start)
      print 'Vectorizing: Done'
      print "Pickling vectorizer"
      pkl_d(vec, vec_pkl)
        
    print 'Truncating similarity table'
    bs = BeerSimilarity()
    bs.remove_all()
    
    print 'Computing similarities and saving to db %s' % X_t.shape[0]
    print 'Nonzero elements %s' % len(X_t.data)
    
    # set style RU
    # will account for symmetry in the database
    ru_sids = [ (top_sy[i], top_sy[j]) for i in xrange(len(top_sy)) for j in xrange(i+1,len(top_sy)) ]
    
    pool_inp = []
    for ruc in ru_sids:
      indices = np.where(X['style_id'].values == ruc[0])[0]
      X_t_ref = X_t.tocsr()[indices,]
      b_id_ref = X['beer_id'].ix[indices,]
      
      indices = np.where(X['style_id'].values == ruc[1])[0]
      X_t_comp = X_t.tocsr()[indices,:]
      b_id_comp = X['beer_id'].ix[indices,]
      
      pool_inp.append((bs, b_id_ref, X_t_ref, b_id_comp, X_t_comp, 100))
      
    p = Pool(min(10,len(top_sy)))
    b_id_res = p.map(__asyncable_similarity, pool_inp)
            
    for res in b_id_res:
      if res[1] is not None:
        print '%s %s' % (', '.join(str(r) for r in res[0].values.ravel()), res[1])
    
    
  
  # start main
  while (True):
    inp = 'y' #raw_input("Are you sure you want to overwrite beerad.beersimilarity? [y/n] ")
    inp = inp.strip().lower()
    if inp == 'n':
      break
    elif inp == 'y':
      recompute_and_populate()
      break