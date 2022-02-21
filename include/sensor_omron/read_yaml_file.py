#!/usr/bin/env python3

import yaml

class Read_Yaml_File :
    '''Classe Creata per interagire con file di configurazione .yaml'''

    #Carica contenuto file yaml in una mappa
    def __init__ ( self , nome_file ) :
        self.nome_file = nome_file
        file = open( nome_file , "r" )
        self.parametri = yaml.safe_load(file)

    #Restituisce valore della mappa corrispondente alla key passata per parametro
    def getValueFromYaml ( self , key ) :
        try :
            return self.parametri[key]
        except KeyError :
            return None
