#!/usr/bin/env python

import rospy
from std_msgs.msg import String
import telnetlib
import getpass #Libreria per acquisizione password?

def connection_Telnet() :

	#Definition of Login parameters
    HOST = "192.168.1.1"
    user = str(input("Inserisci il tuo account remoto: "))
    password = getpass.getpass()

    tn = telnetlib.Telnet(HOST)

    tn.read_until("login: ")
    tn.write(user + "\n")
    if password:
        tn.read_until("Password: ")
        tn.write(password + "\n")

    return tn

def reading_coordinates( tn ) :

    publisher = rospy.Publisher("Coordinates" , String , queue_size = 22 )
    rospy.init_node("Reader Coordinates" , anonymous = True )
    rate = rospy.Rate(0.1)

    while rospy.is_shutdown() 
        tn.write("status\n")
        tn.read_until("Location: ")
        coordinates = tn.read_until("LocalizationScore :");

        rospy.loginfo(coordinates)
        publisher.publish(coordinates)
        #Stringa restituita essere tipo x y theta

        rate.sleep()

if __name__ = "__main__" :
	try :
		telnet = connection_Telnet()
		reading_coordinates(telnet)
	except rospy.ROSInterruptException :
		pass
