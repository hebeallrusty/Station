print("loading modules")
import time
#start_time=time.time()
import matplotlib
import matplotlib.pyplot as plt
# allow matplotlib to render pngs
matplotlib.use('Agg')
import datetime as dt
import matplotlib.dates as mdates
from configparser import SafeConfigParser
import os
from app.modules.Database.DBUtils import *
print("done loading modules")

# Config file location has to be static
CONFIG_FILE=os.path.expanduser('~/Station/config/config.ini')

print("opening config file")
config = SafeConfigParser()
# print(CONFIG_FILE)
config.read(CONFIG_FILE)


print("setting location of files")
#databases
# to do - get database locations from config file
SENSOR_DATABASE=config.get('files','SensorDatabase')
WEATHER_DATABASE=config.get('files','WeatherDatabase')
GRAPH_ROOT=config.get('folder','Graph')

print(SENSOR_DATABASE)

print("setting variables")

# variables

HistHours = abs(int(config.get('plotting','HistoryHours'))) # to do make configurable in config file. Make sure it's positive too
# print(HistHours)

# how often script should run (sleep time)
UPDATE_INTERVAL = int(config.get('general','UpdateInterval'))

var = 1

while var > 0:
	# we only want to look at data from the database from the last x hours, so create two datetime objects, one for this moment now, and one from 6hrs ago. Remove the microseconds as this creates issues later on

	# NOW
	oDateNow = dt.datetime.now().replace(microsecond=0)

	# PREV - this provides the history of the graphs
	oDatePrev = oDateNow - dt.timedelta(hours=HistHours)
	#############################################
	# connect to sensor databas
# connect to the sensor database and return the sensor data we need. The timestamps in the database are always GMT/UTC
	db = db_connect(SENSOR_DATABASE)
	# c=db.cursor()
	# read from wired sensor database
	WiredOutput = read_sensor(db,"BME_280_1",oDatePrev,oDateNow)
	#print(WiredOutput[0])

	# read from wireless sensor database
	WirelessOutput = read_sensor(db,"SENSORTAG_1",oDatePrev,oDateNow)	
	#print(WirelessOutput[0])

	print("recevied results from Sensor DB")
	db.close

# dito weather database
	db = db_connect(WEATHER_DATABASE)
	WeatherOutput = read_weather(db,"Current",oDatePrev,oDateNow)
	# print(WeatherOutput)
	db.close

	print("recevied results from Weather DB")

	# now we have objects:
	#	WirelessOutput(Date & Time, Temperature, Humidity, Pressure)
	#	WiredOutput(Date & Time, Temperature, Humidity, Pressure)
	#	WeatherOutput(Date & Time, Actual Temperature outside)
	# containing data from databases.

	print("loop ended")
	var = 0

	# create 2d list for sensor data as it's the same for both wired and wireless data. [wired:wireless]
	#print(WeatherOutput)

	print("convert output to manageable variables")	
	# print(list(zip(*WiredOutput))[0])
	# transpose rows to columns so that we can easily take all dates, all humidity's and all pressures from output from database

	print("wiredoutput",WiredOutput)
	print("wirelessoutput",WirelessOutput)
	SensorDate=[list(zip(*WiredOutput))[0],list(zip(*WirelessOutput))[0]]
	# print(SensorDate)

	SensorTemperature=[list(zip(*WiredOutput))[1],list(zip(*WirelessOutput))[1]]
	# print(SensorTemperature)

	SensorHumidity=[list(zip(*WiredOutput))[2],list(zip(*WirelessOutput))[2]]
	# print(SensorHumidity)
	
	SensorPressure=[list(zip(*WiredOutput))[3],list(zip(*WirelessOutput))[3]]
	# print(SensorPressure)

	WeatherDate=list(zip(*WeatherOutput))[0]
	# print(WeatherDate)

	WeatherTemperature=list(zip(*WeatherOutput))[1]
	# print(WeatherTemperature)

	print("fixing date text to datetime objects")

	# Now we have all the elements to produce graphs (x and y axes), however the date/times are text and not datetime objects which means the matplotlib doesn't know what dates/times go after each other. Data is ordered however.

	oSensorDate=[0,0]

	for x in range(0,2):
		oSensorDate[x]= [dt.datetime.strptime(d,'%Y-%m-%d %H:%M:%S') for d in SensorDate[x]]
	
	# print(oSensorDate)

	# ditto for weather dates. Place back inside own list
	
	oWeatherDate = [dt.datetime.strptime(d,'%Y-%m-%d %H:%M:%S') for d in WeatherDate]

	# print(oWeatherDate)

	# make the plot

	# format for x-axis times
	xfmt=mdates.DateFormatter('%H:%M')

	# make a list of keywords, arguments so that a loop can be used to execute the graphing code
	
	# format: x axis data, y axis data, xlabel, y label, title, filename	
	# order: Wired Sensor Temp, Wireless Sensor Temp, Wired Sensor Humidity, Wireless Sensor Humidity, Wired Sensor Pressure, Wireless Sensor Pressure, Weather Data

	print("Creating Graphs")	

	kwords=[[oSensorDate[0],SensorTemperature[0],'Time','Deg C','Wired Sensor Temperature','wiredtemperature'], \
	[oSensorDate[1],SensorTemperature[1],'Time','Deg C','Wireless Sensor Temperature','wirelesstemperature'], \
	[oSensorDate[0],SensorHumidity[0],'Time','%','Wired Sensor Humidity','wiredhumidity'], \
	[oSensorDate[1],SensorHumidity[1],'Time','%','Wireless Sensor Humidity','wirelesshumidity'], \
	[oSensorDate[0],SensorPressure[0],'Time','Millibar','Wired Sensor Pressure','wiredpressure'], \
	[oSensorDate[1],SensorPressure[1],'Time','Millibar','Wireless Sensor Pressure','wirelesspressure'], \
	[oWeatherDate, WeatherTemperature,'Time','Deg C', 'Weather Temperature','weathertemperature']]
	#print(kwords[0][2])
	for k in range(0,7):
		fig, ax = plt.subplots()
		# assemble the x and y data
		ax.plot(kwords[k][0],kwords[k][1])

		ax.set(xlabel=kwords[k][2], ylabel=kwords[k][3], title=kwords[k][4])
		# put on grid lines
		ax.grid()
		# make the dates look nice on the x axis
		plt.gcf().autofmt_xdate()
		# use the textual format set earlier
		plt.gca().xaxis.set_major_formatter(xfmt)
		# save the plot with narrow border
		fig.savefig(''.join([GRAPH_ROOT,kwords[k][5],'.png']),bbox_inches='tight')
		#plt.show()
		#print("Graph ", kwords[k][5], " saved")
	
	#print(time.time()-start_time)	
	var=1
	time.sleep(UPDATE_INTERVAL)

