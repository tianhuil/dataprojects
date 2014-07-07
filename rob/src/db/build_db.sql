
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

alter table reviews add index user_id_ix (user_id);
alter table reviews add index beer_id_ix (beer_id);
alter table reviews add index user_beer_ix (user_id, beer_id);

  
drop view if exists reviewctbybeer;
create view reviewctbybeer as
select beer_id, count(*) as rev_ct
from reviews
group by beer_id
order by rev_ct desc ;
  
drop view if exists reviewctbystyle;
create view reviewctbystyle as
select be.style_id, sum(rev_ct) as rev_ct
from reviewctbybeer as r inner join beers be
  on be.id = r.beer_id
group by be.style_id
order by rev_ct desc ;
  

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
end //
delimiter ;


drop table if exists reviewfeatures ;
create table reviewfeatures (
  style_id int not null,
  feature varchar(255),
  primary key (style_id, feature),
  foreign key (style_id)
    references styles (id)
    on update cascade
    on delete cascade
);

# doesn't really need an upsert, just insert if not exists
delimiter //
drop procedure if exists featureupsert ;
create procedure featureupsert (in new_style_id int, in new_feat varchar(255))
begin
  if not exists (
      select feature
      from reviewfeatures
      where style_id = new_style_id
        and feature = new_feat ) then

    insert into reviewfeatures (style_id, feature)
    values (new_style_id, new_feat) ;
    
  end if ;
end //
delimiter ;


drop table if exists beersimilarity ;
create table beersimilarity (
  beer_id_ref int not null,           # beer being searched
  beer_id_comp int not null,          # beer being compared to
  smooth_ct int not null default 1,   # number of averaging updates
  similarity double,
  primary key (beer_id_ref, beer_id_comp),
  foreign key (beer_id_ref)
    references beers (id)
    on update cascade
    on delete cascade,
  foreign key (beer_id_comp)
    references beers (id)
    on update cascade
    on delete cascade,
  check (smooth_ct > 0)
) partition by hash(beer_id_ref)
  partitions 40;

alter table beersimilarity add index beer_id_ref_ix (beer_id_ref);
alter table beersimilarity add index beer_id_comp_ix (beer_id_comp_ix);

delimiter //
drop procedure if exists similarityupsert ;
create procedure similarityupsert (in new_bi_r int, in new_bi_c int, in new_sim double)
begin
  INSERT INTO beersimilarity (beer_id_ref, beer_id_comp, similarity)
  VALUES (new_bi_r, new_bi_c, new_sim)
  ON DUPLICATE KEY UPDATE
    similarity = new_sim ;
end //
delimiter ;

delimiter //
drop procedure if exists similaritysmooth ;
create procedure similaritysmooth (in new_bi_r int, in new_bi_c int, in new_sim double)
begin
  INSERT INTO beersimilarity (beer_id_ref, beer_id_comp, similarity)
  VALUES (new_bi_r, new_bi_c, new_sim)
  ON DUPLICATE KEY UPDATE
    similarity = (smooth_ct*similarity + new_sim)/(smooth_ct+1) ,
    smooth_ct = smooth_ct + 1 ;
end //
delimiter ;



drop table if exists userreviewstats ;
create table userreviewstats (
  user_id int not null,
  review_ct int not null default 0,
  sum_palate double(10,2) default 0,
  sum_taste double(10,2) default 0,
  sum_aroma double(10,2) default 0,
  sum_appearance double(10,2) default 0,
  sum_overall double(10,2) default 0,
  sum_sq_palate double(20,2) default 0,
  sum_sq_taste double(20,2) default 0,
  sum_sq_aroma double(20,2) default 0,
  sum_sq_appearance double(20,2) default 0,
  sum_sq_overall double(20,2) default 0,
  primary key (user_id),
  foreign key (user_id)
    references users (id)
    on update cascade
    on delete cascade
) ;

alter table userreviewstats add index user_id_ix (user_id);


