
# run using
# mysql -uroot -p password < src/build_db.sql


drop database if exists beerad2;
create database beerad2;  # create database
use beerad2;              # select it
    
drop table if exists brewers;
create table brewers (
  id int not null,
  name varchar(100),
  location varchar(50),
  primary key (id)
);
    
drop table if exists users;
create table users (
  id int not null,
  name varchar(50),
  title varchar(50),
  location varchar(50),
  sex varchar(25),
  primary key (id)
);
    
drop table if exists styles;
create table styles (
  id int not null,
  name varchar(50),
  primary key (id)
);
    
drop table if exists beers;
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
);
   
drop table if exists reviews;
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
);
  
drop view if exists reviewctbybeer;
create view reviewctbybeer as
select beer_id, count(*) as rev_ct
from reviews
group by beer_id
order by rev_ct ;
  
drop view if exists reviewctbystyle;
create view reviewctbystyle as
select be.style_id, sum(rev_ct) as rev_ct
from reviewctbybeer as r inner join beers be
  on be.id = r.beer_id
group by be.style_id
order by rev_ct ;
  

drop view if exists beerctbystyle;
create view beerctbystyle as
select style_id, count(id) as beer_ct
from beers
group by style_id
order by beer_ct desc ;
  
    
drop table if exists basewordcts;
create table basewordcts (
  id int not null auto_increment,
  word varchar(255),
  count int default 0,
  primary key (id),
  unique (word),
  check (count >= 0)
);
    


delimiter //
//
drop procedure if exists wordupsert ;
create procedure wordupsert (in new_word varchar(255), in ct int)
begin
  if exists (select word from basewordcts where word = new_word) then
    update basewordcts
    set count = count + ct
    where word = new_word ;
  else
    insert into basewordcts (word, count)
    values (new_word, ct) ;
  end if ;
end ;
//

