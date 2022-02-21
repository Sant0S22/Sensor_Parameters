#!/usr/bin/env python3

import rospy
from time import sleep
from std_msgs.msg import String
from datetime import datetime

class Merger :
    '''Classe utilizzata per effettuare un merge delle coordinate con parametri aggiungendo marcatura temporale'''

    #Definizione variabili che gestiranno merge
    def __init__( self ) :
        self.merged = ""
        self.last_write = 1 

    #Metodo che gestisce terminazione dell'esecuzione del nodo 
    def callback_end( self , data ) :
        rospy.signal_shutdown("Fine Merge Dati")

    #Metodo callback che gestisce merge delle coordinate
    def callback_Coordinates(self , data) :    
        coordinate = str(data.data).split(" ");
        x = coordinate[0]
        y = coordinate[1]
        flag = True
        while flag :
            if self.merged == "" and self.last_write == 1 :
                self.merged = x + " " + y
                self.last_write = 0
                flag = False
                #print("aspetto turno coordinate")
            else :
                sleep(1)

    #Metodo callback che gestisce merge parametri
    def callback_Parameters(self , data) :
        flag = True
        while flag :
            if self.merged != "" and self.last_write == 0 :
                self.merged = self.merged + " " + str(data.data)
                self.last_write = 1
                flag = False
                #print("aspetto turno parameters")
            else :
                sleep(1)
        self.transmit_merged_dates(self.merged)
        self.merged = ""         

    #Metodo che trasmette stringa merged al nodo db_saver
    def transmit_merged_dates (self , info) :
        rospy.loginfo("Coordinates merged with parameters : \n " + info + "\n at The time " + datetime.now().strftime('%d-%m-%Y %H:%M:%S') )
        self.publisher.publish(info + " " + datetime.now().strftime('%d/%m/%Y %H:%M:%S') )

    #Metodo che inizializza nodo 
    def merge( self ) :
        rospy.init_node("Merger" , anonymous = True )
        rospy.Subscriber("End", String , self.callback_end )
        rospy.Subscriber("Parameters", String , self.callback_Parameters )
        rospy.Subscriber("Coordinates", String , self.callback_Coordinates )
        self.publisher = rospy.Publisher("Merged_Data" , String , queue_size = 22)
        rospy.spin()

if __name__ == "__main__" :
    try :
        merger = Merger()
        merger.merge()
    except Exception as e :
        if type(e) is rospy.ROSInterruptException :
            print("Terminazione Nodo Merger")
        else :
            print(e)