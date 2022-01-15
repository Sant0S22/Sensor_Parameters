#!/usr/bin/env python

import psycopg2
from config_db import config

def connect_db() : 
	conn = None
    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
        return conn
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

#Sql is a string that contain a SQL string
#Remmeber that fetchone return a tuple and not a value
def select_query ( sql , conn ) :
    try : 
        cursor = conn.cursor()
        cursor.execute(sql)
        id = cursor.fetchone()
        cursor.close()
        return id
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    
#Sql is a string that contain a SQL string
#Remmeber that fetchone return a tuple and not a value
def insert_database ( sql , conn ) :
    try :
        cursor = conn.cursor()
        cursor.execute(sql)
        id = cursor.fetchone()
        conn.commit()
        cursor.close()
        return id
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

#Sql is a string that contain a SQL string
#Remmeber that fetchall return a list of tuple and not values
def select_query_list ( sql , conn ) :
    try : 
        cursor = conn.cursor()
        cursor.execute(sql)
        list = cursor.fetchall()
        cursor.close()
        return list
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)