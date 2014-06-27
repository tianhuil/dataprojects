

# access to db table containing review vocabulary features
# vocab indexed by style

from tableacc import TableAcc

class ReviewFeatures(TableAcc):
  
  def __init__(self):
    self.vocabulary = []
    
    super(FeatureVocab, self).__init__(
      table_name='reviewfeatures',
      cols=['style_id', 'feature'],
      'featureupsert')
   
  
  def style_feat_dict(self):
    out = { }
    for r in self.load_all():
      try:
        out[r[0]].append(r[1])
      except:
        out[r[0]] = [r[1]]
        
    return out
        
  def unique_feat(self):
    res = []
    rs = self._select(cols=["distinct", "feature"])
    if rs is not None:
      res.extend(rs)
      
    return res
          
      
  def add_feature(self, style_id, feature):
    # strip and check encoding
    feature = feature.strip().replace('\n','')
    if word != self._enc(word):
      raise ValueError('Bad word encoding')
      
    return self.add_record((style_id, feature))
    


# when run from command line, populate table
if __name__ == "__main__":
  def reload_and_populate():
    pass
  
  
  
  # start main
  while (True):
    inp = raw_input("Are you sure you want to overwrite beerad.reviewfeatures? [y/n] ")
    inp = inp.strip().lower()
    if inp == 'n':
      break
    elif inp == 'y':
      reload_and_populate()
      break


