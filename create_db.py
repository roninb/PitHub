# this file creates the db and populates the database with dummy data
import sqlite3
import sys
import subprocess
from datetime import datetime

# creating database from schema
output = subprocess.call("sqlite3 pithub.db < pithub.sql", shell=True)

# database connection object
connection = None

# putting everything in a try so that it doesn't break the shit out of the
# database if I typoed something, as is often the case
try:
    connection = sqlite3.connect('pithub.db')
    cursor = connection.cursor()

    cursor.execute("INSERT INTO user VALUES(NULL, 'roninb', '1234', 'roninb')")
    cursor.execute("INSERT INTO repo VALUES(NULL, 'PitHub', 0, 1)")
    cursor.execute("INSERT INTO pit VALUES(NULL, 'black', 4, ?, 1)", (datetime.now(),))
    connection.commit()

    cursor.execute("SELECT * from user")
    rows = cursor.fetchall()
    for row in rows:
        print row

    cursor.execute("SELECT * from repo")
    rows = cursor.fetchall()
    for row in rows:
        print row

    cursor.execute("SELECT * from pit")
    rows = cursor.fetchall()
    for row in rows:
        print row

except sqlite3.Error, e:
    print "Error: %s." % e.args[0]
    sys.exit(1)

finally:
    if connection:
        connection.close()
