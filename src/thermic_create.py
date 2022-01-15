import numpy as np 
import matplotlib.pyplot as plt
from PIL import Image
import db_persistance 
from Building_Map_Lab import convertCoordinatesOnPixel

def rgb(minimum, maximum, value):
  minimum, maximum = float(minimum), float(maximum)
  ratio = 2 * (value-minimum) / (maximum - minimum)
  b = int(max(0, 255*(1 - ratio)))
  r = int(max(0, 255*(ratio - 1)))
  g = 255 - b - r
  return r, g, b

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
    map[y,x,0] = rgb_values[0] 
    map[y,x,1] = rgb_values[1] 
    map[y,x,2] = rgb_values[2] 

if __name__ == "__main__" : 

  data = inserisci_data_analisi()
  orario = inserisci_orario_analisi()

  conn = None
  try :
    conn = db_persistance.connect_db()
  except (Exception, psycopg2.DatabaseError) as error:
    print(error)

  lista = take_list_dates(data , orario , conn )
  img = Image.open("/map/output/Lab_map.png")
  map = np.asarray(img)
  
  map = modify_thermic( lista , map , conn )

  image = Image.fromarray(map)
  image.save("Lab_map_Thermic.png")