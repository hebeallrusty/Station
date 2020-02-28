# station

Station is a Weather Station that polls data from OpenWeatherMap and gets real world Temperature, Pressure and Humidity data from a BME280 on an i2c interface, and a Texas Instruments Sensortag using Bluetooth.

Station also generates useful information such as Sun rise / set and moon phase and presents all the information on a local webpage on it's own server (using Python Flask)

Station is incomplete and currently won't run as-is, and is having the individual modules amended / tweaked before the webpage will work again. Also webpage will need re-writing to take account of module changes and design changes

Original Station started life in Dec 2015 as a way to learn how to code in Python, and had been happily running since then, but the weather module has broken due to changes in the weather data provider no longer providing data

Requires the following modules installed:

matplotlib
adafruit-circuitpython-bme280 (sudo pip3 install adafruit-circuitpython-bme280)
python 3.6
bluepy (sudo apt install libglib2.0-dev; sudo pip3 install bluepy)


_______________________
Notes:

key.ini - for api keys, file should look like the following:

[OpenWeatherMap]
API_Key=******************

where * represent the api key and should reside in /config file as key.ini


database files

Sensor Database
	Each Sensor should have its own table, with table name as sensor. Project is intended to have two sensors - a SensorTag bluetooth (wireless) one and a BME280 attached to the main unit (wired sensor).
	Future plans may increase wired sensors with additional "base stations"
	
	tables:
		SENORTAG_1
		BME_280_1
	fields:
		ID (ID Integer)
		TTIme (Timestamp, not null, default current_timestamp)
		Temperature (Real)
		Humidity (Real)
		Pressure(Real)
		

