#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import MySQLdb as mdb

with open('creds.json') as c:
  creds = json.load(c)
  
con = mdb.connect(host='localhost', user=creds["uname"], passwd=creds["pwd"], db='beerad')
cur = con.cursor()

# check for encoding errors in foreign beer names
# brute force appears to be all that's working
def enc(s):
  return ''.join([x for x in s if ord(x) < 128])

with open('data/brewers.json', 'r') as brs:
  for br_j in brs:
    try:
      br = json.loads(br_j)
      
      ins = """
        insert into brewers (id, name, location)
        values (%s, %s, %s)"""
        
      try:
        cur.execute(ins, (br["id"], enc(br["name"]), br["location"]))
      except Exception as e:
        print e, br
    except:
      print "Failed to load: ", br

styles = { }
with open('data/beers.json') as bes:
  for be_j in bes:
    try:
      be = json.loads(be_j)
  
      # extract styles while parsing
      styles[be["style_num"]] = be["style"]
      
      ins = """
        insert into beers (brewer_id, id, name, style_id, ba_score, bros_score, abv, ibu, notes)
        values (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
      
      try:
        cur.execute(ins, (be["brewer_id"], be["beer_id"], enc(be["name"]), be["style_num"],
           be["ba_score"], be["bros_score"], be["abv"], be["ibu"], be["notes"]))
      except Exception as e:
        print e, be
    except:
      print "Failed to load: ", be
    
with open('data/styles.json', 'w') as st:
  # save local json copy
  st.write(json.dumps(styles))
  
  # fill style table
  for k,v in styles.iteritems():
    ins = """
      insert into styles (id, style)
      values (%s, %s)"""
    
    try:
      cur.execute(ins, (k,v))
    except Exception as e:
      print e, k, v
      

with open('data/users.json') as user_f:

  for u_j in user_f:
    u = json.loads(u_j)
    ins = '''
      insert into users (id, name, title, location, sex)
      values ( %s, %s, %s, %s, %s )'''
        
    try:
      cur.execute(ins, (u["id"], u["name"], u["title"], u["location"], u["sex"])))
    except Exception as e:
      print e

mdb.commit()
cur.close()
mdb.close()
