import sqlite3
import re #regex

# since db can be dangerous, only allow a-z, 0-9 and _ in table names
RE_STRING='[^A-Za-z0-9_]+'

def safe_table(table):
	# remove special characters in table names (exc underscore)
	return re.sub(RE_STRING, '',table)

# create database connection
def db_connect(db_path):
	# start the connection and return the object
	con = sqlite3.connect(db_path)
	return con


def insert_sensor(con, table, temperature = None,humidity = None,pressure = None):
	# make table name safe just in case of sql injection
	SafeTable = safe_table(table)
	
	# sql statement to insert data into sensor db. Allow table name to be passed as argument for efficiency
	sql = 'Insert into ' + SafeTable + '(Temperature, Humidity, Pressure) values (?, ?, ?);'
	print(sql)
	cur = con.cursor()	

	# execute sql statement and insert data into database
	cur.execute(sql,(temperature,humidity,pressure))

	return cur.lastrowid

def insert_weather(con,table, temperature = None, humidity = None, pressure = None, condition = None, windspeed = None, windbearing = None, uvindex = None):
	# sanitise table name in case of SQL injection	
	SafeTable = safe_table(table)
	
	sql = 'Insert into ' + SafeTable + '(Temperature, Humidity, Pressure, Condition, WindSpeed, WindBearing, UVIndex) values (?, ?, ?, ?, ?, ?, ?);'
	print(sql)

	cur = con.cursor()

	print(temperature, humidity, pressure, condition, windspeed, windbearing, uvindex)

	# execute sql statement and insert data into database
	cur.execute(sql,(temperature, humidity, pressure, condition, windspeed, windbearing, uvindex))

	return cur.lastrowid

def read_sensor(con,table,StartTime,EndTime):
	# sanitise table name in case of SQL injection	
	SafeTable = safe_table(table)

	cur = con.cursor()
	sql = "Select datetime(TTime,'localtime'),Temperature,Humidity,Pressure from " + SafeTable + " where datetime(TTime,'localtime') between ? and ?;"
	cur.execute(sql,(StartTime, EndTime))
	
	return cur.fetchall()

def read_weather(con,table,StartTime,EndTime):
	# sanitise table name in case of SQL injection	
	SafeTable = safe_table(table)

	cur = con.cursor()	

	sql = "Select datetime(TTime,'localtime'),Temperature from " + SafeTable + " where datetime(TTime,'localtime') between ? and ?;"
	cur.execute(sql,(StartTime,EndTime))

	return cur.fetchall()


