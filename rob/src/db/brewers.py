

from tableacc import TableAcc

class Brewers(TableAcc):
  
  def __init__(self):
    
    super(Brewers, self).__init__(
      table_name='brewers',
      cols=['id', 'name', 'location_id'],
      upsert_proc='brewerupsert')

  def bylocation_id(self, location_id, order_by=""):
    return self._select(
      cols=["id", "name"],
      where="location_id = %s",
      order_by=order_by,
      param=[location_id] )
      
  def has_recommended_beers_by_loc(self, location_id, order_by=""):
    return self._view(view_name='brewerswithrecs',
      where="location_id = %s",
      order_by=order_by,
      param=[location_id])
      
      

if __name__ == "__main__":
  br = Brewers()
  for r in br.has_recommended_beers_by_loc(15):
    print r
      