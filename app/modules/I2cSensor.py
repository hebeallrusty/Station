from app.Adafruit_BME280 import *
import time
import sqlite3
from math import exp

# database connection
DATABASE='/home/pi/Python/station/app/db/sensor.db'
MSL=194 # Elevation above sea level

#connect to wired sensor
sensor = BME280(mode=BME280_OSAMPLE_8)
var=1
# start loop
while var > 0:
	degrees = sensor.read_temperature()
	pascals = sensor.read_pressure()
	Pressure = pascals / 100
	humidity = sensor.read_humidity()

	#Adjust for sea level
	pressure=Pressure/exp((-MSL)/((degrees+273.15)*29.263)) # adjust for sea level

	try:
		db=sqlite3.connect(DATABASE)
		c=db.cursor()
		c.execute("Insert into Wired(Temperature, Humidity, Pressure) values (?, ?, ?);",(float(degrees), float(humidity), float(pressure)))
		db.commit()
		db.close
		#	#failure=-1
	except:
		failure=2
		db.rollback
		db.close	
		#print(Temperature)
		#print(Humidity)
		#print(Pressure)	
		
		var=var+1
		# wait for 10 secs for the next iteration
	time.sleep(600)



