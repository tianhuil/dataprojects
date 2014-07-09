

from tableacc import TableAcc

class Beers(TableAcc):
  
  def __init__(self):
    
    super(Beers, self).__init__(
      table_name='beers',
      cols=['id', 'name', 'location_id'],
      upsert_proc='brewerupsert')

  def bylocation_id(self, location_id):
    return self._select(
      cols=["id", "name"],
      where="location_id = %s",
      param=(location_id,) )
      
  def has_rec_by_brewer(self, brewer_id):
    return self._exec_proc(proc='beerswithrecs',
      inputs=(brewer_id,))
      
  def recommendations(self, beer_id, style_id, limit):
    return self._exec_proc(proc='similarbeersbystyle',
      inputs=(beer_id, style_id, limit))
      
  def meta_dict(self, beer_id):
    res = self._exec_proc(proc='beermeta', inputs=[beer_id])
    if res is not None:
      new_cols = [
        'beer_id','name','brewer_id','brewer_name','location_id',
        'location_name','style_id','style_name','abv','ibu','notes']
      
      return { new_cols[i]: v for i,v in enumerate(list(res[0])) }
      
    return res

if __name__ == "__main__":
  br = Beers()
  
  # Victory beers with recommendations
  for r in br.has_rec_by_brewer(345):
    print r
      
  # Pale Ale recommendations for fans of Victory Headwaters
  for r in br.recommendations(66281,97,5):
    print r
    
  for k,v in br.meta_dict(345).iteritems():
    print k,v