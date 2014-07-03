import json
import os
from pprint import pprint
from bs4 import BeautifulSoup
from urllib import urlopen
import sqlite3
import re

def userDB(user, sub_dir):
    conn = sqlite3.connect(os.path.join(sub_dir,'yelp.db'))
    ################### Store user
    conn.execute("DROP TABLE IF EXISTS user;")
    conn.execute('''CREATE TABLE user
        ( ID            INT PRIMARY KEY NOT NULL,
          NAME          TEXT NOT NULL,
          DATE          TEXT NOT NULL,
          STARS         REAL NOT NULL,
          REVIEWS       INT  NOT NULL,
          VOTES_C       INT  NOT NULL,
          VOTES_F       INT  NOT NULL,
          VOTES_U       INT  NOT NULL,
          FRIENDS       INT  NOT NULL,
          ELITE         INT  NOT NULL,
          USER_ID       TEXT NOT NULL);''')
    
    for i in range(len(user)):
        val = "%s,\"%s\",\"%s\",%s,%s,%s,%s,%s,%s,%s,\"%s\"" % \
                (str(i), user[i]['name'], \
                user[i]['yelping_since'], str(user[i]['average_stars']), \
                str(user[i]['review_count']), str(user[i]['votes']['cool']), \
                str(user[i]['votes']['funny']), str(user[i]['votes']['useful']), \
                str(len(user[i]['friends'])), str(len(user[i]['elite'])), \
                user[i]['user_id'] )     
        insert1 = "INSERT INTO user (ID,NAME,DATE,STARS,REVIEWS,\
            VOTES_C,VOTES_F,VOTES_U,FRIENDS,ELITE,USER_ID) \
            VALUES (%s)" % val.encode('ascii','ignore')
        conn.execute(insert1);
        conn.commit();
    
    conn.close()

def tipDB(tip, sub_dir):
    conn = sqlite3.connect(os.path.join(sub_dir,'yelp.db'))
    ################### Store tip
    conn.execute("DROP TABLE IF EXISTS tip;")
    conn.execute('''CREATE TABLE tip
        ( ID            INT PRIMARY KEY NOT NULL,
          BUSINESS_ID   TEXT NOT NULL,
          DATE          TEXT NOT NULL,
          LIKES         INT  NOT NULL,
          TEXT          TEXT NOT NULL,
          USER_ID       TEXT NOT NULL);''')
    
    
    for i in range(len(tip)):
        text = tip[i]['text']
        text = text.replace('"','\"\"')
        val = "%s,\"%s\",\"%s\",%s,\"%s\",\"%s\"" % (str(i), tip[i]['business_id'], \
                tip[i]['date'], str(tip[i]['likes']), text, tip[i]['user_id'] )     
        insert1 = "INSERT INTO tip (ID,BUSINESS_ID,DATE,LIKES,TEXT,USER_ID) VALUES (%s)" % \
                    val.encode('ascii','ignore')    
        conn.execute(insert1);
        conn.commit();
    
    conn.close()

def reviewDB(review, sub_dir):
    conn = sqlite3.connect(os.path.join(sub_dir,'yelp.db'))
    ################### Store review
    conn.execute("DROP TABLE IF EXISTS review;")
    conn.execute('''CREATE TABLE review
        ( ID            INT PRIMARY KEY NOT NULL,
          BUSINESS_ID   TEXT NOT NULL,
          DATE          TEXT NOT NULL,
          STARS         REAL NOT NULL,
          TEXT          TEXT NOT NULL,
          VOTES_C       INT  NOT NULL,
          VOTES_F       INT  NOT NULL,
          VOTES_U       INT  NOT NULL,
          USER_ID       TEXT NOT NULL);''')
    
    for i in range(len(review)):
        text = review[i]['text']
        text = text.replace('"','\"\"')
        val = "%s,\"%s\",\"%s\",%s,\"%s\",%s,%s,%s,\"%s\"" % \
                (str(i), review[i]['business_id'], \
                review[i]['date'], str(review[i]['stars']), text, \
                str(review[i]['votes']['cool']), str(review[i]['votes']['funny']), \
                str(review[i]['votes']['useful']), review[i]['user_id'] )     
        insert1 = "INSERT INTO review (ID,BUSINESS_ID,DATE,STARS,TEXT,\
            VOTES_C,VOTES_F,VOTES_U,USER_ID) VALUES (%s)" % val.encode('ascii','ignore')
        conn.execute(insert1);
        conn.commit();
    
    conn.close()

