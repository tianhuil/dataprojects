

from tableacc import TableAcc

class Locations(TableAcc):
  
  def __init__(self):
    
    super(Locations, self).__init__(
      table_name='locations',
      cols=['id', 'name'],
      upsert_proc='locationupsert')

  def top_beer_ct(self, top):
    return self._view(view_name='beerctbyloc',
      cols=['location_id', 'name'],
      limit=top)
      
      

if __name__ == "__main__":
  l = Locations()
  
  for r in l.top_beer_ct(10):
    print r
      