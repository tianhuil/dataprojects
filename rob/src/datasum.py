
# generate some summary counts for the data that successfully made it into the db

from beeradcn import Beerad

def fetch_and_print(cur, qry, o):
  with open(o, 'w') as out:
    cur.execute(qry,())
    out.write(",".join(d[0] for d in cur.description))
    out.write(cur.fetchall() + "\n")


qry = []
# top 10 breweries by beer count
qry.append("""
  select br.name, count(be.id) as beer_ct
  from brewers br inner join beers be
    on br.id = be.brewer_id
  group by br.name
  order by beer_ct desc
  limit 10 """)
    
# top 10 beers by review count
qry.append("""
  select be.name, count(r.user_id) as review_ct
  from beers be inner join reviews r
    on be.id = r.beer_id
  group by be.name
  order by review_ct desc
  limit 10 """)
    
# number of beers with at least n reviews received
qry.append("""
  select type, count(review_ct) as reviews
  from
  (
    select '25+ Reviews' as type, count(r.user_id) as review_ct
    from beers be inner join reviews r
      on be.id = r.beer_id
    group by be.name
    having count(r.user_id) >= 25
  ) as tf union (
    select '50+ Reviews' as type, count(r.user_id) as review_ct
    from beers be inner join reviews r
      on be.id = r.beer_id
    group by be.name
    having count(r.user_id) >= 50
  ) as ff union (
    select '100+ Reviews' as type, count(r.user_id) as review_ct
    from beers be inner join reviews r
      on be.id = r.beer_id
    group by be.name
    having count(r.user_id) >= 100
  ) as hu
  group by type """)
  
# number of users with at least 10, 50, 100 reviews submitted
qry.append("""
  select type, count(r.beer_id) as reviews
  from
  (
    select '10+ Reviews' as type, count(r.beer_id) as review_ct
    from reviews r
    group by r.user_id
    having count(r.user_id) >= 10
  ) as tf union (
    select '25+ Reviews' as type, count(r.beer_id) as review_ct
    from reviews r
    group by r.user_id
    having count(r.user_id) >= 50
  ) as ff union (
    select '100+ Reviews' as type, count(r.beer_id) as review_ct
    from reviews r
    group by r.user_id
    having count(r.user_id) >= 100
  ) as hu
  group by type """)
  
# top 10 locations by count of users w at least 50 reviews
qry.append("""
  select u.location, count(u.id) as power_users
  from users u join on reviews r
    on u.id = r.user_id
  group by u.location
  having count(u.id) >= 50
  order by power_users desc
  limit 10 """)
    
# number of beers w valid abv and ibu data
qry.append("""
  select 'valid abv and ibu' as type, count(*)
  from beers be
  where abv > 0 and ibu > 0 """)

# create and open connection to beerad
with Beerad() as dbc:
  cur = dbc.cursor()
  for q in qry:
    fetch_and_print(cur, q, 'data/data_summ.txt')
      
  dbc.commit()
  cur.close()


