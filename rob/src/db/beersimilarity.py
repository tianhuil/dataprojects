

# access to the beer similarity table
# cli: truncate beersimilarity, load unique feature set
# and recompute all beer similarities

from datetime import datetime as dt

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
  
#  bs, beer_id_ref, ref_vect, s_ids, b_ids, X_t, top = tup
  
  # bs: beer similarity object for db commit
  # ref_vects from one style
  # ref_b_ids: beer ids for ref vecs
  # s_ids, b_ids: style and beer indices of X_t
  # X_t for beers in other styles to be compared to
  # keep top similarities by style
  bs, b_refs, X_t_ref, b_comps, X_t_comp, top = tup

  start = dt.now()
  print 'Beers %s vs %s: Compute Similarity' % (b_refs,b_comps)
  try:
    for i in xrange(len(b_refs)):
      
      # compute similarity between beer_ref[i] and all b_comps
      lk = linear_kernel(X_t_ref.getrow(i), X_t_comp).flatten()
      
      # take #top of largest similarities
      n = len(lk)
      kp = min(top, n)
      m_ixs = lk.argsort()[-kp:]
      
      sims = [ (b_refs[i], b_comps[j], lk[j]) for j in m_ixs ]
      bs.smooth_similarity(sims)
    
    print 'Comparison Complete: %s' % (dt.now() - start)
    return (b_refs, None)
  except Exception as e:
    return (b_refs, e)
      

def __asyncable_transform(tup):
  
  vectorizer, style_id, X = tup
  
  print 'Vectorize %s: start' % style_id
  start = dt.now()
  X_t = vectorizer.transform(X['review'])
  print 'Vectorize %s: done %s' % (style_id, (dt.now()-start))
  
  return (style_id, X['beer_id'].values, X_t)


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
  
  
  # pickling helper func
  def pkl_l(src):
    with open(src, 'rb') as f:
      res = pickle.loads(f.read())
    return res
  
  # loading/building vectorizer
  def load_vec(vec_pkl):
    try:
      # load pickled vectorizer if available
      return True, pkl_l(vec_pkl)
    except Exception as e:
      print "Pickled vectorizer not found."
      print "Must run styletfidfnb.py to build model"
      
      return False, None
      
  
  def recompute_and_populate():
    """
      - load pickled vectorizer
      - transform docs
      - compute cosine similarity for all vector pairs
      - data is retrieved at rev_rollup_ct = 1 (beer level)
    """
    
    vec_pkl = "src/vocab/review_vectorizer.p"
    was_pkl, vec = load_vec(vec_pkl)
    
    # load data for styles with feature sets
    # overridden until full feature table is populated
    
    styles = Styles()
    top_sy = [159, 84, 157, 56, 58, 9, 128, 97, 116, 140]
    print 'Comparing the top %s styles: %s' % (len(top_sy), ', '.join(str(s) for s in top_sy))
    X = styles.beer_reviews_rollup(top_sy, limit=0, rev_rollup_ct=1, shuffle=False)
    
    if was_pkl:
      print "Loaded pickled vectorizer."
      print "Feature count: %s" % len(vec.get_feature_names())
      print "Transforming reviews"
      
      trans_pool = Pool(min(10,len(top_sy)))
      res_t = trans_pool.map(__asyncable_transform,
        [ (vec, sy, X[ X['style_id'] == sy ]) for sy in top_sy])
      
      # as style keyed dict
      res_t = {
        r[0]: {
          'beer_ids': r[1],
          'X_t': r[2]
          } for r in res_t
      }
      
    else:
      # exit program
      return 0
        
    print 'Truncating similarity table'
    bs = BeerSimilarity()
    bs.remove_all()
    
    dim1 = sum(v['X_t'].shape[0] for k,v in res_t.iteritems())
    dim2 = sum(len(v['X_t'].data) for k,v in res_t.iteritems())
    print 'Computing similarities and saving to db %s' % dim1
    print 'Nonzero elements %s' % dim2
    
    # set style RU
    # will account for symmetry in the database
    ru_sids = [ (top_sy[i], top_sy[j]) for i in xrange(len(top_sy)) for j in xrange(i+1,len(top_sy)) ]
    
    pool_inp = []
    for ruc in ru_sids:
      X_t_ref = res_t[ruc[0]]['X_t']
      b_id_ref = res_t[ruc[0]]['beer_ids']
      
      X_t_comp = res_t[ruc[1]]['X_t']
      b_id_comp = res_t[ruc[1]]['beer_ids']
      
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