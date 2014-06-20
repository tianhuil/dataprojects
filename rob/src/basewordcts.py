

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
   
  def __enc(self, s):
    return ''.join([x for x in s if ord(x) < 128])
   
  def __select(self, where = "", limit = 0):
    sel = ["select word, count from basewordcts"]
    
    if not where:
      sel.append(where)
      
    if limit:
      sel.append('limit %i' % limit)
    
    res = None
    sel = ' '.join(s for s in sel)
    with Beerad() as dbc:
      cur = dbc.cursor()
      if not cur.execute(sel):
        res = cur.fetchall()
        
    return res
  
  def __upsert(self, word, count):
    qry = """
      """
    
    res = None
    with Beerad() as dbc:
      cur = dbc.cursor()
      res = cur.execute(qry.replace('\n',''), (word, count, word, word, count))
        
    return res
        
        
  def load_all(self):
    self.word_counts = { }
    
    wcs = self.__select()
    if wcs is not None:
      self.word_counts[r[0]] = r[1]
      
    return self.word_counts
          
          
  def count(self, word):
    wc = self.__select('word = %s', 1)
    if wc is not None:
      return wc[1]
    else:
      return 0
      
  def add_word(self, word, count):
    # strip and check encoding
    word = word.strip().replace('\n','')
    if word != self.__enc(word):
      raise ValueError('Bad word encoding')
      
    return self.__upsert(word, count)
    
    
    
# populate basewordcts table in beerad
def reload_and_populate():
  # loader function; put all base corpora here
  def load_nltk():
    fd = nltk.FreqDist(w.lower() for w in brown.words(categories='reviews'))
    fd.update(w.lower() for w in movie_reviews.words(categories='pos'))
    fd.update(w.lower() for w in movie_reviews.words(categories='neg'))
    
    return fd
  
  # connect to database and save info
  with Beerad() as dbc:
    cur = dbc.cursor()
    
    try:
      cur.execute("truncate table basewordcts")
    except Exception as e:
      print 'Error clearing out basewordcts table', e
      
    word_list = [w.lower() for w in news_text]
    word_list.extend([w.lower() for w in good_movie_revs])
    word_list.extend([w.lower() for w in bad_movie_revs])
    
    qry = """
      insert into basewordcts (word, count)
      values (%s, %s) """
    
    try:
      fd = load_nltk()
      cur.executemany(qry, [(w,c)for w, c in fd])
    except Exception as e:
      print "Error processing and saving word counts", e
      
    dbc.commit()
    cur.close()


# when run from command line, populate table
if __name__ == "__main__":
  while (True):
    inp = raw_input("Are you sure you want to overwrite beerad.basewordcts? [y/n] ")
    inp = inp.strip().lower()
    if inp == 'n':
      break
    elif inp == 'y':
      #reload_and_populate()
      wc = BaseWordFreq()
      wc.add_word('word', 5)
      wc.add_word('homes', 7)
      
      print wc.count('word')
      
      wc.add_word('word', 2)
      print wc.count('word')
      
      for w,c in wc.load_all().iteritems():
        print w, c
      
      break