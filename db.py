# Create a database
import sqlite3

conn = sqlite3.connect('database.db')
print ("Opened database successfully")
conn.execute('CREATE TABLE reviews (ID INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT, review TEXT, pred TEXT,feedback TEXT)')
print ("Table created successfully")
conn.close()