
import json
import MySQLdb as mdb

with open(creds.json) as c:
  creds = json.load(c)
  
con = mdb.connect(host=localhost, user=creds["uname"], passwd=creds["pwd"], 'beerad')

with open('users.json') as user_f, closing(con.cursor()) as cur:
  
  for u in user_f:
    ins_u = '''
      insert into users (id, name, title, location, sex)
      values ( {0}, {1}, {2}, {3}, {4} )'''.format(
        u["id"], u["name"], u["title"], u["location"], u["sex"]

    try:
      cur.execute(ins_u)
    except Exception as e:
      print e
      
    break
