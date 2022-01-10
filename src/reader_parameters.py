#!/usr/bin/env python

import rospy
from std_msgs.msg import String
from omron_2jcie_bu01 import Omron2JCIE_BU01
#from datetime import datetime

#Per modificare i parametri interessati vedere questo codice
#https://github.com/nobrin/omron-2jcie-bu01/blob/master/examples/measure_serial.py

def read() :
    publisher = rospy.Publisher("Parameters" , String , queue_size = 22 )
    rospy.init_node("Reader_Parameters" , anonymous = True );
    rate = rospy.Rate(0.1) #10 hz aka 10 messaggi al minuto
    sensor = Omron2JCIE_BU01.serial("/dev/ttyUSB0") # Linux /dev/ttyUSB0
    #devinfo = sensor.info()
    
    while not rospy.is_shutdown() :
    	data = sensor.latest_data_long()
    	#stringa = str(data) #+ datetime.now().strftime('%d-%m-%Y %H:%M:%S')
        stringa = "Temp: " + data.temperature
    	rospy.loginfo(stringa)
    	publisher.publish(stringa)
    	rate.sleep()


if __name__ == "__main__" : 
	try :
		read()
	except rospy.ROSInterruptException :
		pass
