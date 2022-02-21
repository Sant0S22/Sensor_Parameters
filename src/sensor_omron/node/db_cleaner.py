#!/usr/bin/env python3

import rospy
from std_msgs.msg import String
from std_msgs.msg import Bool
from sensor_omron.db_persistence import Db_Persistence
import psycopg2
from sensor_omron.read_yaml_file import Read_Yaml_File
import time
from script.build_map import Build_Map
import numpy as np
from PIL import Image
import os
import copy
import cv2 as cv


class Misurazione :

    def __init__ ( self , misurazione , numeroParametri = 7 ) :
        self.anomaly = False
        self.listAnomaly = []
        self.mapParams = { }
        self.numeroParametri = numeroParametri
        self.fromArrayToAttributes(misurazione)

    def __hash__ (self) :
        return hash(self.mapParams[0]) + hash(self.mapParams[1])

    def fromArrayToAttributes(self , misurazione ) : 
        #print(misurazione)
        #x , y , data_misurazione , orario_misurazione , temperature , humidity , light , pressure , noise , etvoc , eco2 
        for i in range( 0 , self.numeroParametri + 4 ) :
            self.mapParams[i] = misurazione[i]

    def setValueAtIndex( self , i , value ) :
        self.mapParams[i] = value

    def getValueAtIndex ( self , i ) :
        return self.mapParams[i]

    def changeValuesMedia ( self , punto ) :
        for i in range(4,self.numeroParametri+4) :
            self.mapParams[i] = punto.getValueAtIndex(i)

    def buildArrayMisurazione ( self ) :
        misurazioni = []
        for i in range(4,self.numeroParametri+4) :
            misurazioni = misurazioni + [self.mapParams[i]]
        return misurazioni

    def setAnomaly ( self , index , type ) :
        self.anomaly = True
        self.listAnomaly = self.listAnomaly + [(index,type)]

    def getListAnomaly (self) :
        return self.listAnomaly

    def getListParametersAnomaly ( self ) :
        if len(self.listAnomaly) == 0 :
            return "null"
        anomaly = ""
        for a in self.listAnomaly :
            anomaly = anomaly + str(a[0]) + "-"
        return anomaly

    def isAnomaly (self) :
        return self.anomaly

    def cloneMisurazione ( self ) :
        return copy.deepcopy(self)

