#!/usr/bin/env python3

import rospy
import os
from std_msgs.msg import String
from omron_2jcie_bu01 import Omron2JCIE_BU01
from sensor_omron.read_yaml_file import Read_Yaml_File

class Reader_Parameters :
	'''Classe che acquisisce Parametri da un sensore Omron 2JCIE-BU01'''

	def __init__ ( self, yaml ) :
		self.usb_port = yaml.getValueFromYaml('usb_port')
		self.frequency_Hz = yaml.getValueFromYaml('frequency_Hz')

	#Gestione Terminazione Nodo
	def callback_end( self , data ) :
		rospy.signal_shutdown("Fine Merge Dati")

	#Inizializzazione Nodo
	def inizializzazioneNodo ( self ) :
		rospy.Subscriber("End", String , self.callback_end )
		self.publisher = rospy.Publisher("Parameters" , String , queue_size = 22 ) 
		rospy.init_node("Reader_Parameters" , anonymous = True );
		self.rate = rospy.Rate(self.frequency_Hz)

	#Metodo che si occupa di costruire la Stringa composta da tutte le misurazioni
	def costruisciStringaMisurazioni(self , data) :
		merge = ""
		merge = merge + str(data.temperature)+"-"
		merge = merge + str(data.humidity)+"-"
		merge = merge + str(data.light)+"-"
		merge = merge + str(data.pressure)+"-"
		merge = merge + str(data.noise)+"-"
		merge = merge + str(data.eTVOC)+"-"
		merge = merge + str(data.eCO2)
		return merge

	#Metodo che acquisisce i parametri 
	def read_parameters(self) :
		self.inizializzazioneNodo()
		sensor = Omron2JCIE_BU01.serial(self.usb_port)
		while not rospy.is_shutdown() :
			data = sensor.latest_data_long()
			stringa = "Misure: " + self.costruisciStringaMisurazioni(data)
			rospy.loginfo(stringa)
			self.publisher.publish(stringa)
			self.rate.sleep()


if __name__ == "__main__" :
	try :
		dirname = os.path.dirname(__file__) #src/sensor/src/sensor/node/reader
		index = dirname.find("/src/sensor_omron/") #Ritorna index prima corrispondenza
		path = dirname[:index] #Restituisce sottoStringa
		path = path + "/src/sensor_omron/cfg"
		os.chdir(path) #Cambia Directory in cfg 
		yaml = Read_Yaml_File("config_param_posit.yaml")
		os.chdir(dirname) # Ritorna Directory origine
		reader = Reader_Parameters( yaml )
		reader.read_parameters()
	except Exception as e :
		if type(e) is rospy.ROSInterruptException :
			print("Esecuzione Nodo Interrotta")
			pass
		else :
			print(e)

