import numpy as np 
import matplotlib.pyplot as plt
from PIL import Image

#Valori customizzabili

#Parametri dimensione immagine
height = 600
width = 1200

#parametro di scalatura
scale = 18 
#Valore per azzerare coordinate negative x
shift_x = 8240 
#Valore per azzerare coordinate negative x
shift_y = 6420
#Valori di offset per cerare una certa distanza dai bordi dell'immagine
offset_x = 760
offset_y = 580

#--------------------------------------------------------------------
#--------------------------------Code--------------------------------
#--------------------------------------------------------------------

def convertCoordinatesOnPixel ( coordinate , id ) :
  if ( id == "x" ) :
    res = coordinate + shift_x + offset_x
    res = int(res/scale)
    #res = abs(res - width)
  else :
    res = coordinate + shift_y + offset_y
    res = int(res/scale)
    #Modifica delle coordinate y per poter avere l'origine degli assi in basso a sinistra
    res = abs(res-height)
  return res  

if __name__ == "__main__" :
  flag = 0   #0 ignore - 1 Linee - 2 Punti
  map = np.ones([height,width,3],np.uint8)*255 #Immagine tutta bianca 

  #Apre file e scansiona linea per linea
  #file = open("/content/drive/MyDrive/Cartella Tesi/Laboratorio.map" , "r" )

  #with open("/content/drive/MyDrive/Cartella Tesi/Laboratorio.map" , "r" ) as file :
  with open("/map/Laboratorio.map" , "r" ) as file :
    for line in file :
      #Default il flag è a 0 quindi ignora tutte le linee fintanto non arriva a quelle che gli interessano
      #Gestione Linee
      if flag == 1 and line != "DATA\n" :
        string = line
        coordinate = string.split(" ")
        #prendo le coordinate dal file , le shifto della quantità voluta e la scalo con un fattore di scala
        x = convertCoordinatesOnPixel(int(coordinate[0]) , "x" )
        y = convertCoordinatesOnPixel(int(coordinate[1]) , "y" )
        x2 = convertCoordinatesOnPixel(int(coordinate[2]) , "x" )
        y2 = convertCoordinatesOnPixel(int(coordinate[3]) , "y" )

        map[y:y2,x:x2,:] = 0
      #Gestione punti
      if flag == 2 : 
        string = line
        coordinate = string.split(" ")
        #prendo le coordinate dal file , le shifto della quantità voluta e la scalo con un fattore di scala
        x = convertCoordinatesOnPixel(int(coordinate[0]) , "x" )
        y = convertCoordinatesOnPixel(int(coordinate[1]) , "y" )

        map[y,x,:] = 0
      #Check del flag
      if line == "LINES\n" :
        print("cambio in linee")
        flag = 1 
      if line == "DATA\n" :
        print("cambio in punti")
        flag = 2



  #Mostra l'immagine Della mappa Creata 
  plt.imshow(map)

  #Salva L'immagine in formato png 
  image = Image.fromarray(map)
  image.save("/map/ouput/Lab_map.png")