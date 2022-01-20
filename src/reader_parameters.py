#!/usr/bin/env python

import rospy
from std_msgs.msg import String
from omron_2jcie_bu01 import Omron2JCIE_BU01
#from datetime import datetime

#Per modificare i parametri interessati vedere questo codice
#https://github.com/nobrin/omron-2jcie-bu01/blob/master/examples/measure_serial.py  *

def read() :
    #------------------------------------
    #--------- Custom Parameters---------
    #------------------------------------

    frequencyHZ = 0.1
    usb_port = "/dev/ttyUSB0" #Linux /dev/ttyUSB0 Windows COM5

    #------------------------------------


    #Nodo Ros si chiamerà Reader_Parameters e pubblicherà informazioni su un topic chiamato Parameters , messaggi di tipo String
    publisher = rospy.Publisher("Parameters" , String , queue_size = 22 ) 
    rospy.init_node("Reader_Parameters" , anonymous = True );
    #Valore in Hz , se 10 = 10hz => 10 Messaggi al secondo , con 0.1 sono 1 messaggio ogni 10 secondi
    rate = rospy.Rate(frequencyHZ) 
    #Accedere alla porta usb per accedere al sensore
    sensor = Omron2JCIE_BU01.serial(usb_port)
    # Per Avere informazioni sull'hardware del sensore
    #devinfo = sensor.info() 
    
    while not rospy.is_shutdown() :   #Fintanto il nodo ros non venga interrotto
        #Preleva dati da sensore , per formato del dato vedere *
    	data = sensor.latest_data_long() 
    	#stringa = str(data) #+ datetime.now().strftime('%d-%m-%Y %H:%M:%S')
        stringa = "Temp: " + str(data.temperature)
        #Stampa a console il dato costruito sopra
    	rospy.loginfo(stringa)
        #Pubblica nel topic il dato
    	publisher.publish(stringa)
    	rate.sleep()


if __name__ == "__main__" : 
	try :
		read()
	except rospy.ROSInterruptException :
		pass
