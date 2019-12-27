# station

Requires the following modules installed:

matplotlib
adafruit-circuitpython-bme280 (sudo pip3 install adafruit-circuitpython-bme280)
python 3.6


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
		1SENORTAG
		2BME_280
	fields:
		ID (ID Integer)
		TTIme (Timestamp, not null, default current_timestamp)
		Temperature (Real)
		Humidity (Real)
		Pressure(Real)
		

