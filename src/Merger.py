#!/usr/bin/env python

import rospy
from time import sleep
from std_msgs.msg import String
from datetime import datetime

#-------------------------------------------
#---------Global Variables------------------
#-------------------------------------------

merged = ""
#Se il valore è 1 sono stati scritti per ultimi i parametri , Se invece 0 Sono stati scritte le coordinate
last_write = 1 
publisher = None

#-------------------------------------------


def callback_Coordinates(data) :	
	coordinate = data.split(" ");
	x = coordinate[0]
	y = coordinate[1]
	flag = True
	#Si rimane nel ciclo fintanto la stringa non è vuota ed è il suo turno di scrivere altrimenti aspetti 5 secondi
	while flag :
	    if merged == "" and last_write == 1
	        merged = x + " " + y
	        last_write = 0
	        flag = False
	    else 
	        sleep(5)


def callback_Parameters(data) :
    flag = True
    #Si rimane nel ciclo fintanto la stringa non è con dei parametri ed è il suo turno di scrivere altrimenti aspetti 5 secondi
    while flag :
    	if merged != "" and last_write == 0 
    	    merged = merged + " " + str(data)
    	    last_write = 1
    	    flag = False
    	else
    	    sleep(5)
   	#Quando esci dal ciclo trasmetti il dato all'altro nodo e azzeri la stringa
    transmit_merged_dates(merged)
    merged = "" 	    


def transmit_merged_dates (info) :
	rospy.loginfo("Coordinates merged with coordinates : \n " + info + "\n at The time " + datetime.now().strftime('%d-%m-%Y %H:%M:%S') )
    publisher.publish(info + " " + datetime.now().strftime('%d-%m-%Y %H:%M:%S') )



def merge() :
	rospy.init_node("Merge Coordinates & Parameters" , anonymous = True )
	rospy.Subscriber("Parameters", String , callback_Parameters )
	rospy.Subscriber("Coordinates", String , callback_Coordinates )
	publisher = rospy.Publisher("Merged Data" , String , queue_size = 22)
	rospy.spin()

if __name__ == "__main__" :
	try :
	    merge()
	except rospy.ROSInterruptException :
	    pass