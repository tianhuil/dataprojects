
import json
import MySQLdb as mdb

with open(creds.json) as c:
  creds = json.load(c)
  
con = mdb.connect(host=localhost, user=creds["uname"], passwd=creds["pwd"], 'beerad')
cur = con.cursor()

with open('data/brewers.json') as brs:
  for br in brs:
    ins = """
      insert into brewers (id, name, location)
      values ({0}, '{1}', '{2}')""".format(
      br["id"], br["name"], br["location"]
    
    try:
      cur.execute(ins_u)
    except Exception as e:
      print e, br

styles = { }
with open('data/beers.json') as bes:
  for be in bes:
    # extract styles while parsing
    styles[be["style_num"]] = be["style"]
    
    ins = """
      insert into brewers (brewer_id, id, name, style_id, date_add, ba_score, bros_score, abv, ibu, notes)
      values ({0}, '{1}', '{2}')""".format(
      be["brewer_id"], be["id"], be["name"], be["style_num"], be["date_add"],
      be["ba_score"], be["bros_score"], be["abv"], be["ibu"], be["notes"]
    
    try:
      cur.execute(ins_u)
    except Exception as e:
      print e, br
      
with open('data/styles.json', 'w') as st:
  # save local json copy
  st.write(json.dumps(styles))
  
  # fill style table
  for k,v in styles.iteritems():
    ins = """
      insert into brewers (id, style)
      values ({0}, '{1}')""".format(k,v)
    
    try:
      cur.execute(ins)
    except Exception as e:
      print e, br
      

with open('data/users.json') as user_f:

  for u in user_f:
    ins = '''
      insert into users (id, name, title, location, sex)
      values ( {0}, {1}, {2}, {3}, {4} )'''.format(
        u["id"], u["name"], u["title"], u["location"], u["sex"]

    try:
      cur.execute(ins)
    except Exception as e:
      print e

mdb.commit()
cur.close()
mdb.close()