begin transaction;

create table punti( 
	x integer,
	y integer,
	id serial primary key
);

create table misurazioni(
	id serial primary key,
	temperature real ,
	humidity real ,
	light real ,
	pressure real ,
	noise real ,
	etvoc real ,
	eco2 real ,
	data_misurazione date ,
	orario_misurazione time ,
	posizione_fk serial references punti(id) on update cascade 
);

create table giroBuccino (
	id serial primary key ,
	data_inizio date ,
	data_fine date ,
	orario_inizio time,
	orario_fine time
);

commit;
