#!/usr/bin/env python

import numpy as np 
import os
import matplotlib.pyplot as plt
from PIL import Image
import db_persistence 
from Building_Map_Lab import convertCoordinatesOnPixel

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

def take_list_dates ( data , orario , conn ) :
  sql = "SELECT temperatura , posizione_fk FROM temperature WHERE data_misurazione = " + data #+ " AND "
  lista = db_persistance.select_query_list(sql , conn)
  return lista

def take_coordinates ( id_co , conn ) : 
  sql = "SELECT x , y FROM punti WHERE id = " + id_co
  punto = db_persistance.select_query(sql , conn) 
  return punto

def inserisci_data_analisi () :
  #data = str(input("Inserisci il giorno di cui vuoi sapere le temperature spaziando giorno mese anno"))
  #tmp = data.split(" ")
  return "22-02-2022"

def inserisci_orario_analisi () :
  #data = str(input("Inserisci il giorno di cui vuoi sapere le temperature spaziando giorno mese anno"))
  #tmp = data.split(" ")
  return "09:00"

def modify_thermic( lista , map , conn ) :
  for misurazione in lista :
    temp = misurazione[0]
    id_pos = misurazione[1]
    coordinate = take_coordinates(id_pos , conn)
    x = convertCoordinatesOnPixel( int(coordinate[0]) , "x" )
    y = convertCoordinatesOnPixel( int(coordinate[1]) , "y" )
    rgb_values = rgb( 0 , 30 , temp )
    for i in range (10) : 
      for j in range (10) :
        map[y + i ,x + j] = rgb_values

#Customized Parameters
max = 30  #Max temperature on Degrees
min = 0   #Min Temperature on Degrees

if __name__ == "__main__" : 

  data = inserisci_data_analisi()
  orario = inserisci_orario_analisi()

  conn = None
  try :
    conn = db_persistance.connect_db()
    lista = take_list_dates(data , orario , conn )
    img = cv.imread("/map/output/Lab_map.png")
    map = img[:,:,::-1] #Conversion BGR to RGB
    #map = np.asarray(img)
  
    map = modify_thermic( lista , map , conn )

    image = Image.fromarray(map)
    image.save("/map/output/Lab_map_Thermic.png")
  except (Exception, psycopg2.DatabaseError) as error:
    print(error)
  finally :
    conn.close()