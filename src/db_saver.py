#!/usr/bin/env python

import rospy
from std_smgs.msg import String
import db_persistance 
import psycopg2

conn = None

def initialize() : 
	try : 
		conn = connect_db()
		rospy.init_node("Save Dates on DB" , anonymous = True)
		rospy.Subscriber("Merged Data" , String , callback_saver )
		rospy.spin()
	except (Exception, psycopg2.DatabaseError) as error:
        print(error)

def position_exist ( x , y , conn ) :
	sql = "SELECT id FROM punti WHERE x = " + x + " AND y = " + y 
	id = db_persistance.select_query_id(sql)
	return id	

def create_position ( x , y ) :
	sql = "INSERT INTO punti ( x , y ) values ( " + x + " , " + y + " ) RETURNING id;"
	id = db_persistance.insert_database(sql)
	return id

def save_date ( id_pos , temp , giorno , orario ) : 
	sql = "INSERT INTO temperature ( temperatura , data_misurazione , orario_misurazione , posizione_fk) values ( %s , %s , %s , %s) RETURNING id; "
	id = db_persistance.insert_database(sql)
	return id

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
		conn.close()
	    pass