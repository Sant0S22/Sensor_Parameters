#!/usr/bin/env python3

import numpy as np 
import os
import datetime
import psycopg2
import cv2 as cv
import matplotlib.pyplot as plt
from sensor_omron.read_yaml_file import Read_Yaml_File
from PIL import Image
from sensor_omron.db_persistence import Db_Persistence
from script.build_map import Build_Map

class Maps_Creator :

	def __init__ (self , yaml  , yaml_telnet , yaml_sql ) :
		self.patrolOnce = yaml_telnet.getValueFromYaml('patrolOnce')
		self.build_map = Build_Map(yaml)
		self.numeroParametri = yaml.getValueFromYaml('numeroParametri') 
		self.params = yaml.getValueFromYaml('params')
		self.nome_mappa = yaml.getValueFromYaml('nome_file_output')
		self.params_Max_Min = yaml.getValueFromYaml('params_Max_Min')
		self.db_persistence = Db_Persistence()
		self.raggioCerchio = yaml.getValueFromYaml('raggioCerchio')
		self.sql_patrol = yaml_sql.getValueFromYaml('sql_find_patrol')
		self.sql_range = yaml_sql.getValueFromYaml('sql_query_range_data')
		self.puntiClean = yaml_sql.getValueFromYaml('puntiClean')
		self.misureClean = yaml_sql.getValueFromYaml('misureClean')
		self.sql_anomaly = yaml_sql.getValueFromYaml('sql_find_anomaly')

	#Metodo che acquisisce data da standard input
	def inserisci_data_analisi ( self ) :
		flag = True
		while flag : 
			self.data = str(input("Inserisci La data del giorno di cui vorresti avere la scansione in formato dd/mm/yyyy : \n"))
			try:
				datetime.datetime.strptime(self.data, '%d/%m/%Y')
				flag = False
			except ValueError:
				print("Devi inserire una data che sia valida e nel formato richiesto")

	#Metodo Cge acquisisce orario da standard input
	def inserisci_orario_analisi ( self ) :
		flag = True
		while flag :
			self.orario = str(input("Inserisci l'orario in cui vuoi conoscere la scansione in formato hh:mm : \n"))
			try:
				datetime.datetime.strptime(self.orario, '%H:%M')
				flag = False
			except ValueError:
				print("Devi inserire un orario che sia valido e nel formato richiesto")

	#Metodo che a partire da data e orario inserito vede sul database se esiste un giro effettuato con i parametri inseriti 
	#Se esiste restituisce data e ora di inizio e fine , altrimenti lancia ValueError Exception
	def orarioInizioEFineGiro( self ) :
		#sql = "SELECT data_inizio , data_fine , orario_inizio , orario_fine FROM " + str(self.patrolOnce) + " WHERE data_inizio = \'" + str(self.data) + \
		# "\' AND orario_inizio > \'" + str(self.orario) + "\' ORDER BY data_inizio"
		sql = self.sql_patrol.format(self.patrolOnce,self.data,self.orario)
		date = self.db_persistence.select_query(sql)
		if date == None :
			raise ValueError("Nessun giro effettuato nel range di date inserito")
		self.inizio = date[0]
		self.fine = date[1]
		self.o_inizio = date[2]
		self.o_fine = date[3]

	#Carica Mappa creata da script precedente 
	def carica_mappa ( self ) :
		dirname = os.path.dirname(__file__) #src/sensor/src/script
		index = dirname.find("/src/sensor_omron/")
		path = dirname[:index]
		self.path = path + "/src/sensor_omron"
		file = self.path+"/resources/map/output/"+self.nome_mappa
		self.base = cv.imread(file,cv.IMREAD_UNCHANGED)

	#Salva mappe create dalle misurazioni
	def salva_mappe ( self , orario ) :
		#self.insert_warning_anomaly()
		directory = self.path + '/resources/map/output/' + str(self.inizio) + "-" + orario
		os.makedirs(directory, exist_ok  = True)
		for i in range(1 , self.numeroParametri+1 ) :
			#i = 1
			map_generated = cv.addWeighted(self.base , 0.5 , self.maps_list[i] , 0.5 , 0 )
			map_generated = cv.cvtColor(map_generated, cv.COLOR_BGR2RGBA)
			image = Image.fromarray(map_generated)
			file = directory + '/' +self.params[i] + '.png'
			print("Salvata mappa in posizione " + file )
			image.save(file)

	#Metodo richiamato per chiudere la connessione al db
	def closeDb (self) :
		self.db_persistence.close_db()

	#Metodo che preleva lista misurazioni da db
	def take_list_dates ( self ) :
		#sql = "SELECT posizione_fk , temperature , humidity , light , pressure , noise , etvoc , eco2 FROM misurazioniClean WHERE (data_misurazione BETWEEN \'" + str(self.inizio) + "\' AND \'" + str(self.fine) + "\') AND orario_misurazione BETWEEN \'" + str(self.o_inizio) + "\' AND \'" + str(self.o_fine) + "\'" #+ /
		# order by     qua puoi fare from punti , select punti.x punti.y where punti.id uguale misurazione.id
		sql = self.sql_range.format(self.misureClean,self.puntiClean,self.misureClean,self.puntiClean,self.inizio,self.fine,self.o_inizio,self.o_fine)
		lista = self.db_persistence.select_query_list( sql )
		return lista

	#Metodo che tramite id preleva posizione misurazione sul db
	#Non utilizzato più
	def take_coordinates ( self , id_co ) : 
		sql = "SELECT x , y FROM puntiClean WHERE id = " + str(id_co)
		punto = self.db_persistence.select_query( sql ) 
		return punto

	#Metodo che normalizza il valore in un intervallo tra 0 e 1
	def shade_gray ( self , value , max , min ) :
		perc = (value - min) / (max - min)
		#print("Valore normalizzato con temperatura " + str(value) + " : " + str(perc))
		return (255*perc)

	#Metodo che crea immagine bianche che verranno colorate successivamente
	def create_blank_maps ( self ) :
		self.maps_list = [ None ]
		for i in range(1, self.numeroParametri+1) :
			#i = 1
			maps = np.ones([self.build_map.getHeight(),self.build_map.getWidth(),4],dtype = np.uint8)*255
			self.maps_list = self.maps_list + [ maps ]

	#Metodo che colora immagini bianche
	def modify_thermic( self ,lista ) :
		print( str(len(lista)) + " Misurazioni trovate , Modifica mappa in corso...")
		self.create_blank_maps ()
		for misurazione in lista :
			# IdPos 0 , Temp 1 ,  Humidity 2 , Light 3 , Pressure 4 , Noise 5 , etvoc 6 , etco2 7
			# x , y , temperature , humidity , light , pressure , noise , etvoc , eco2 , data_misurazione , orario_misurazione
			#coordinate = self.take_coordinates( misurazione[0] )
			coordinate = [misurazione[0],misurazione[1]]
			x = self.build_map.convertCoordinatesOnPixel( int(coordinate[0]) , "x" )
			y = self.build_map.convertCoordinatesOnPixel( int(coordinate[1]) , "y" )
			punto = (int(x),int(y))
			#print(punto)
			rgb_list = self.rgb_from_gray( misurazione )
			for i  in range(2,self.numeroParametri+2) :
				#i = 1
				rgb_values = rgb_list[i-1]
				bgr_values = [int(rgb_values[0])]
				bgr_values = bgr_values + [int(rgb_values[1])]
				bgr_values = bgr_values + [int(rgb_values[2])]
				bgr_values = bgr_values + [255]
				maps = self.maps_list[i-1]
				cv.circle(maps,punto,self.raggioCerchio,bgr_values,-1)
				#print(maps[y,x])
				#for i in range (N) : 
					#for j in range (M) :
						#if ( np.all(maps[y+i,x+j] == [255,255,255]) ) :
							#maps[y + i ,x + j] = rgb_values  

	#Metodo che converte sfumatura di grigio in combinazione rgb
	def rgb_from_gray ( self , misurazioni ) :
		gray = np.ones([1,1],dtype = np.uint8)
		rgb_list = [ None ]
		for i  in range(1,self.numeroParametri+1) :
			#i = 1
			gray_scale = self.shade_gray(misurazioni[i+1],(self.params_Max_Min[i])[1],(self.params_Max_Min[i])[0])
			gray[0][0] = gray_scale
			converted = cv.applyColorMap(gray,self.params_Max_Min[i][2])
			rgb_list = rgb_list + [converted[0][0]]
		return rgb_list   

	#Metodo principale della classe che richiama i singoli metodi
	def build ( self ) :
		self.inserisci_data_analisi()
		self.inserisci_orario_analisi()
		#self.data = "11/02/2022"
		#self.orario = "16:55"
		self.carica_mappa()
		self.db_persistence.connect_db()
		self.orarioInizioEFineGiro()
		lista_misure = self.take_list_dates()
		self.modify_thermic(lista_misure)

		#----------------------------------------------------------------------------
		#Operazioni per creare una stringa compatibile per convenzione nome directory 
		#Nomi directory non possono contenere / : o altra punteggiatura
		val_orario = str(self.o_inizio).split(":")
		orarioFile = val_orario[0]+"_"+val_orario[1]
		#-----------------------------------------------------------------------------

		self.salva_mappe( orarioFile)

if __name__ == "__main__" :
	try :
		dirname = os.path.dirname(__file__) #src/sensor/src/script
		index = dirname.find("/src/sensor_omron/")
		path = dirname[:index]
		path = path + "/src/sensor_omron/cfg"
		os.chdir(path)
		yaml = Read_Yaml_File("config_maps.yaml")
		yaml_telnet = Read_Yaml_File("config_param_posit.yaml")
		yaml_sql = Read_Yaml_File("config_sql.yaml")
		os.chdir(dirname)
		maps_creator = Maps_Creator( yaml , yaml_telnet , yaml_sql )
		maps_creator.build()
	except Exception as error:
		if type(error) is psycopg2.DatabaseError :
			print("Errore sul db : " + str(error))
		elif type(error) is ValueError :
			print(error)
		elif type(error) is KeyError :
			print("Problema con key delle mappe caricate da yaml , key inserita non valida" + str(error))
		elif type(error) is KeyboardInterrupt :
			pass
		else :
			print(error)
	finally :
		try :
			maps_creator.closeDb()
		except AttributeError :
			pass
		

