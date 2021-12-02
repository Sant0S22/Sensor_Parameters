#!/usr/bin/env python

import rospy
from time import sleep
from std_msgs.msg import String
from datetime import datetime

merged = ""
last_write = 1 #Se 1 ultima write dei parametri , se 0 ultima write delle coordinate
publisher = None


def callback_Coordinates(data) :	
	coordinate = data.split(" ");
	x = coordinate[0]
	y = coordinate[1]
	flag = True
	while flag :
	    if merged == "" and last_write == 1
	        merged = x + y
	        last_write = 0
	        flag = False
	    else 
	        sleep(0.5)


def callback_Parameters(data) :
    flag = True
    while flag :
    	if merged != "" and last_write == 0 
    	    merged = merged + str(data)
    	    last_write = 0
    	    flag = False
    	else
    	    sleep(0.5)
    transmit_merged_dates(merged)
    merged = "" 	    


def transmit_merged_dates (info) :
	rospy.loginfo("Coordinates merged with coordinates : \n " + info + "\n at The time " + datetime.now().strftime('%d-%m-%Y %H:%M:%S') )
    publisher.publish(info + " " + datetime.now().strftime('%d-%m-%Y %H:%M:%S') )



def merge() :
	rospy.init_node("Merge Coordinates & Parameters " , anonymous = True )
	rospy.Subscriber("Parameters", String , callback_Parameters )
	rospy.Subscriber("Coordinates", String , callback_Coordinates )
	publisher = rospy.Publisher("Merged Data" , String , queue_size = 22)
	rospy.spin()

if __name__ == "__main__" :
	try :
	    merge()
	except rospy.ROSInterruptException :
	    pass