def bus_catDB(bus, sub_dir):
    conn = sqlite3.connect(os.path.join(sub_dir,'yelp.db'))

    categories = {}
    for i in range(len(bus)):
       for key in bus[i]['categories']:
           if key not in categories.keys(): categories[key] = 1

    categories2 = {}
    for key in categories.keys():
       temp = re.sub("[&]", "and", key)
       temp = re.sub("[ -/(),']", "", temp)
       categories2[temp] = categories[key]
   
    sortKeys = sorted(categories2.keys())
    l = len(sortKeys)

    insert_sql = "(ID INT PRIMARY KEY NOT NULL, BUSINESS_ID TEXT NOT NULL" \
                    + ",%s INT NOT NULL"*l + ")"
    insert_sql = insert_sql % tuple(sortKeys)
    insert_sql = "CREATE TABLE bus_cat%s;" % insert_sql

    conn.execute("DROP TABLE IF EXISTS bus_cat;")
    # conn.execute("VACUUM bus_cat;")
    conn.execute(insert_sql)
    
    tempDict = {}
    for i in range(len(bus)):
       values = []
       for key in sortKeys: tempDict[key] = 0
       for key in bus[i]['categories']:
           temp = re.sub("[&]", "and", key)
           temp = re.sub("[ -/(),']", "", temp)
           if temp in sortKeys: tempDict[temp] = 1
       for key in sortKeys: values.append(tempDict[key])

       insert_sql = "INSERT INTO bus_cat(ID, BUSINESS_ID, %s) VALUES(%s, \"%s\", %s)"
       cols = ', '.join(sortKeys)
       vals = ', '.join(["%s" for x in range(l)])
       vals = vals % tuple(values)
       insert_sql = insert_sql % (cols, str(i), bus[i]['business_id'], vals)
       conn.execute(insert_sql)
       conn.commit()

    conn.close()
        
def busDB(bus, sub_dir):
    conn = sqlite3.connect(os.path.join(sub_dir,'yelp.db'))
    ################### Store business
    conn.execute("DROP TABLE IF EXISTS bus;")
    conn.execute('''CREATE TABLE bus
        ( ID            INT PRIMARY KEY NOT NULL,
          BUSINESS_ID   TEXT NOT NULL,
          NAME          TEXT NOT NULL,
          ADDRESS       TEXT NOT NULL,
          CITY          TEXT NOT NULL,
          LATITUDE      REAL NOT NULL,
          LONGITUDE     REAL NOT NULL,
          STARS         REAL NOT NULL,
          REVIEWS       INT  NOT NULL,
          OPEN          INT  NOT NULL);''')
    
    for i in range(len(bus)):
        val = "%s,\"%s\",\"%s\",\"%s\",\"%s\",%s,%s,%s,%s,%s" % \
                (str(i), bus[i]['business_id'], bus[i]['name'], \
                bus[i]['full_address'], bus[i]['city'], \
                str(bus[i]['latitude']), str(bus[i]['longitude']), \
                str(bus[i]['stars']), str(bus[i]['review_count']), \
                str(int(bus[i]['open'] == 1)))     
        insert1 = "INSERT INTO bus (ID,BUSINESS_ID,NAME,ADDRESS,CITY,\
            LATITUDE,LONGITUDE,STARS,REVIEWS,OPEN) VALUES (%s)" % val
        conn.execute(insert1);
        conn.commit();
    
    conn.close()
    
