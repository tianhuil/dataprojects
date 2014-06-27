

# access to db table containing review vocabulary features
# vocab indexed by style
# cli: as always, run from root folder, i.e. project folder containing src

from tableacc import TableAcc

class ReviewFeatures(TableAcc):
  
  def __init__(self):
    
    super(ReviewFeatures, self).__init__(
      table_name='reviewfeatures',
      cols=['style_id', 'feature'],
      upsert_proc='featureupsert')
   
  
  def style_ids(self):
    res = self._select(
      distinct=True,
      cols=["style_id"])
      
    if res is not None:
      res = list(r[0] for r in res)
      
    return res
  
  def style_feat_dict(self):
    out = { }
    for r in self.load_all():
      try:
        out[r[0]].append(r[1])
      except:
        out[r[0]] = [r[1]]
        
    return out
        
  def unique_feat(self, limit=0):
    res = []
    rs = self._select(distinct=True, cols=["feature"], limit=0)
    if rs is not None:
      res.extend(r[0] for r in rs)
      
    return res
          
      
  def add_feature(self, style_id, feature):
    # strip and check encoding
    feature = feature.strip().replace('\n','')
    if feature != self._enc(feature):
      raise ValueError('Bad feature encoding')
      
    return self.add_record((style_id, feature))
    


# when run from command line, populate table
if __name__ == "__main__":
  def reload_and_populate():
    # read feature csv
    print 'Loading vocab_by_style.csv'
    with open('src/vocab/vocab_by_style.csv','r') as file:
      rows = []
      for f in file:
        try:
          s_id, feat = f.split(',')
          s_id = int(s_id)
          rows.append((s_id, feat.strip()))
        except:
          print 'Error on ', f
    
    print 'Committing to db'
    # commit to db
    rf = ReviewFeatures()
    rf.add_many(rows)
    
    print 'Features Added: %s' % rf.row_count()
    print 'Done'
  
  # start main
  while (True):
    inp = raw_input("Are you sure you want to overwrite beerad.reviewfeatures? [y/n] ")
    inp = inp.strip().lower()
    if inp == 'n':
      break
    elif inp == 'y':
      reload_and_populate()
      break


