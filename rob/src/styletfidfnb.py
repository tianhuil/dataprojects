
import numpy as np
import pandas as pd

from sklearn.base import BaseEstimator
from sklearn.naive_bayes import MultinomialNB

from reviewvectorizer import ReviewTfidf, nonnum_stem_tokenizer

# worker func that takes a tuple of
# (vectorizer, num of reviews to use, num of rolled up review docs)
def _asyncable_style_voc(tup):
  
  # unpack vectorizer and documents
  s_id, vec, data = tup
  print 'START: vectorize style %s' % s_id
  # fit vectorizer
  vec.fit(data)
  print 'END: vectorize style %s' % s_id
  # get tup ( s, vec )
  return (s_id, vec)


class StyleTfidfNB(BaseEstimator):
  
  def __init__(self,
        max_features=None,
        ngram_range=(1,1),
        min_df=0.00,
        max_df=1.0,
        tokenizer=nonnum_stem_tokenizer,
        stop_words=[],
        use_idf = True,
        sublinear_tf = False,
        binary=False,
        vocabulary=None):
    
    self.max_features = max_features
    self.ngram_range = ngram_range
    self.min_df = min_df
    self.max_df = max_df
    self.tokenizer = tokenizer
    self.stop_words = stop_words
    self.use_idf = use_idf
    self.sublinear_tf = sublinear_tf
    self.binary=binary
    self.vocabulary=vocabulary
    
    # intermediate models
    self.style_vectorizers = { }
    self.extracted_vocabulary = None
    self.reviews_vectorizer = None
    self.style_nb_clf = None
  
  def __get_vectorizer(self,vocab=None):
    return ReviewTfidf(
      max_features=self.max_features,
      ngram_range=self.ngram_range,
      min_df=self.min_df,
      max_df=self.max_df,
      tokenizer=self.tokenizer,
      stop_words=self.stop_words,
      use_idf=self.use_idf,
      sublinear_tf=self.sublinear_tf,
      binary=self.binary,
      vocabulary=vocab)
          
  def fit(self, X, y):
    
    # extract styles in set
    print 'extract styles'
    sy_ids = np.unique(y)
    print 'style ids ', sy_ids
    
    # if no vocab provided, extract by style
    
    if self.vocabulary is None or not self.vocabulary:
      print 'no given vocab. extracting from style specific reviews'
      from multiprocessing import Pool
      
      # reviews for a given style id
      sy_dat = lambda s: X[ y == s ]
      
      p = Pool(min(30,len(sy_ids)))
      print 'START WORKER POOL'
      # for each style run tfidf
      # pool returns [ { word: idf }, ..., { word: idf } ]
      sy_vecs = p.map(_asyncable_style_voc,
                [(s, self.__get_vectorizer(), sy_dat(s)) for s in sy_ids])
      print 'DONE WORKER POOL'
      self.style_vectorizers = { syv[0]: syv[1] for syv in sy_vecs }
      print 'extract vocabulary'
      # build merged dictionary
#      print self.style_vectorizers[84].feature_vals().keys()
      all_w = ( fv for s,v in self.style_vectorizers.iteritems() for fv in v.feature_vals().keys() )
      self.extracted_vocabulary = np.unique( all_w )
      print 'vocab size %s' % len(self.extracted_vocabulary)
      use_voc = self.extracted_vocabulary
    else:
      use_voc = self.vocabulary
    print 'vectorize full corpus'
    # fit_and_transform on full corpus
    self.reviews_vectorizer = self.__get_vectorizer(use_voc)
    x_t = self.reviews_vectorizer.fit_transform(X)
    print 'fit classifier'
    # fit NB to f_and_t result
    self.style_nb_clf = MultinomialNB()
    self.style_nb_clf.fit(x_t, y)
    print 'DONE FIT'
    return self
    
  def predict(self, X):
    # transform corpora
    x_t = self.reviews_vectorizer.transform(X)
    
    # pass transformed data to nb for prediction
    return self.style_nb_clf.predict(x_t)


if __name__ == "__main__":
  
  from db.styles import Styles
  from db.basewordcts import BaseWordFreq
  from sklearn import cross_validation as c_v
  from sklearn.metrics import confusion_matrix
  
  print 'Load baseline stop words'
  baseline = BaseWordFreq()
  baseline.load_all()
  
  print 'Get reviews by style'
  styles = Styles()
  
  # get top n styles by review count
  sty_ids = styles.review_counts(5).keys()
  X = styles.beer_reviews_rollup(sty_ids, limit=0)
  print 'Styles Retrieved: %s' % len(np.unique(X['style_id'].values))
  print 'Beers Retrieved : %s' % len(np.unique(X['beer_id'].values))
  print 'Total Rev Docs  : %s' % len(X.index)

  X_train, X_test, y_train, y_test = c_v.train_test_split(
    X['review'], X['style_id'], test_size=0.2, random_state=0)

  clf = StyleTfidfNB(
          max_features=None,
          ngram_range=(1,2),
          min_df=0.05,
          max_df=0.8,
          stop_words=baseline.keys())
          
  clf.fit(X_train, y_train)
  y_pred = clf.predict(X_test)
  
  
  print confusion_matrix(y_test, y_pred)