#!/usr/bin/env python

import rospy
from std_smgs.msg import String
from db_persistance import connect_db

conn = None

def initialize() : 
	try : 
		conn = connect_db()
		rospy.init_node("Save Dates on DB" , anonymous = True)
		rospy.Subscriber("Merged Data" , String , callback_saver )
	except (Exception, psycopg2.DatabaseError) as error:
        print(error)

def position_exist ( x , y , conn ) :
	try : 
		sql = "SELECT id FROM punti WHERE x = " + x + " AND y = " + y 
		cursor = conn.cursor()
		cursor.execute(sql)
		id = cursor.fetchone()
		cursor.close()
		return id
	except (Exception, psycopg2.DatabaseError) as error:
        print(error)
	

def create_position ( x , y ) :
	try :
		cursor = conn.cursor()
		sql = "INSERT INTO punti ( x , y ) values ( " + x + " , " + y + " ) RETURNING id;"
		cursor.execute(sql)
		pos_id = cursor.fetchone()[0]
		conn.commit()
		cursor.close()
		return pos_id
	except (Exception, psycopg2.DatabaseError) as error:
        print(error)

def save_date ( id_pos , temp , giorno , orario ) : 
	try :
		sql = "INSERT INTO temperature ( temperatura , data_misurazione , orario_misurazione , posizione_fk) values ( %s , %s , %s , %s) RETURNING id; "
		cursor = conn.cursor()
		cursor.execute(sql, (temp,giorno,orario,id_pos))
		temp_id = cursor.fetchone()[0]
		conn.commit()
		cursor.close()
		return temp_id
	except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def callback_saver(data) :
	#Dato tipo che mi arriva :
	# *coordinataX* *coordinataY* Temp: *temperatura* gg-mm-yyyy hh-mm-ss
	dati = data.split(" ")
	x = dati[0]
	y = dati[1]
	temp = dati [3]
	giorno = dati[4]
	orario = dati[5]
	id_pos = position_exist( x , y )
	if ( id_pos == None ) :
		id_pos = create_position( x , y )
	save_date( id_pos , temp , giorno , orario )


if __name__ == "__main__" : 
	try :
		initialize()
	except rospy.ROSInterruptException :
	    pass