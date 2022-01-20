#!/usr/bin/env python

import numpy as np 
import psycopg2
import cv2 as cv
import matplotlib.pyplot as plt
from PIL import Image
import db_persistence 
from Building_Map_Lab import convertCoordinatesOnPixel

#Metodo che crea colorazione tramite un calcolo numerico
#Sostituito da Shade Gray e modify map che utilizzano OpenCV
def rgb(minimum, maximum, value):
  minimum, maximum = float(minimum), float(maximum)    
  halfmax = (minimum + maximum) / 2
  if minimum <= value <= halfmax:
    r = 0
    g = int( 255./(halfmax - minimum) * (value - minimum))
    b = int( 255. + -255./(halfmax - minimum)  * (value - minimum))
    return [r,g,b]  
  elif halfmax < value <= maximum:
    r = int( 255./(maximum - halfmax) * (value - halfmax))
    g = int( 255. + -255./(maximum - halfmax)  * (value - halfmax))
    b = 0
    return [r,g,b]
  elif minimum > value :
    return [0,0,255]   
  else :
    return [255,0,0]

def shade_gray ( value , max , min ) :
  perc = (value - min) / (max - min)
  #print("Valore normalizzato con temperatura " + str(value) + " : " str(perc))
  return 255 - (255*perc)
  
def rgb_from_gray ( value , max, min ) :
  gray = np.ones([1,1],dtype = np.uint8)
  col = shade_gray(value, max , min)
  #print(col)
  gray[0][0] = col
  conv = cv.applyColorMap(gray,cv.COLORMAP_JET)
  #conv = cv.applyColorMap(gray,cv.COLORMAP_TURBO )
  rgb = conv[0][0]
  #print(rgb)
  return rgb

def take_list_dates ( data , orario , conn ) :
  sql = "SELECT temperatura , posizione_fk FROM temperature WHERE data_misurazione = \'" + str(data) + "\'" #+ " AND "
  lista = db_persistence.select_query_list(sql , conn)
  return lista

def take_coordinates ( id_co , conn ) : 
  sql = "SELECT x , y FROM punti WHERE id = " + str(id_co)
  punto = db_persistence.select_query(sql , conn) 
  return punto

def inserisci_data_analisi () :
  #data = str(input("Inserisci il giorno di cui vuoi sapere le temperature spaziando giorno mese anno"))
  #tmp = data.split(" ")
  return "22/12/2021"

def inserisci_orario_analisi () :
  #data = str(input("Inserisci il giorno di cui vuoi sapere le temperature spaziando giorno mese anno"))
  #tmp = data.split(" ")
  return "09:00"

def modify_thermic( lista , maps , conn ) :
  for misurazione in lista :
    #print(misurazione)
    temp = misurazione[0]
    id_pos = misurazione[1]
    coordinate = take_coordinates(id_pos , conn)
    #print(coordinate)
    x = convertCoordinatesOnPixel( int(coordinate[0]) , "x" )
    y = convertCoordinatesOnPixel( int(coordinate[1]) , "y" )
    rgb_values = rgb_from_gray( temp , max_temperature , min_temperature )
    for i in range (10) : 
      for j in range (10) :
        maps[y + i ,x + j] = rgb_values
  return maps      

#Customized Parameters
max_temperature = 30  #Max temperature on Degrees
min_temperature = 0   #Min Temperature on Degrees

if __name__ == "__main__" : 

  data = inserisci_data_analisi()
  orario = inserisci_orario_analisi()

  conn = None
  try :
    conn = db_persistence.connect_db()
    lista = take_list_dates(data , orario , conn )
    #print(len(lista))
    img = cv.imread("./map/output/Lab_map.png")
    maps = img[:,:,::-1] #Conversion BGR to RGB
    #map = np.asarray(img)
  
    maps = modify_thermic( lista , maps , conn )

    image = Image.fromarray(maps)
    image.save("./map/output/Lab_map_Thermic.png")
  except (Exception, psycopg2.DatabaseError) as error:
    print(error)
  finally :
    conn.close()