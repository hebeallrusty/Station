import bluepy
import time
#import sqlite3
#from math import exp
from app.modules.Utilities.PressureCalc import *
import configparser # for reading ini files
import os
from app.modules.Database.DBUtils import *

CWD = os.getcwd()

# Config file location has to be static
CONFIG_FILE=''.join([CWD,'/config/config.ini'])

#print("opening config file")
config = configparser.ConfigParser()
config._interpolation = configparser.ExtendedInterpolation()
# open config file
config.read(CONFIG_FILE)


# get MAC Address of SensorTag (in config file)
MAC_ADDRESS = config.get('SensorTag','MacAddress')

# get location of Sensor Database
DATABASE = ''.join([CWD,config.get('files','SensorDatabase')])

# get location of 
MSL = float(config.get('location','MetersAboveSeaLevel')) # Elevation above sea level

# how often script should run (sleep time)
UPDATE_INTERVAL = int(config.get('general','UpdateInterval'))


# connect to tag
tag=bluepy.sensortag.SensorTag(MAC_ADDRESS)
var=1

# if tag disconnects midway through processes, then very likely the tag connection has been disrupted and recovery is not likely
try:
	# loop to keep getting data from the Sensortag
	while var > 0:
		# enable sensors - temperature is included within barometer and humidity
		tag.humidity.enable()
		tag.barometer.enable()
		# enable time for notifications and also for the sensor to take measurements
		#time.sleep(1.0)
		tag.waitForNotifications(1.0)
	
		# read sensor data and assign it a variable
		# both humidity and pressure have their first value as the temperature. Temperature differs slightly between them. Take humidity's value.
		humidity = tag.humidity.read()

		# value is (temperature, humidity)
		pressure = tag.barometer.read()
		# value is (temperature, pressure). Pressure is local pressure and needs adjusted back to sea level so that it is comparable to met office values for example.
		SeaPressure = SeaLevel(MSL,pressure[1],humidity[0])
		
		# insert sensor values into database
		db = db_connect(DATABASE)
		insert_sensor(db, 'SENSORTAG_1',humidity[0],humidity[1],SeaPressure)
		db.commit()
		db.close		

		
		#shutdown the sensors until next iteration
		tag.humidity.disable()
		tag.barometer.disable()
		
		time.sleep(UPDATE_INTERVAL)
except:
	# disconnect from the sensor
	tag.disconnect()
	# remove reference
	del tag	
	# disconnect from the sensor

