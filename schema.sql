CREATE TABLE controller (
  id integer PRIMARY KEY ASC AUTOINCREMENT NOT NULL,
  description varchar(64) NOT NULL default '',
  commpath varchar(64) NOT NULL default ''
) ;

CREATE TABLE route (
  id integer PRIMARY KEY ASC AUTOINCREMENT NOT NULL,
  name varchar(64) NOT NULL default '',
  difficulty varchar(16)  NOT NULL default ''
) ;

CREATE TABLE route_hold (
  id integer PRIMARY KEY ASC AUTOINCREMENT NOT NULL,
  route_id integer NOT NULL default '0',
  controller_id integer NOT NULL default '0',
  position integer  NOT NULL default '0'
) ;

CREATE TABLE touch_hold (
  id integer PRIMARY KEY ASC AUTOINCREMENT NOT NULL,
  controller_id integer NOT NULL default '0',
  touch_channel integer NOT NULL default '0',
  rc_level integer NOT NULL default '0',
  position integer  NOT NULL default '0'
) ;

