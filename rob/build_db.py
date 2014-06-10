

#!/usr/bin/python

import MySQLdb as mdb
import json

# store login credentials in same directory as this
with open(creds.json) as c:
  creds = json.load(c)

# connect to mysql
# make sure credentials have the appropriate permissions to create databases, tables, etc
con = mdb.connect(host=localhost, user=creds["uname"], passwd=creds["pwd"])
cur = con.cursor()

cur.execute("create database airtravel")  # create database
cur.execute("use airtravel")              # select it

# create table of monthly segment aggregates
# total freight/passengers/etc per carrier per route
cur.execute('''create table if not exists mthlyseg (
  departures_scheduled int not null,
  departures_performed int not null,
  payload decimal(10,2),
  seats int not null,
  passengers int not null,
  freight decimal(10,2),
  mail decimal(10,2),
  distance decimal(5,2),
  ramp_to_ramp decimal(10,2),
  air_time decimal(10,2),
  unique_carrier varchar(5),
  airline_id int not null,
  unique_carrier_name varchar(50),
  unique_carrier_entity varchar(50),
  region varchar(50),
  carrier varchar(50),
  carrier_name varchar(50),
  carrier_group varchar(50),
  carrier_group_new varchar(50),
  origin_airport_id int not null,
  origin_airport_seq_id int not null,
  origin_city_market_id int not null,
  origin varchar(50),
  origin_city_name varchar(50),
  origin_state_abr varchar(2),
  origin_state_fips varchar(50),
  origin_state_nm varchar(50),
  origin_wac varchar(50),
  dest_airport_id int not null,
  dest_airport_seq_id int not null,
  dest_city_market_id int not null,
  dest varchar(50),
  dest_city_name varchar(50),
  dest_state_abr varchar(50),
  dest_state_fips varchar(50),
  dest_state_nm varchar(50),
  dest_wac varchar(50),
  aircraft_group varchar(50),
  aircraft_type varchar(50),
  aircraft_config int not null,
  year int not null,
  quarter int not null,
  month int not null,
  distance_group int not null,
  class varchar(1),
  primary key(year, month, airline_id, origin_airport_id, dest_airport_id) )''' )
  
  
# table containing characteristics of specific aircraft
# primarily interested in available seats and age
#cur.execute("""create table if not exists aircraft