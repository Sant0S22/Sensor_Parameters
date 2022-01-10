#!/usr/bin/env python

import rospy
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


if __name__ = "__main__" :
	try :
		connect_db()
	except rospy.ROSInterruptException :
		pass