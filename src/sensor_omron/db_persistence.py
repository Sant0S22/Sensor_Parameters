#!/usr/bin/env python3

import psycopg2
from sensor_omron.config_db import config

class Db_Persistence :
	'''Classe Utilizzata per interagire su database di tipo PostgreSql'''

	#Carico Parametri da file database.ini
	def __init__ ( self ) :
		self.params = config()

	#Connetto al db tramite parametri del file database.ini
	def connect_db( self ) :
		print("*****************************************")
		print("*Connecting to The PostgreSQL Database..*")
		print("*****************************************")
		self.conn = psycopg2.connect(**self.params)
	
	#Chiudo Connessione al DB	
	def close_db( self ) :
		self.conn.close()

	#Metodo che effetta una query su singola tupla
	def select_query ( self , sql ) :
		cursor = self.conn.cursor()
		cursor.execute(sql)
		id = cursor.fetchone() #Restituisce una sola tupla della ricerca o null 
		cursor.close()
		return id

	#Metodo che effettua una query su una lista di tuple
	def select_query_list ( self , sql ) :
		cursor = self.conn.cursor()
		cursor.execute(sql)
		lista = cursor.fetchall() #Restituisce lista di tuple
		cursor.close()
		return lista

	#Metodo che inserisce una nuova tupla sul database e restituisce id
	#ATTENZIONE : Ricordati di inserire SEMPRE dopo la stringa sql RETURNING id; altrimenti lancia eccezione
	def insert_database( self , sql ) :
		cursor = self.conn.cursor()
		cursor.execute(sql)
		id_tuple = cursor.fetchone() #Ritorna id della tupla se inserita
		self.conn.commit()
		cursor.close()
		return id_tuple


	def crea_tabella (self , sql ) :
		cursor = self.conn.cursor()
		cursor.execute(sql)
		self.conn.commit()
		cursor.close()

	