class Db_Cleaner :
    
    
    def __init__( self , yaml_sql , yaml , yaml_maps) :
        self.sql_patrol = yaml_sql.getValueFromYaml('sql_find_patrol')
        self.nome_map = yaml_maps.getValueFromYaml('nome_file_output')
        self.icon_lux = yaml.getValueFromYaml('icon_light')
        self.icon_therm = yaml.getValueFromYaml('icon_therm')
        self.icon_warning = yaml.getValueFromYaml('icon_warning')
        self.thresholds = yaml.getValueFromYaml('thresholds_anomaly')
        self.weightAnomaly = yaml.getValueFromYaml('weight_anomaly')
        self.numeroParametri = yaml.getValueFromYaml('numeroParametri')
        self.puntiTemporanea = yaml_sql.getValueFromYaml('puntiTemporanea')
        self.misureTemporanea = yaml_sql.getValueFromYaml('misureTemporanea')
        self.puntiClean = yaml_sql.getValueFromYaml('puntiClean')
        self.misureClean = yaml_sql.getValueFromYaml('misureClean')
        self.sql_query_range = yaml_sql.getValueFromYaml('sql_query_range')
        self.sql_max_min = yaml_sql.getValueFromYaml('sql_max_min')
        self.sql_crea_misure = yaml_sql.getValueFromYaml('sql_crea_misurazioni')
        self.sql_crea_punti = yaml_sql.getValueFromYaml('sql_crea_punti')
        self.sql_exist = yaml_sql.getValueFromYaml('sql_exist_position')
        self.sql_insert = yaml_sql.getValueFromYaml('sql_insert_position')
        self.sql_insert_data = yaml_sql.getValueFromYaml('sql_insert_data_anomaly')
        self.range_x = yaml.getValueFromYaml("range_x")
        self.range_y = yaml.getValueFromYaml("range_y")
        self.range_x_medie = yaml.getValueFromYaml('range_x_medie')
        self.range_y_medie = yaml.getValueFromYaml('range_y_medie')
        self.yaml_maps = yaml_maps
    
    #Quando finiscono le misurazioni inizia l'esecuzione
    def callback_end ( self , data ) :
        time.sleep(5)
        #self.cleanData(data)
        self.cleanData("11/02/2022 10:15:00-11/02/2022 10:30:00")

    def chiudiConnessione ( self ) :
        self.db_persistence.close_db()
        
    def inizializza (self) :
        self.db_persistence = Db_Persistence()
        rospy.init_node("Clean_Date_On_Db" , anonymous = True)
        #self.publisher = rospy.Publisher("Start" , Bool , queue_size = 4)
        rospy.Subscriber("End" , String , self.callback_end )
        #self.creaTabellaTemporanea()
        rospy.spin()
    
    #Metodo se volessimo creare una tabella temporanea che contiene i dati da misurare per poi
    #Cancellarla e mantenere solamente i dati in una tabella con i dati clean
    def creaTabellaTemporanea ( self ) :
        self.db_persistence.connect_db()
        sqlMisurazioni = self.sql_crea_misure.format(self.misureTemporanea)
        sqlPunti = self.sql_crea_punti.format(self.puntiTemporanea)
        #print(sqlMisurazioni)
        #print(sqlPunti)
        self.db_persistence.creaTabella(sqlPunti)
        self.db_persistence.creaTabella(sqlMisurazioni)
        self.publisher.publish(True)
        self.chiudiConnessione()

    #Metodo che crea un punto medio con valori misurati con media aritmetica con una lista di punti
    #Presenti in un range di valori
    def puntoMedio ( self , punti ) :
        new_punto = [ None , None ,None ,None ,None ,None ,None ,None ,None , None , None]
        #print(punti)
        for misurazione in punti :
            for i in range(0,self.numeroParametri+4) :
            #print(i)
                if new_punto[i] == None :
                    new_punto[i] = misurazione.getValueAtIndex(i)
                else :
                    if i != 2 and i != 3 :
                        new_punto[i] = new_punto[i] + misurazione.getValueAtIndex(i)
        for i in range(0,self.numeroParametri+4) :
            #print(new_punto[i])
            if i != 2 and i != 3 :
                new_punto[i] = new_punto[i] / len(punti)
                new_punto[i] = round(new_punto[i],3)
                #Arrotondamento a 2 cifre decimali
                #print(new_punto[i])
        return Misurazione(new_punto,self.numeroParametri)

    def puntoMedioPonderata ( self , punti ) :
        new_punto = [ None , None ,None ,None ,None ,None ,None ,None ,None , None , None]
        #print(punti)
        cAnomalie = 0
        for misurazione in punti :
            weight = 1
            if misurazione.isAnomaly() :
                cAnomalie = cAnomalie + 1
                weight = self.weightAnomaly
            for i in range(0,self.numeroParametri+4) :
            #print(i)
                if new_punto[i] == None :
                    if i > 3 :
                        new_punto[i] = misurazione.getValueAtIndex(i) * weight
                    else : 
                        new_punto[i] = misurazione.getValueAtIndex(i)
                else :
                    if i > 3 :
                        new_punto[i] = new_punto[i] + (misurazione.getValueAtIndex(i) * weight)
                    elif i < 2 :
                        new_punto[i] = new_punto[i] + misurazione.getValueAtIndex(i)
        normali = len(punti) - cAnomalie
        tot = normali + (cAnomalie * self.weightAnomaly)
        for i in range(0,self.numeroParametri+4) :
            #print(new_punto[i])
            if i > 3 :
                new_punto[i] = new_punto[i] / tot
                new_punto[i] = round(new_punto[i],3)
                #Arrotondamento a 2 cifre decimali
                #print(new_punto[i])
            elif i < 2 :
                new_punto[i] = new_punto[i] / len(punti)
                new_punto[i] = round(new_punto[i],3)
        return Misurazione(new_punto) 

    def convertiInMisurazioni( self , punti ) :
        convertiti = []
        for misurazione in punti :
            convertiti = convertiti + [Misurazione(misurazione,self.numeroParametri)]
        return convertiti

    def merge( self, punti ) :
        if len(punti) == 0 :
            return [ ]
        elif len(punti) == 1 :
            return punti
        else :
            misurazione = self.puntoMedio(punti)
        return [ misurazione ] 

    #Metodo che verifica se sul db esiste già quella posizione
    def position_exist ( self ,x , y ) :
        sql = self.sql_exist.format(self.puntiClean,x,y)
        #print(sql)
        id_tuple = self.db_persistence.select_query(sql)
        return id_tuple

    #Metodo che crea posizione sul db
    def create_position ( self ,x , y ) :
        sql = self.sql_insert.format(self.puntiClean,x,y)
        #print(sql)
        id = self.db_persistence.insert_database(sql)
        return id

    def save_date ( self , isAnomaly , listAnomaly , id_pos , misurazioni , giorno , orario ) : 
        sql = self.sql_insert_data.format(self.misureClean,misurazioni[0],giorno,orario,id_pos,isAnomaly , listAnomaly , misurazioni[1],misurazioni[2],misurazioni[3],misurazioni[4],misurazioni[5],misurazioni[6])
        #print(sql)
        id = self.db_persistence.insert_database(sql)
        return id

    def save_on_db ( self ) :
        for misurazione in self.def_point :
            punto = [ misurazione.getValueAtIndex(0) , misurazione.getValueAtIndex(1) ]
            id_tupla = self.position_exist(punto[0],punto[1])
            if id_tupla == None :
                id_tupla = self.create_position(punto[0],punto[1])
            self.save_date( misurazione.isAnomaly() , misurazione.getListParametersAnomaly() , id_tupla[0] , misurazione.buildArrayMisurazione() , misurazione.getValueAtIndex(2) , misurazione.getValueAtIndex(3))

    def cambiaValori ( self , lista ) :
        if len(lista) == 0 :
            return []
        elif len(lista) == 1 :
            return [lista[0]]
        else :
            punto = self.puntoMedioPonderata(lista)
            for misurazione in lista :
                misurazione.changeValuesMedia(punto)
            return lista

    def mediazioneValori(self , def_point ) :
        medie = []
        for i in range(self.min_x , self.max_x , self.range_x_medie ) :
            for j in range (self.min_y , self.max_y , self.range_y_medie ) :
                lista = []
                for misurazione in def_point :
                    if (i - self.range_x_medie < misurazione.getValueAtIndex(0) ) and  (misurazione.getValueAtIndex(0) < i + self.range_x_medie) and  (j - self.range_y_medie< misurazione.getValueAtIndex(1)) and  (misurazione.getValueAtIndex(1) < j+self.range_y_medie):
                        #print("Tre:" + str(m))
                        lista = lista + [misurazione]
                medie = medie + self.cambiaValori(lista)
        return medie

    def anomaly_detection ( self , medio , punti ) :
        anomaly = []
        for misurazione in punti :
            for i in range ( 4 , self.numeroParametri + 4 ) :
                if  misurazione.getValueAtIndex(i) > medio.getValueAtIndex(i)+self.thresholds[i] :
                    misurazione.setAnomaly(i,"hight")
                    anomaly = anomaly + [misurazione]
                elif misurazione.getValueAtIndex(i) < medio.getValueAtIndex(i)-self.thresholds[i] :
                    misurazione.setAnomaly(i,"low")
                    anomaly = anomaly + [misurazione]
        return anomaly

    def modify_merged ( self , anomaly , merged ) :
        contaLow = [ 0 ,0 ,0 ,0 ,0 ,0 ,0 ]
        contaHigh = [ 0 ,0 ,0 ,0 ,0 ,0 ,0 ]
        valori = [ [] , [] ,[] ,[] ,[] ,[] ,[] ]
        for anom in anomaly :
            #print(anom)
            for ril in (anom.getListAnomaly()) :
                valori[ril[0]-4] = valori[ril[0]-4] + [anom.getValueAtIndex(ril[0])]
                if ril[1] == "low" :
                    contaLow[ril[0]-4] = contaLow[ril[0]-4] + 1
                else : 
                    contaHigh[ril[0]-4] = contaHigh[ril[0]-4] + 1
        for i in range(6) :
            if len(valori[i]) != 0 :
                max_an = max(contaHigh[i],contaLow[i])
                if max_an == contaHigh[i] :
                    max_val = max(valori[i])
                    #print(("Cambiato valore da {} a {} ").format(merged.getValueAtIndex(i+4) , max_val ))
                    merged.setValueAtIndex(i+4 , max_val )
                    merged.setAnomaly(i+4,"hight")
                else :
                    min_val = min(valori[i])
                    #print(("Cambiato valore da {} a {} ").format(merged.getValueAtIndex(i+4) , min_val ))
                    merged.setValueAtIndex(i+4 , min_val)
                    merged.setAnomaly(i+4,"low")


    def carica_mappa_icons ( self ) :
        dirname = os.path.dirname(__file__) #src/sensor/src/sensor/node/db_cleaner
        index = dirname.find("/src/sensor_omron/")
        pathTmp = dirname[:index]
        self.path = pathTmp + "/src/sensor_omron/resources/"
        pathMap = self.path + "map/output/" + self.nome_map
        pathIcon = self.path + "icon/"
        pathLux = pathIcon + self.icon_lux
        pathTher = pathIcon + self.icon_therm
        pathWar = pathIcon + self.icon_warning
        #print(pathMap)
        self.mappa = cv.imread(pathMap,cv.IMREAD_UNCHANGED)
        #print(self.mappa)
        #print(pathLux)
        self.light_icon = cv.imread(pathLux,cv.IMREAD_UNCHANGED)
        #print(light_icon)
        self.therm_icon = cv.imread(pathTher,cv.IMREAD_UNCHANGED)
        self.warn_icon = cv.imread(pathWar,cv.IMREAD_UNCHANGED)

    def create_map_anomaly ( self ) :
        #0 x 1 y 4 temp 6 light
        self.carica_mappa_icons()
        self.build_map = Build_Map(self.yaml_maps)
        for misurazione in self.def_point :
            if misurazione.isAnomaly() :
                x = misurazione.getValueAtIndex(0)
                y = misurazione.getValueAtIndex(1)
                x = self.build_map.convertCoordinatesOnPixel(x , "x")
                y = self.build_map.convertCoordinatesOnPixel(y , "y")
                icon = self.warn_icon
                #print(misurazione.getListParametersAnomaly())
                if "4" in misurazione.getListParametersAnomaly() :
                    icon = self.therm_icon
                elif "6" in misurazione.getListParametersAnomaly() :
                    icon = self.light_icon
                shape_icon = icon.shape  #width 1 hight 0
                min_y = y-int(shape_icon[0]/2)
                max_y = y+int(shape_icon[0]/2)+1
                min_x = x-int(shape_icon[1]/2)
                max_x = x+int(shape_icon[1]/2)+1
                result = np.zeros(shape_icon, np.uint8)
                alpha = icon[:, :, 3] / 255.0
                result[:, :, 0] = (1. - alpha) * self.mappa[min_y:max_y,min_x:max_x, 0] + alpha * icon[:, :, 0]
                result[:, :, 1] = (1. - alpha) * self.mappa[min_y:max_y,min_x:max_x, 1] + alpha * icon[:, :, 1]
                result[:, :, 2] = (1. - alpha) * self.mappa[min_y:max_y,min_x:max_x, 2] + alpha * icon[:, :, 2]
                result[:,:,3] = 255
                self.mappa[min_y:max_y,min_x:max_x] = result
        path = self.path + "map/output/Maps_Anomalies"
        os.makedirs(path, exist_ok  = True)

        tmp = self.inizio[0].split("/")
        data_path = "{}_{}_{}".format(tmp[0],tmp[1],tmp[2])
        tmp = self.inizio[1].split(":")
        data_path = data_path + "-{}_{}_{}".format(tmp[0],tmp[1],tmp[2])
        
        filePath = path + "/Anomaly_{}.png".format(data_path)
        mappa = cv.cvtColor(self.mappa, cv.COLOR_BGR2RGBA)
        image = Image.fromarray(mappa) 
        image.save(filePath)
        print("Mappa Anomalie salvata in " + filePath)
        
    def cleanData ( self , data ) :
        self.db_persistence.connect_db()
        self.def_point = []
        self.anomaly = []
        #date = data.data.split("-")
        date = data.split("-")
        self.inizio = date[0].split(" ")
        self.fine = date[1].split(" ")

        sql = self.sql_max_min.format(self.puntiTemporanea,self.misureTemporanea,self.puntiTemporanea,self.misureTemporanea,self.inizio[0],self.fine[0],self.inizio[1],self.fine[1])
        maxAndMin = self.db_persistence.select_query_list(sql)[0]
        #print(sql)
        self.min_x = maxAndMin[0]
        self.min_y = maxAndMin[2]
        self.max_x = maxAndMin[1]
        self.max_y = maxAndMin[3]

        print("Scansiono Punti Sul Db Per approssimareli..")
        for i in range(self.min_x , self.max_x , self.range_x ) :
            for j in range (self.min_y , self.max_y , self.range_y ) :
                #print ( str(i) + " " + str(j))
                tmp = self.sql_query_range.format(self.puntiTemporanea,self.misureTemporanea,self.misureTemporanea,self.puntiTemporanea,self.inizio[0],self.fine[0],self.inizio[1],self.fine[1],i,i+self.range_x,j,j+self.range_y)
                #print(sqlRange)
                punti = self.db_persistence.select_query_list(tmp)
                punti = self.convertiInMisurazioni(punti)
                merged = self.merge(punti)

                anomaly_near = []
                if len(punti) != 0 and len(punti) != 1 :
                    anomaly_near = self.anomaly_detection(merged[0] , punti )
                    self.anomaly = self.anomaly + anomaly_near

                if len(anomaly_near) != 0 :
                    self.modify_merged(anomaly_near , merged[0] )

                self.def_point = self.def_point + merged

        print("Fine approssimazione , punti generati : %s" , len(self.def_point) )
        self.anomaly = list(set(self.anomaly))
        print("Anomalie Detectate : {}".format(len(self.anomaly)))

        print("Inizio Mediazione Valori")
        self.def_point = self.mediazioneValori(self.def_point)
        print("Fine Mediazione Valori")

        #Elimina Duplicati
        self.def_point = list(set(self.def_point))

        print("Dimensione Lista Post processo : %s " , len(self.def_point))

        if len(self.anomaly) != 0 :
            self.create_map_anomaly()

        #print(len(def_point))
        self.save_on_db()

        rospy.signal_shutdown("Clear effettuato")

if __name__ == "__main__" :
    try :
        dirname = os.path.dirname(__file__) #src/sensor/src/sensor/node/reader
        index = dirname.find("/src/sensor_omron/")
        path = dirname[:index]
        path = path + "/src/sensor_omron/cfg"
        os.chdir(path)
        yaml_sql = Read_Yaml_File("config_sql.yaml")
        yaml = Read_Yaml_File("config_param_posit.yaml")
        yaml_maps = Read_Yaml_File("config_maps.yaml")
        os.chdir(dirname)
        db_cleaner = Db_Cleaner( yaml_sql , yaml , yaml_maps)
        db_cleaner.inizializza()
    except Exception as e :
        print(e)
    finally :
        try :
            db_cleaner.chiudiConnessione()
        except AttributeError :
            pass    

