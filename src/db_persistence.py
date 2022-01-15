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
def select_query ( sql ) :
    try : 
        cursor = conn.cursor()
        cursor.execute(sql)
        id = cursor.fetchone()
        cursor.close()
        return id
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    
#Sql is a string that contain a SQL string
def insert_database ( sql ) :
    try :
        cursor = conn.cursor()
        cursor.execute(sql)
        id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        return id
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)