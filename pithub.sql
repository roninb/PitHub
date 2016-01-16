drop table if exists user;
create table user(
  userid integer primary key,
  username text not null,
  password text not null,
  gusername text
);

drop table if exists repo;
create table repo(
  repoid integer primary key,
  name text not null,
  commits integer,
  uid integer,
  foreign key(uid) references user(userid)
);

drop table if exists pit;
create table pit(
  pitid integer primary key,
  name text,
  health integer,
  birth text not null,
  uid integer,
  foreign key(uid) references user(userid)
);
