#!/usr/bin/env python3

from sensor_omron.read_yaml_file import Read_Yaml_File
import rospy
import os
from std_msgs.msg import String
from sensor_omron.db_persistence import Db_Persistence
from time import sleep
import psycopg2

class Db_Saver :
	'''Classe che salva parametri e coordinate su database'''

	#Definisce variabile per non far terminare programma mentre si salva e quale percorso segue robot da file yaml
	def __init__ ( self , yaml , yaml_sql ) :
		self.punti = yaml_sql.getValueFromYaml('puntiTemporanea')
		self.misurazioni = yaml_sql.getValueFromYaml('misureTemporanea')
		self.sql_exist = yaml_sql.getValueFromYaml('sql_exist_position')
		self.sql_insert = yaml_sql.getValueFromYaml('sql_insert_position')
		self.sql_insert_data = yaml_sql.getValueFromYaml('sql_insert_data')
		self.sql_insert_patrol = yaml_sql.getValueFromYaml('sql_insert_patrol')
		self.patrolOnce = yaml.getValueFromYaml('patrolOnce')
		self.salva = False

	#Metodo che gestisce terminazione esecuzione nodo
	def callback_end( self , data ) :
		date = data.data.split("-")
		inizio = date[0].split(" ")
		fine = date[1].split(" ")
		#print(inizio)
		#print(fine)
		
		while True :
			#print(self.salva)
			if not self.salva : 
				sql = self.sql_insert_patrol.format(self.patrolOnce,inizio[0],inizio[1],fine[0],fine[1])
				#sql = "INSERT INTO " + self.patrolOnce + " ( data_inizio , orario_inizio ,  data_fine , orario_fine ) values ( \'" + inizio[0] + "\' , \'" + inizio[1] + "\' , \'" + fine[0] + "\' , \'" + fine[1] + "\' ) RETURNING id;"
				self.db_persistence.insert_database(sql)
				rospy.signal_shutdown("Fine Salvataggio Dati su db")
				break
			else :
				sleep(1)

	#Metodo che inizializza nodo e connessione al db
	def save( self ) :
		self.db_persistence = Db_Persistence()
		self.db_persistence.connect_db()
		rospy.init_node("Save_Dates_on_DB" , anonymous = True)
		rospy.Subscriber("Merged_Data" , String , self.callback_saver )
		rospy.Subscriber("End" , String , self.callback_end )
		rospy.spin()

	#Metodo che chiude connessione al db
	def chiudiConnessione ( self ) :
		self.db_persistence.close_db()

	#Metodo che verifica se sul db esiste già quella posizione
	def position_exist ( self ,x , y ) :
		sql = self.sql_exist.format(self.punti,x,y)
		#sql = "SELECT id FROM punti WHERE x = " + x + " AND y = " + y 
		id_tuple = self.db_persistence.select_query(sql)
		return id_tuple

	#Metodo che crea posizione sul db
	def create_position ( self ,x , y ) :
		sql = self.sql_insert.format(self.punti,x,y)
		#sql = "INSERT INTO punti ( x , y ) values ( " + x + " , " + y + " ) RETURNING id;"
		id = self.db_persistence.insert_database(sql)
		return id

	#Metodo che salva i dati sul db
	def save_date ( self , id_pos , misurazioni , giorno , orario ) : 
		sql = self.sql_insert_data.format(self.misurazioni,misurazioni[0],giorno,orario,id_pos,misurazioni[1],misurazioni[2],misurazioni[3],misurazioni[4],misurazioni[5],misurazioni[6])
		#sql = "INSERT INTO misurazioni ( temperature , data_misurazione , orario_misurazione , posizione_fk , humidity , light , pressure , noise , etvoc , eco2) \
		#values ( " + str(misurazioni[0]) + " , \'" + str(giorno) + "\' , \'" + str(orario) + "\' , " + str(id_pos) + " , " + str(misurazioni[1]) + " , " + str(misurazioni[2]) + \
		#" , " + str(misurazioni[3]) + " , " + str(misurazioni[4]) + " , " + str(misurazioni[5]) + " , " + str(misurazioni[6]) + ") RETURNING id; "
		id = self.db_persistence.insert_database(sql)
		return id

	#Metodo che separa parametri
	def splittaMisurazioni( self , misure) :
		# Temperatura - Umidità - Luce - Pressione - Rumore - eTVOC - eCO2
		return misure.split("-")

	#Metodo callback che gestisce salvataggio sul db
	def callback_saver(self ,data) :
		##########################################################################
		#	   0			 1		  2		   3		  4		 5	  #	 
		# *coordinataX* *coordinataY*  Misure: *Misurazioni* gg/mm/yyyy hh:mm:ss #
		##########################################################################
		self.salva = True
		dati = str(data.data).split(" ")
		print(dati)
		x = dati[0]
		y = dati[1]
		misure = dati [3]
		misure = self.splittaMisurazioni(misure)
		giorno = dati[4]
		orario = dati[5]
		id_pos = self.position_exist( x , y )
		#print(str(id_pos))
		if ( id_pos == None ) :
			id_pos = self.create_position( x , y )
			#print("non c'era id e l ho creato e ora è " + str(id_pos))
		self.save_date( id_pos[0] , misure , giorno , orario )
		self.salva = False

if __name__ == "__main__" : 
	try :
		dirname = os.path.dirname(__file__) #src/sensor/src/sensor/node/reader
		index = dirname.find("/src/sensor_omron/")
		path = dirname[:index]
		path = path + "/src/sensor_omron/cfg"
		os.chdir(path)
		yaml = Read_Yaml_File("config_param_posit.yaml")
		yaml_sql = Read_Yaml_File("config_sql.yaml")
		os.chdir(dirname)
		saver = Db_Saver(yaml , yaml_sql)
		saver.save()
	except Exception as e :
		if type(e) is rospy.ROSInterruptException :
			print("Terminazione Nodo Db_Saver")
		elif type(e) is psycopg2.DatabaseError :
			print("Errore lato Database : \n")
			print(e)
		else :
			print(e)
	finally :
		try :
			saver.chiudiConnessione()
		except AttributeError :
			pass
		