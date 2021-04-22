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
        # query to select and display all rows from recipe table for testing
        sqlQuery = "select * from minibarmanager.recipe"
        cursor = connection.cursor()
        cursor.execute(sqlQuery)
        records = cursor.fetchall()
        for row in records:
            print("recipeID: ", row[0],"\nrecipeName: ", row[1],"\ninstructions: ", row[2],
                "\ngarnish: ", row[3], "\nlike: ", row[4], "\ncomments: ", row[5],"\n\n")

except Error as e:
    print("error reading data from MySQL", e)

finally:
    # close the connection
    if connection.is_connected():
        connection.close()
        cursor.close()
        print("MySQL connection is closed")


