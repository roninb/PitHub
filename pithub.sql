drop table if exists user;
create table user(
  userid integer primary key,
  username text not null,
  password text not null,
  gusername text,
  greponame text
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
