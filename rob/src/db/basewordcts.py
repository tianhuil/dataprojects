

# create a baseline word frequency distribution
# if run from command line the word counts will
# be recomputed from nltk and commited to databse.
# as a lib it is a wrapper around the basewordcts table
# the base word counts come from the brown corpora
# time magazine reviews and the nltk movie_reviews
# will be used as a reference point for 'normal' word
# frequencies in reviews of non-beer types

from beeradcn import Beerad

# import corpora from nltk
import nltk
from nltk.corpus import brown
from nltk.corpus import movie_reviews

class BaseWordFreq(object):
  
  def __init__(self):
    self.word_counts = { }
    
  def __iter__(self):
    for k, v in self.word_counts.iteritems():
      yield k, v
   
  def __enc(self, s):
    return ''.join([x for x in s if ord(x) < 128])
   
  def __select(self, where = "", limit = 0, param = []):
    sel = ["select word, count from basewordcts"]
    
    if where != "":
      sel.append("where")
      sel.append(where)
      
    if limit:
      sel.append('limit %s')
      param.append(limit)
    
    if param and len(param) == 1:
      param = (param[0],)
    else:
      param = tuple(param)
    
    res = None
    sel = ' '.join(s for s in sel)
    with Beerad() as dbc:
      cur = dbc.cursor()
      cur.execute(sel, param)
      res = cur.fetchall()
      cur.close()
      
    return res
  
  def __upsert(self, word, count):
    res = None
    with Beerad() as dbc:
      cur = dbc.cursor()
      cur.callproc("wordupsert", (word, count))
      res = cur.fetchone()
      
      dbc.commit()
      cur.close()
      
    return res
        
        
  def load_all(self):
    self.word_counts = { }
    
    wcs = self.__select()
    if wcs is not None:
      for r in wcs:
        self.word_counts[r[0]] = r[1]
      
    return self.word_counts
          
          
  def count(self, word):
    wc = self.__select('word = %s', 1, [word])
    if wc is not None:
      return wc[0][1]
    else:
      return 0
      
  def add_word(self, word, count):
    # strip and check encoding
    word = word.strip().replace('\n','')
    if word != self.__enc(word):
      raise ValueError('Bad word encoding')
      
    return self.__upsert(word, count)
    
  def remove_all(self):
    with Beerad() as dbc:
      cur = dbc.cursor()
      cur.execute("truncate table basewordcts")
      dbc.commit()
      cur.close()
      
    self.word_counts = { }
      
  def add_many(self, word_counts):
    res = None
    with Beerad() as dbc:
      cur = dbc.cursor()
      cur.executemany("call wordupsert(%s,%s)", word_counts)
      res = cur.fetchone()
      
      dbc.commit()
      cur.close()
    
      
  def iteritems(self):
    return self.word_counts.iteritems()
    
  def keys(self):
    return self.word_counts.keys()
    
    
    
# populate basewordcts table in beerad
def reload_and_populate():
  # loader function; put all base corpora here
  def load_nltk():
    fd = nltk.FreqDist(w.lower() for w in brown.words(categories='reviews'))
    fd.update(w.lower() for w in movie_reviews.words(categories='pos'))
    fd.update(w.lower() for w in movie_reviews.words(categories='neg'))
    
    return fd
  
  try:
    fd = load_nltk()
    wcdb = BaseWordFreq()
    wcdb.remove_all()
    wcdb.add_many([(w,c)for w, c in fd.iteritems()])
  except Exception as e:
    print "Error processing and saving word counts", e


# when run from command line, populate table
if __name__ == "__main__":
  while (True):
    inp = raw_input("Are you sure you want to overwrite beerad.basewordcts? [y/n] ")
    inp = inp.strip().lower()
    if inp == 'n':
      break
    elif inp == 'y':
      reload_and_populate()
      
      break