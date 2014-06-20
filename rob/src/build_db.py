

#!/usr/bin/python

from warnings import filterwarnings
from warnings import resetwarnings
import MySQLdb as mdb
import json

from beeradcn import Beerad

filterwarnings('ignore', category = mdb.Warning)

# store login credentials in same directory as this
#with open('creds.json') as c:
#  creds = json.load(c)

# connect to mysql
# make sure credentials have the appropriate permissions to create databases, tables, etc
#con = mdb.connect(host='localhost', user=creds["uname"], passwd=creds["pwd"])
with Beerad() as con:

  cur = con.cursor()
  cur.execute("drop database if exists beerad")
  cur.execute("create database beerad")  # create database
  cur.execute("use beerad")              # select it
    
  cur.execute("drop table if exists brewers")
  cur.execute("""
    create table brewers (
      id int not null,
      name varchar(100),
      location varchar(50),
      primary key (id)
    )""")
    
  cur.execute("drop table if exists users")
  cur.execute("""
    create table users (
      id int not null,
      name varchar(50),
      title varchar(50),
      location varchar(50),
      sex varchar(25),
      primary key (id)
    )""")
    
  cur.execute("drop table if exists styles")
  cur.execute("""
    create table styles (
      id int not null,
      name varchar(50),
      primary key (id)
    )""")
    
  cur.execute("drop table if exists beers")
  cur.execute("""
    create table beers (
      id int not null,
      brewer_id int not null,
      name text,
      style_id int,
      date_add date,
      ba_score int,
      bros_score int,
      abv double(5,2),
      ibu double(5,2),
      notes text,
      primary key (id, brewer_id),
      foreign key (brewer_id)
        references brewers (id)
        on update cascade
        on delete cascade,
      foreign key (style_id)
        references styles (id)
        on update cascade
        on delete cascade
    )""" )
  
  #cur.execute("drop table if exists product_ids")
  #cur.execute("""
  #  create table product_ids (
  #    brewer_id int not null,
  #    beer_id int not null,
  #    primary key (brewer_id, beer_id),
  #    foreign key (brewer_id)
  #      references brewers(id)
  #      on update cascade
  #      on delete cascade,
  #    foreign key (beer_id)
  #      references beers (id)
  #      on update cascade
  #      on delete cascade
  #  )""")
      
  cur.execute("drop table if exists reviews")
  cur.execute("""
    create table reviews (
      brewer_id int not null,
      beer_id int not null,
      user_id int not null,
      rev_date date,
      palate double(3,2),
      taste double(3,2),
      aroma double(3,2),
      appearance double(3,2),
      overall double(3,2),
      review text,
      primary key (brewer_id, beer_id, user_id),
      foreign key (user_id)
        references users (id)
        on update cascade
        on delete cascade,
      foreign key (beer_id, brewer_id)
        references beers (id, brewer_id)
        on update cascade
        on delete cascade
    )""")
  
  cur.execute("drop view if exists reviewsbybeer")
  cur.execute("""
    create view reviewsbybeer as
    select beer_id, count(*) as rev_ct
    from reviews
    group by beer_id """)
  
  cur.execute("drop view if exists reviewsbystyle")
  cur.execute("""
    create view reviewsbystyle as
    select be.style_id, sum(rev_ct) as rev_ct
    from reviewsbybeer as r inner join beers be
      on be.id = r.beer_id
    group by be.style_id """)
    
  cur.execute("drop table if exists basewordcts")
  cur.execute("""
    create table basewordcts (
      id int not null auto_increment,
      word varchar(255),
      count int default 0,
      primary key (id),
      unique (word),
      check (count >= 0)
    )""")
    
  cur.execute("drop procedure if exists wordupsert")
  cur.execute("""
    create procedure wordupsert (new_word varchar(255), ct int)
    begin
      if (select word from basewordcts where word = new_word)
      begin
        update basewordcts
        set count = count + ct
        word = new_word;
      end
      else
      begin
        insert into (word, count)
        values (new_word, ct);
      end
      end if
    end """)
    
  con.commit()  # save to db
  cur.close()   # close cursor

resetwarnings()
