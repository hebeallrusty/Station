# from adafruit website
import board
import busio
import adafruit_bme280

from app.modules.Database.DBUtils import *
from app.modules.Utilities.PressureCalc import *

# for sleeping the module
import time

from math import exp

# for reading config files
import configparser
import os

CWD = os.getcwd()

# config file location
CONFIG_FILE=''.join([CWD,'/config/config.ini'])

# get info from config file
config = configparser.ConfigParser()
config._interpolation = configparser.ExtendedInterpolation()
config.read(CONFIG_FILE)

# database location
DATABASE = ''.join([CWD,config.get('files','SensorDatabase')])
print(DATABASE)

# altitude for sea-level calcs later on
MSL = int(config.get('location','MetersAboveSeaLevel'))

# how often script should run (sleep time)
UPDATE_INTERVAL = int(config.get('general','UpdateInterval'))


# from adafruit website
i2c = busio.I2C(board.SCL, board.SDA)
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)

# bme280 object can now be referenced for the sensor values


var = 1
# start loop
while var > 0:
	
	# commented out until it's possible to test on actual hardware
	
	temperature = bme280.temperature
	pressure = bme280.pressure
	humidity = bme280.humidity

	# debug values - until tested on actual hardware with sensor
	#temperature = 25
	#pressure = 1005
	#humidity = 45
	
	#Adjust for sea level
	#SeaLevelPressure = pressure / exp((-MSL) / ((temperature + 273.15) * 29.263)) # adjust for sea level
	SeaLevelPressure = SeaLevel(MSL,pressure,temperature)

	# enter values into database	

	db = db_connect(DATABASE)
	insert_sensor(db, 'BME_280_1',temperature,humidity,SeaLevelPressure)
	db.commit()
	db.close
	print("done")
		
	# sleep before re-running the script
	time.sleep(UPDATE_INTERVAL)



