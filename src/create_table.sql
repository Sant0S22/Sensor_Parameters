begin transaction;

create table punti( 
	x integer,
	y integer,
	id serial primary key
);

create table temperature(
	id serial primary key,
	temperatura real ,
	data_misurazione date ,
	orario_misurazione time ,
	posizione_fk serial references punti(id) on update cascade 
);

commit;