def catDB (sub_dir):
    file = 'catList.txt'
    html = urlopen(os.path.join(sub_dir,file)).read()
    soup = BeautifulSoup(html)
    mains = soup.select("ul.attr-list > li")

    # mainCat is list of main categories in Yelp
    mainCat = []
    for a in mains:
        cat = re.sub("\(.*\)", "", a.text)
        cat = re.sub("[&]", "and", cat)
        cat = re.sub("[ -/(),']", "", cat)
        mainCat.append(cat)

    subs = soup.select("ul.attr-list > ul")

    # subCat is list of sub-categories in Yelp
    subCat = []
    count = 0
    for sub in subs:
        temp = []
        for a in sub.select("li"):
            cat = a.text.rsplit("(", 1)[0]
            cat = re.sub("[&]", "and", cat)
            cat = re.sub("[ -/(),']", "", cat)
            temp.append(cat)
        
        subCat.append(temp)

    conn = sqlite3.connect(os.path.join(sub_dir,'yelp.db'))

    # create table of categories called cat
    # columns = main categories
    # rows    = sub-categories
    # entries = 1 if sub-category in main category, 0 otherwise

    l    = len(mainCat)
    insert_sql = "(ID INT PRIMARY KEY NOT NULL, SUBCATEGORY TEXT NOT NULL" \
                    + ",%s INT NOT NULL"*l + ")"
    insert_sql = insert_sql % tuple(mainCat)
    insert_sql = "CREATE TABLE cat%s;" % insert_sql

    conn.execute("DROP TABLE IF EXISTS cat;")
    conn.execute(insert_sql)

    catFlat = []
    for i in subCat: catFlat.extend(i)
    r = len(catFlat)

    index = 0
    count = 0
    for i in range(r):
        p = [0]*l
        p[index] = 1
        insert_sql = "INSERT INTO cat(ID, SUBCATEGORY, %s) VALUES(%s, \"%s\", %s)"
        cols = ', '.join(mainCat)
        vals = ', '.join(["%s" for x in range(l)])
        vals = vals % tuple(p)
        insert_sql = insert_sql % (cols, str(i), catFlat[i], vals)
        conn.execute(insert_sql)
        conn.commit()
    
        if count + 1 < len(subCat[index]): count += 1
        else:
            count = 0
            index += 1
    
    conn.close()

    # there are 780 total sub-categories including main categories
    # there are 758 sub-categories
    # there are 22 main categories

def rev_cat(sub_dir):
    conn = sqlite3.connect(os.path.join(sub_dir,'yelp.db'))
    conn.execute("DROP TABLE IF EXISTS rev_cat;")
    conn.execute("VACUUM rev_cat;")
    conn.execute('''CREATE TABLE rev_cat AS SELECT review.DATE, review.STARS, 
                    review.TEXT, review.VOTES_C, review.VOTES_F, review.VOTES_U, 
                    review.USER_ID, bus_cat.* FROM review JOIN bus_cat ON 
                    review.BUSINESS_ID==bus_cat.BUSINESS_ID;''')
    # conn.execute("DROP TABLE IF EXISTS review;")
    # conn.execute("VACUUM review;")
    conn.close()
                
def load():   
    sub_dir = "/Users/yb/data_project/yelp_phoenix_academic_dataset/" 
    
    # Load all of the data from .json files
    bus = []
    with open(os.path.join(sub_dir,'yelp_academic_dataset_business.json')) as f:
        for line in f:
            bus.append(json.loads(line))
    user = []
    with open(os.path.join(sub_dir,'yelp_academic_dataset_user.json')) as f:
        for line in f:
            user.append(json.loads(line))
    tip = []
    with open(os.path.join(sub_dir,'yelp_academic_dataset_tip.json')) as f:
        for line in f:
            tip.append(json.loads(line))
    review = []
    with open(os.path.join(sub_dir,'yelp_academic_dataset_review.json')) as f:
        for line in f:
            review.append(json.loads(line))

    # Insert data into sqlite3 database
    tipDB(tip, sub_dir)
    reviewDB(review, sub_dir)
    userDB(user, sub_dir)
    bus_catDB(bus, sub_dir)
    busDB(bus, sub_dir)
    catDB(sub_dir)
    # rev_cat(sub_dir)

if __name__ == '__main__':
    load()