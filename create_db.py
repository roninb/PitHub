# this file creates the db and populates the database with dummy data
import sqlite3
import sys
import subprocess
from datetime import datetime

# creating database from schema
output = subprocess.call("sqlite3 pithub.db < pithub.sql", shell=True)

if output == None:
    print "Success!"
