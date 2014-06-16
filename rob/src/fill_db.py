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
            
        v = (br["id"], enc(br["name"]), br["location"])
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
      
      v = (s["id"],s["name"])
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


#ct = 0
#ct_s = 0
#print 'FILL PRODUCT IDS'
#with open(pth('product_ids.json'), 'r') as prods, \
#    open(pth('dberr_prodid.txt'), 'w') as err:
#  prs = json.loads(prods.read())
  
#  for brewer, beers in prs.iteritems():
#    for beer in beers:
#      ct += 1
#      ins = """
#        insert into product_ids (brewer_id, beer_id)
#        values (%s, %s)"""
      
#      v = (brewer, beer)
#      ct_s += insert(cur, ins, v, err)

#print 'FILLED PRODUCT IDS: {0} of {1}\n'.format(ct_s, ct)



def fill_users(cur):
  ct_s, ct = 0, 0
  with open(pth('users.json')) as user_f, \
      open(pth('dberr_prodid.txt'), 'w') as err:
  
    for u_j in user_f:
      ct += 1
      u = json.loads(u_j)
      ins = '''
        insert into users (id, name, title, location, sex)
        values ( %s, %s, %s, %s, %s )'''
          
      v = (u["id"], u["name"], u["title"], u["location"], u["sex"])
      ct_s += insert(cur, ins, v, err)

  return ct_s, ct




# reviews only come with user_name
# temp table to convert into proper review format
def fill_revs(cur):
  
  from datetime import datetime as dt
  
  ct_s, ct = 0, 0
  with open(pth('beeradvocate.json'), 'r') as revs, \
      open(pth('dberr_revs.txt'), 'w') as err:
    
    for rev in revs:
      ct += 1
      r = json.loads(rev)
      
      bd = r["beer"]
      rv = r["review"]
      
      v = (-1)
      try:
        # first get user id
        sel = """select id from users where name = %s"""
        cur.execute(sel, (rv["user_name"],))
        u_id = int(cur.fetchone()[0])
        
        ins = """
          insert into reviews ( brewer_id, beer_id, user_id, rev_date,
                      palate, taste, aroma, appearance, overall, review )
          values (%s, %s, %s, from_unixtime(%s), %s, %s, %s, %s, %s, %s) """
        
        v = ( bd["brewer_id"], bd["id"], u_id, int(rv["date"]), rv["palate"],
              rv["taste"], rv["aroma"], rv["appearance"], rv["overall"], rv["review"] )
              
        ct_s += insert(cur, ins, v, err)
      except Exception as e:
        err.write("{0}:{1}\n".format(v, e))
    
  return ct_s, ct




with Beerad() as con:
  cur = con.cursor()

  l = lambda f: f(cur)

  print_res('BREWERS', l(fill_brewers))
  print_res('STYLES', l(fill_styles))
  print_res('BEERS', l(fill_beers))
  print_res('USERS', l(fill_users))
  print_res('REVIEWS', l(fill_revs))
  
  con.commit()
  cur.close()
