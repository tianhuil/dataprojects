
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

print 'Total Baseline Features : %s' % len(bct.get_feature_names())
n = sum(base_voc.values())
print 'Total Counts            : %s' % n
base_freq = { k: v/float(n) for k,v in base_voc.iteritems() }

rv = { }
with open('src/vocab/s-116-r-1.txt') as vo:
  for r in vo:
    r = r.split(',')
    rv[r[0]] = float(r[1])


n_rv = sum(base_voc.values())
rv_freq = { k: v/float(n_rv) for k,v in rv.iteritems() }

print 'Total Review Features   : %s' % len(rv)
print 'Total Review Counts     : %s' % sum(rv.values())
print 'Num in common           : %s' % sum(1 for k,_ in rv_freq.iteritems() if k in base_freq)

pos_dev = 0
with open('src/vocab/s-116-r-1-dev.txt','w') as out, \
  open('src/vocab/s-116-r-1-dev-no.txt','w') as out2:
  for k,v in rv_freq.iteritems():
    if k in base_freq:
      if v > base_freq[k]:
        pos_dev += 1
        out.write(k + ' POS \n')
      else:
        out2.write('{0}, {1}, {2}\n'.format(k,v,base_freq[k]))
    else:
      out.write(k + ' SOLO \n')
      
print 'More freq rev words     : %s' % pos_dev