#!/usr/bin/env python3

import rospy
import os
from std_msgs.msg import String
from datetime import datetime
import telnetlib
from sensor_omron.read_yaml_file import Read_Yaml_File

class Reader_Coordinates :
	'''Classe Creata per acquisire Coordinate da una Base OmronLD60'''

	def __init__( self , yaml ) :
		self.host = yaml.getValueFromYaml('host')
		self.password = yaml.getValueFromYaml('password')
		self.port = yaml.getValueFromYaml('port')
		self.frequency_Hz = yaml.getValueFromYaml('frequency_Hz')
		self.patrol = yaml.getValueFromYaml('patrolOnce')

	#Cosa Fare Quando il robot finisce il percorso prefissato
	def end_node( self ) :
		data_fine = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
		stringa = self.data_inizio + "-" + data_fine
		self.publisher_end.publish(stringa)
		rospy.signal_shutdown("Fine Coordinate nodo")

	#Inizializzazione Nodo
	def inizializzazioneNodo ( self ):
		self.publisher = rospy.Publisher("Coordinates" , String , queue_size = 22 )
		self.publisher_end = rospy.Publisher("End" , String , queue_size = 4 )
		rospy.init_node("Reader_Coordinates" , anonymous = True )
		self.rate = rospy.Rate(self.frequency_Hz)

	#Connessione a telnet 
	def connessioneTelnet(self) :
		print("Connessione in corso al server telnet..")
		#print("Host : " + str(self.host) + " port : " str(self.port))
		self.tn = telnetlib.Telnet(self.host,self.port)
		#print(tn)
		s = self.tn.read_until(b"Enter password:")
		#print(s)
		self.tn.write(self.password.encode("ascii") + b"\n" )
		print("Password Inserita")

	def chiudiTelnet(self) :
		self.tn.close()

	#Metodo che acquisisce coordinate e controlla quando interrompere i nodi
	def read_coordinates(self) :
		#print("ciao")
		self.inizializzazioneNodo()
		#print("Mondo")
		self.connessioneTelnet()
		#print("skrr")
		self.data_inizio = datetime.now().strftime('%d/%m/%Y %H:%M:%S')	

		self.tn.write(b"patrolOnce "+ self.patrol.encode("ascii") + b"\n")

		while not rospy.is_shutdown() :
			status = {}
			self.tn.write(b"status\n")

			self.tn.read_until(b"ExtendedStatusForHumans: ")
			output = (self.tn.read_until(b"\n")).decode("ascii")
			status['ExtendedStatusForHumans'] = output

			self.tn.read_until(b"Status: ")
			output = (self.tn.read_until(b"\n")).decode("ascii")
			status['Status'] = output

			self.tn.read_until(b"StateOfCharge: ")
			output = (self.tn.read_until(b"\n")).decode("ascii")
			status['StateOfCharge'] = output

			self.tn.read_until(b"Location: ")
			output = (self.tn.read_until(b"\n")).decode("ascii")
			status['Location'] = output

			self.tn.read_until(b"LocalizationScore: ")
			output = (self.tn.read_until(b"\n")).decode("ascii")
			status['LocalizationScore'] = output

			self.tn.read_until(b"Temperature: ")
			output = (self.tn.read_until(b"\n")).decode("ascii")
			status['Temperature'] = output

			if "Finished patrolling route" in status['Status'] :
				self.end_node()
				break

			rospy.loginfo(status['Location'])
			self.publisher.publish(status['Location'])
			self.rate.sleep()  

	#Metodo per effettuare test senza telnet
	def read_coordinates_prova(self) :
		self.inizializzazioneNodo()
		i = 0
		self.data_inizio = datetime.now().strftime('%d/%m/%Y %H:%M:%S')	
		while not rospy.is_shutdown() :
			if i == 100 :
				self.end_node()
				break
			i = i + 10
			rospy.loginfo(str(i)+" "+str(i)+" "+str(i))
			self.publisher.publish(str(i)+" "+str(i)+" "+str(i))
			self.rate.sleep()


if __name__ == "__main__" :
	try :
		dirname = os.path.dirname(__file__) #src/sensor/src/sensor/node/reader
		index = dirname.find("/src/sensor_omron/")
		path = dirname[:index]
		path = path + "/src/sensor_omron/cfg"
		os.chdir(path)
		yaml = Read_Yaml_File("config_param_posit.yaml")
		os.chdir(dirname)
		reader = Reader_Coordinates(yaml)
		reader.read_coordinates_prova()
	except Exception as e :
		if type(e) is rospy.ROSInterruptException :
			print("Esecuzione Nodo Interrotta")
			pass
		elif type(e) is EOFError :
			print("Telnet chiuso , impossibile leggere infomazioni\n")
			print(e)
		else :
			print(e)
	finally :
		try :
			reader.chiudiTelnet()
		except AttributeError :
			pass