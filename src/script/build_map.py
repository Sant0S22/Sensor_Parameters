#!/usr/bin/env python3

from sensor_omron.read_yaml_file import Read_Yaml_File
import numpy as np 
import cv2 as cv
import matplotlib.pyplot as plt
from PIL import Image
import os

class Build_Map () :
	'''Classe Python che partendi da un file.map Omron costruisce un immagine png'''

	def __init__ ( self , yaml ) :
		self.height = yaml.getValueFromYaml('height')
		self.width = yaml.getValueFromYaml('width')
		self.scale = yaml.getValueFromYaml('scale')
		self.shift_x = yaml.getValueFromYaml('shift_x')
		self.shift_y = yaml.getValueFromYaml('shift_y')
		self.offset_x = yaml.getValueFromYaml('offset_x')
		self.offset_y = yaml.getValueFromYaml('offset_y')
		self.nome_map = yaml.getValueFromYaml('nome_file_map')
		self.nome_output = yaml.getValueFromYaml('nome_file_output')

	#Restituiscono valore variabili 
	def getWidth ( self ) :
		return self.width

	def getHeight ( self ) :
		return self.height

	#Metodo che converte Coordinate robot in pixel utilizzando parametri definiti in yaml
	def convertCoordinatesOnPixel ( self , coordinate , id ) :
		if ( id == "x" ) :
			res = coordinate + self.shift_x + self.offset_x
			res = int(res/self.scale)
			#res = abs(res - width)
		else :
			res = coordinate + self.shift_y + self.offset_y
			res = int(res/self.scale)
			#Modifica delle coordinate y per poter avere l'origine degli assi in basso a sinistra
			res = abs(res-self.height)
		return res  

	#Metodo che apre file.map e legge tutte le righe e colora immagine
	def read_file( self ) :
		flag = 0
		self.map = np.ones([self.height,self.width,4] , np.uint8) *255 #Immagine Bianca
		dirname = os.getcwd()
		os.chdir("..")
		dirname = os.path.dirname(__file__) #src/sensor/src/sensor/node/reader
		index = dirname.find("/src/sensor_omron/")
		path = dirname[:index]
		self.path = path + "/src/sensor_omron"
		file = self.path+"/resources/map/"+self.nome_map
		with open ( file , "r" ) as file : 
			for line in file :
				#Default il flag è a 0 quindi ignora tutte le linee fintanto non arriva a quelle che gli interessano
				#Gestione Linee
				if flag == 1 and line != "DATA\n" :
					string = line
					coordinate = string.split(" ")
					#prendo le coordinate dal file , le shifto della quantità voluta e la scalo con un fattore di scala
					x = self.convertCoordinatesOnPixel(int(coordinate[0]) , "x" )
					y = self.convertCoordinatesOnPixel(int(coordinate[1]) , "y" )
					x2 = self.convertCoordinatesOnPixel(int(coordinate[2]) , "x" )
					y2 = self.convertCoordinatesOnPixel(int(coordinate[3]) , "y" )

					#map[y:y2,x:x2,:] = 0
					p1 = [x,y]
					p2 = [x2,y2]
					self.map = cv.line(self.map,p1,p2,[0,0,0,255],1)

	  			#Gestione punti
				if flag == 2 : 
					string = line
					coordinate = string.split(" ")
					#prendo le coordinate dal file , le shifto della quantità voluta e la scalo con un fattore di scala
					x = self.convertCoordinatesOnPixel(int(coordinate[0]) , "x" )
					y = self.convertCoordinatesOnPixel(int(coordinate[1]) , "y" )

					self.map[y,x,:] = [0,0,0,255]
				#Check del flag
				if line == "LINES\n" :
					print("cambio in linee")
					flag = 1 
				if line == "DATA\n" :
					print("cambio in punti")
					flag = 2

	#Metodo che salva immagine sul disco
	def save_image ( self ) :
		image = Image.fromarray(self.map)
		image.save(self.path+"/resources/map/output/"+self.nome_output)
		print("Mappa Generata con successo")


if __name__ == "__main__" :
	try :
		dirname = os.path.dirname(__file__) #src/sensor/src/script
		index = dirname.find("/src/sensor_omron/")
		path = dirname[:index]
		path = path + "/src/sensor_omron/cfg"
		os.chdir(path)
		yaml = Read_Yaml_File("config_maps.yaml")
		os.chdir(dirname)
		build_map = Build_Map(yaml)
		build_map.read_file()
		build_map.save_image()
	except Exception as e :
		print(e)