
import numpy as np
import pandas as pd


from reviewvectorizer import ReviewTfidf
from db.styles import Styles
from db.basewordcts import expanded_stop_words

# load vocab from file or db
vocab = []

# retrieve all style ids
styles = Styles()
sty_ids = styles.get_all().keys()

# pull full user review set at default (10) rollup
X = styles.beer_reviews_rollup([97,116], limit=1000)

# vectorize full review set with vocab
vec = ReviewTfidf(max_features=25,
    ngram_range=(1,2),
    min_df=0.01,
    max_df=0.8,
    stop_words=expanded_stop_words(),
    vocabulary=None)
print X
X_t = vec.fit_transform(X['review'])

# same as cosine_similarity for normalized vectors
from sklearn.metrics.pairwise import linear_kernel

n_top = 5
for i in xrange(X_t.shape[0]):
  lk = linear_kernel(X_t[i].toarray())
  # sort indices by similarity descending
  ix = lk.argsort()[::-1]
  
  # get beer_id for n_top most similar
  # exclude first, i.e. similar with itself
  ix = ix[1:(n_top+1)]
  print X[i]['beer_id'], " top 5 ", X[ix]['beer_id']
  
  # save all but first element
  