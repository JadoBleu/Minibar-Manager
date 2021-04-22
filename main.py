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
from getpass import getpass
from mysql.connector import connect, Error

try:
    with connect(
        host=config["host"],
        user=config["user"],
        password=config["password"],
    ) as connection:
        print(connection)
except Error as e:
    print(e)
