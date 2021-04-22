#!/usr/bin/env python3
'''
    Rio Hondo College
    CIT 128: Python Programming II
    Student Directed Project
    Jefferson Wang
    Spring 2021
'''

from dotenv import dotenv_values
# config = {host='localhost', user = 'dbadmin', password = 'tester1234',  databse = 'testdb'}
config = dotenv_values(".env") 

import pymysql

# make the connection with the database
con = pymysql.connect(config['host'], config['user'], config['password'], config['database'])

try:

    with con.cursor() as cur:

        cur.execute('SELECT VERSION()')

        version = cur.fetchone()

        print(f'Database version: {version[0]}')

finally:

    con.close()

