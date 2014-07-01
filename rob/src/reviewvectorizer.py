
# TF-IDF vectorizer child created solely to avoid
# repetitively defining the stemmer and tokenizer defaults

import re
import nltk.tokenize
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer


default_tokenizer = TfidfVectorizer().build_tokenizer()
stemmer = nltk.stem.SnowballStemmer("english", ignore_stopwords=True)

# standard nltk stop words plus some common useless words
base_stop_words = nltk.corpus.stopwords.words('english') + \
  [
    'ever','sure','want','review','got','somewhat','along',
    'see','know','something','beer'
  ]
  

def nonnum_stem_tokenizer(text):
    """
    use the default tokenizer from TfidfVectorizer, combined with the nltk SnowballStemmer.
    """
    def non_num_tokenizer(text):
      return default_tokenizer(re.sub(r'\d', '', text))

    return map(stemmer.stem, non_num_tokenizer(text))

class ReviewTfidf(TfidfVectorizer):
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
        vocabulary=None,
        **kwargs):
    
    # standard nltk stop words plus some common useless words
    stop_words.extend(base_stop_words)
        
    super(ReviewTfidf, self).__init__(
      max_features=max_features,
      ngram_range=ngram_range,
      min_df=min_df,
      max_df=max_df,
      tokenizer=tokenizer,
      stop_words=map(stemmer.stem, stop_words),
      use_idf = use_idf,
      sublinear_tf = sublinear_tf,
      binary=binary,
      vocabulary=vocabulary,
      **kwargs)
      
      
  def feature_vals(self):
    idf = self._tfidf.idf_
    w_lst = zip(self.get_feature_names(), idf)
        
    return { w[0]: w[1] for w in w_lst }
      

# count vectorizer
class ReviewCountVec(CountVectorizer):
  
  def __init__(self,
        max_features=None,
        ngram_range=(1,1),
        tokenizer=nonnum_stem_tokenizer,
        stop_words=[],
        binary=False,
        vocabulary=None):
    
    # standard nltk stop words plus some common useless words
    stop_words.extend(base_stop_words)
    
    super(ReviewCountVec, self).__init__(
      max_features=max_features,
      ngram_range=ngram_range,
      tokenizer=tokenizer,
      stop_words=map(stemmer.stem, stop_words),
      binary=binary,
      vocabulary=vocabulary)

