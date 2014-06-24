
# compare beer review word frequency to
# movie/product review word frequency
# look for significant positive deviations

from basewordcts import BaseWordFreq
from reviewvectorizer import ReviewCountVec   # CountVectorizer w def stemmers etc


baseline = BaseWordFreq()
baseline.load_all()

# create baseline corpus
corpus = []
for w,c in baseline.iteritems():
  corpus.extend(c*[w])

# re-count words using default stemmer
# and base stop words list
bct = ReviewCountVec()
bct.fit(corpus)
base_voc = bct.vocabulary_

print 'Total Baseline Features: %s' % len(bct.get_feature_names())
n = sum(base_voc.values())
print 'Total Counts %s' % n
base_freq = { k: v/float(n) for k,v in base_voc }
