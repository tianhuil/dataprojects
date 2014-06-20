#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from beeradcn import Beerad


def pth(f):
  return 'data/' + f

# check for encoding errors in foreign beer names
# brute force appears to be all that's working
def enc(s):
  return ''.join([x for x in s if ord(x) < 128])

def insert(cur, ins, tup, err):
  succ = 1
  try:
    cur.execute(ins, tup)
  except Exception as e:
    err.write("{0}:{1}\n".format(tup, e))
    succ = 0
    
  return succ

def print_res(dt, f):
  print 'FILL ' + dt
  ct_s, ct = f()
  print 'FILLED {0}: {1} of {2}'.format(dt, ct_s, ct)



def fill_brewers(cur):
  ct, ct_s = 0, 0
  with open(pth('brewers.json'), 'r') as brs, \
      open(pth('dberr_brewers.txt'), 'w') as err:
    for br_j in brs:
      ct += 1
      try:
        br = json.loads(br_j)
        
        ins = """
          insert into brewers (id, name, location)
          values (%s, %s, %s)"""
            
        v = (br["id"], enc(br["name"]), enc(br["location"]))
        ct_s += insert(cur, ins, v, err)
          
      except:
        print "Failed to load: ", br
        
  return ct_s, ct
      


def fill_styles(cur):
  with open(pth('styles.json'), 'r') as st, \
      open(pth('dberr_styles.txt'), 'w') as err:
    
    ct, ct_s = 0, 0
    
    # fill style table
    for sty_j in st:
      ct += 1
      
      s = json.loads(sty_j)
      ins = """
        insert into styles (id, name)
        values (%s, %s)"""
      
      v = (s["id"], enc(s["name"]))
      ct_s += insert(cur, ins, v, err)
      
  return ct_s, ct



def fill_beers(cur):
  with open(pth('beers.json')) as bes, \
      open(pth('dberr_beers.txt'), 'w') as err:
        
    ct, ct_s = 0, 0
    
    for be_j in bes:
      ct += 1
      try:
        be = json.loads(be_j)
        
        ins = """
          insert into beers (id, brewer_id, name, style_id, date_add, ba_score, bros_score, abv, ibu, notes)
          values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        
        abv = be["abv"].replace('%', '')
        try:
          abv = float(abv) if abv != '' else 0
        except:
          abv = 0
          
        v = (be["beer_id"], be["brewer_id"], enc(be["name"]), be["style_num"], be["date_added"],
              be["ba_score"], be["bros_score"], abv, be["ibu"], enc(be["notes"]))
        ct_s += insert(cur, ins, v, err)
        
      except Exception as e:
        print "Failed to load: ", e, be
        
  return ct_s, ct



have_u_ids = False
u_ids = {}
max_id = 0
def fill_users(cur):
  global max_id
  ct_s, ct = 0, 0
  with open(pth('users.json')) as user_f, \
      open(pth('dberr_prodid.txt'), 'w') as err:
  
    for u_j in user_f:
      ct += 1
      u = json.loads(u_j)
      ins = '''
        insert into users (id, name, title, location, sex)
        values ( %s, %s, %s, %s, %s )'''
      
      u_ids[u["name"]] = u["id"]
      max_id = max(max_id, u["id"])
          
      v = (u["id"], u["name"], u["title"], enc(u["location"]), u["sex"])
      ct_s += insert(cur, ins, v, err)

    have_u_ids = True
  return ct_s, ct


  
  
  
def fill_revs(cur):
  
  from datetime import datetime as dt
  
  # reviews only come with user_name
  def get_uids():
    global max_id
    with open(pth('users.json'), 'r') as users:
      for u_j in users:
        u = json.loads(u_j)
        u_ids[u["name"]] = u["id"]
        max_id = max(max_id, u["id"])
  

  def subrevs(v):
    ins = """
        insert into reviews ( brewer_id, beer_id, user_id, rev_date,
                        palate, taste, aroma, appearance, overall, review )
        select %s, %s, %s, from_unixtime(%s), %s, %s, %s, %s, %s, %s
        from beers
        where brewer_id = %s and id = %s and
        not exists (
          select * from reviews
          where brewer_id = %s
            and beer_id = %s
            and user_id = %s )"""
            
    print "Inserting {0} reviews".format(len(v))
    print 'Starting batch insert'
    start = dt.now()
    cur.executemany(ins, v)
    print 'Review batch insert time: %s' % (dt.now() - start)

  if not have_u_ids:
    get_uids()
    
  print "Have ids"
  print "Building review set"
  
  ct_s, ct = 0, 0
  with open(pth('beeradvocate.json'), 'r') as revs, \
      open(pth('dberr_revs.txt'), 'w') as err, \
      open(pth('users.json'), 'a') as users:
    
    v = []
    add_ids = []
    e_ct = 0
    e_uct = []
    
    itct = 0
    # build query parameter lists
    for rev in revs:
      r = json.loads(rev)
      
      bd = r["beer"]
      rv = r["review"]
      
      if rv["user_name"] in u_ids:
        ct += 1
      else:
        e_ct += 1
        if rv["user_name"] not in e_uct:
          e_uct.append(rv["user_name"])
        
        name = rv["user_name"].strip()
        u_ids[name] = max_id
        
        new_u = {
          "id": max_id,
          "name": name,
          "title": "",
          "location": "",
          "sex": "Unspecified"
        }
        users.write(json.dumps(new_u) + "\n")
        add_ids.append( (new_u["id"], new_u["name"], new_u["title"], new_u["location"], new_u["sex"]) )
      
      # first get user id
      u_id = u_ids[rv["user_name"]]
      v.append( ( bd["brewer_id"], bd["id"], u_id, int(rv["date"]), rv["palate"],
            rv["taste"], rv["aroma"], rv["appearance"], rv["overall"], enc(rv["review"]),
            # extra parameters for conditional insert
            bd["brewer_id"], bd["id"], bd["brewer_id"], bd["id"], u_id ) )
              
      itct += 1
      if itct == 50000:
        try:
          subrevs(v)
          v = []
          itct = 0
        except Exception as e:
          print e
          err.write("{0}\n".format(e))
        
    # end for indent
      
    print "Found {0} reviews from {1} valid users".format(ct, len(u_ids.keys()))
    print "Backfilling users to include {0} reviews from {1} users".format(e_ct, len(e_uct))
    
    try:
      if len(add_ids):
        ins = '''
          insert into users (id, name, title, location, sex)
          values  (%s, %s, %s, %s, %s) '''
        cur.executemany(ins, add_ids)
          
        print "Users ({0}) backfilled".format(len(add_ids))
        
      print "Submitting remaining reviews"
      subrevs(v)
      
      cur.execute("""select count(*) from reviews""")
      ct_s = int(cur.fetchone()[0])
    except Exception as e:
      print e
      err.write("{0}\n".format(e))
    
  return ct_s, ct




with Beerad() as con:
  cur = con.cursor()

#  print_res('BREWERS', lambda: fill_brewers(cur))
#  print_res('STYLES', lambda: fill_styles(cur))
#  print_res('BEERS', lambda: fill_beers(cur))
#  print_res('USERS', lambda: fill_users(cur))
  
  print_res('REVIEWS', lambda: fill_revs(cur))
  
  con.commit()
  cur.close()