delimiter //
drop procedure if exists fillurevstats ;
create procedure fillurevstats ()
begin
  truncate table userreviewstats ;
  
  INSERT INTO userreviewstats (
    user_id, review_ct, sum_palate, sum_taste, sum_aroma,
    sum_appearance, sum_overall, sum_sq_palate, sum_sq_taste,
    sum_sq_aroma, sum_sq_appearance, sum_sq_overall )
  select user_id, count(beer_id), sum(palate), sum(taste),
    sum(aroma), sum(appearance), sum(overall),
    sum(palate*palate), sum(taste*taste), sum(aroma*aroma),
    sum(appearance*appearance), sum(overall*overall)
  from reviews
  group by user_id ;
end //
delimiter ;



drop view if exists userreviewsumm ;
create view userreviewsumm as
select user_id, review_ct,
  sum_palate/review_ct as mean_palate,
  sum_taste/review_ct as mean_taste,
  sum_aroma/review_ct as mean_aroma,
  sum_appearance/review_ct as mean_appearance,
  sum_overall/review_ct as mean_overall,
  sqrt((sum_sq_palate - (sum_palate/review_ct)*(sum_palate/review_ct)) / (review_ct - 1)) as std_palate,
  sqrt((sum_sq_taste - (sum_taste/review_ct)*(sum_taste/review_ct)) / (review_ct - 1)) as std_taste,
  sqrt((sum_sq_aroma - (sum_aroma/review_ct)*(sum_aroma/review_ct)) / (review_ct - 1)) as std_aroma,
  sqrt((sum_sq_appearance - (sum_appearance/review_ct)*(sum_appearance/review_ct)) / (review_ct - 1)) as std_appearance,
  sqrt((sum_sq_overall - (sum_overall/review_ct)*(sum_overall/review_ct)) / (review_ct - 1)) as std_overall
from userreviewstats
where review_ct > 1 ;





delimiter //
drop procedure if exists similarbeersbystyle ;
create procedure similarbeersbystyle (in in_beer_id int, in in_style_id int, in in_limit int)
begin
  if in_limit < 0 then
    set in_limit = 1000000 ;
  end if ;

  select
    t.style_id,
    s.name as style_name,
    t.brewer_id,
    br.name as brewer_name,
    t.beer_id,
    b.name as beer_name,
    similarity_score
  from
  (
    select
      b.style_id,
      b.brewer_id,
      r2.beer_id,
      bs.similarity * avg(r2.overall - (urs.sum_overall/urs.review_ct)) as similarity_score
    from
      reviews r2 use index(beer_id_ix),
      reviews r1 use index(user_beer_ix),
      userreviewstats urs use index(user_id_ix),
      beersimilarity bs,
      beers b
    where r2.user_id = r1.user_id
      and r2.beer_id = bs.beer_id_comp
      and r1.user_id = urs.user_id
      and r1.beer_id = bs.beer_id_ref
      and bs.beer_id_ref = in_beer_id
      and r1.beer_id <> r2.beer_id
      and r2.beer_id = b.id
      and b.style_id = in_style_id
    group by style_id, b.brewer_id, r2.beer_id
  ) t inner join beers b
    on t.beer_id = b.id
  inner join brewers br
    on b.brewer_id = br.id
  inner join styles s
    on t.style_id = s.id
  where similarity_score > 0
  order by similarity_score desc
  limit in_limit ;
end //
delimiter ;



delimiter //
drop trigger if exists cascadenewreview ;
create trigger cascadenewreview
after insert on reviews
for each row
begin
  # update user specific review stats
  update userreviewstats
  set review_ct = review_ct + 1,
    sum_palate = sum_palate + new.palate,
    sum_taste = sum_taste + new.taste,
    sum_aroma = sum_aroma + new.aroma,
    sum_appearance = sum_appearance + new.appearance,
    sum_overall = sum_overall + new.overall,
    sum_sq_palate = sum_sq_palate + new.palate*new.palate,
    sum_sq_taste = sum_sq_taste + new.taste*new.taste,
    sum_sq_aroma = sum_sq_aroma + new.aroma*new.aroma,
    sum_sq_appearance = sum_sq_appearance + new.appearance,
    sum_sq_overall = sum_sq_overall + new.overall
  where user_id = new.user_id ;
end //
delimiter ;