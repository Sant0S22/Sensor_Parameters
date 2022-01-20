#!/usr/bin/env python

import rospy
from std_msgs.msg import String
import telnetlib
import getpass #Libreria per acquisizione password

def connection_Telnet() :
    #------------------------------
	#Definition of Login parameters
    #------------------------------

    HOST = "192.168.1.1"
    user = str(input("Inserisci username login telnet: "))
    password = getpass.getpass()

    #------------------------------

    #Connessione ad host tramite protocollo telnet
    tn = telnetlib.Telnet(HOST)

    tn.read_until("login: ")
    #Scrive sulla console telnet nomeutente e password ( se è stata inserita )
    tn.write(user + "\n") 
    if len(password) != 0 :
        tn.read_until("Password: ")
        tn.write(password + "\n")

    return tn

def reading_coordinates( tn ) :

    #-------------------------------
    #------Custom Parameters--------
    #-------------------------------

    frequencyHZ = 0.1

    #--------------------------------

    #Il nodo Reader Coordinates pubblicherà sul topic Coordinates messaggi di tipo stringa 1 ogni 10 secondi
    publisher = rospy.Publisher("Coordinates" , String , queue_size = 22 )
    rospy.init_node("Reader Coordinates" , anonymous = True )
    rate = rospy.Rate(frequencyHZ)

    while rospy.is_shutdown() 
        #Scrive sulla console il comando status , la base omron risponderà con una serie di informazioni :
            #Status: <status>
            #StateOfCharge: <Percentage>
            #Location: <X> <Y> <Theta>
            #LocalizationScore: <score>
            #Temperature: <degrees>
        tn.write("status\n")
        tn.read_until("Location: ")
        coordinates = tn.read_until("LocalizationScore :"); #Restituirà <x> <y> <Theta>

        rospy.loginfo(coordinates)
        publisher.publish(coordinates)

        rate.sleep()

if __name__ = "__main__" :
	try :
		telnet = connection_Telnet()
		reading_coordinates(telnet)
	except rospy.ROSInterruptException :
		pass
