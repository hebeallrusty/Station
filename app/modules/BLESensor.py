import bluepy
import time
import sqlite3
from math import exp

# if multiple tags are available - specify Mac addresses
MAC_LIVINGROOM='A0:E6:F8:B6:8C:80'
# database connection
DATABASE='/home/pi/Python/station/app/db/sensor.db'
MSL=194 # Elevation above sea level

try:
	# connect to tag
	tag=bluepy.sensortag.SensorTag(MAC_LIVINGROOM)
	var=1


	while var > 0:
		# enable sensors - temperature is included within barometer and humidity
		tag.humidity.enable()
		tag.barometer.enable()
		# enable time for notifications and also for the sensor to take measurements
		#time.sleep(1.0)
		tag.waitForNotifications(1.0)
	
		# read sensor data and assign it a variable
		humidity=tag.humidity.read()
		pressure=tag.barometer.read()
	
		#raw values as tuples - separate them out to meaningful variable names
		Temperature=pressure[0]
		Humidity=humidity[1]
		Pressure=pressure[1]/exp((-MSL)/((pressure[0]+273.15)*29.263)) # adjust for sea level
		print(pressure[0])
		print(pressure[1])
		try:
			db=sqlite3.connect(DATABASE)
			c=db.cursor()
			c.execute("Insert into LRoom(Temperature, Humidity, Pressure) values (?, ?, ?);",(float(Temperature), float(Humidity), float(Pressure)))
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
except:
	# disconnect from the sensor
	tag.disconnect()
	# remove reference
	del tag	
	# disconnect from the sensor

	
#print(humidity)
#print(pressure)
