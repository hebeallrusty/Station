print("loading modules")
import time
#start_time=time.time()
import matplotlib
import matplotlib.pyplot as plt
# allow matplotlib to render pngs
matplotlib.use('Agg')
import datetime as dt
import matplotlib.dates as mdates
from matplotlib.ticker import ScalarFormatter
import configparser
import os
from app.modules.Database.DBUtils import *
from modules.Sun.Sun import Sun
from modules.Sun.SunCurve import SunCurve
from modules.Utilities.DecimalTime import DecimalTime
from modules.Utilities.DaylightSavingTime import DaylightSavingTime
from modules.Utilities.LeapYear import LeapYear
print("done loading modules")

CWD = os.getcwd()

# Config file location has to be static
CONFIG_FILE=''.join([CWD,'/config/config.ini'])

print("opening config file")
config = configparser.ConfigParser()
config._interpolation = configparser.ExtendedInterpolation()
# print(CONFIG_FILE)
config.read(CONFIG_FILE)


print("setting location of files")
#databases
# to do - get database locations from config file
SENSOR_DATABASE = ''.join([CWD,config.get('files','SensorDatabase')])
WEATHER_DATABASE = ''.join([CWD,config.get('files','WeatherDatabase')])
GRAPH_ROOT = ''.join([CWD,config.get('folder','Graph')])

print(SENSOR_DATABASE)

print("setting variables")

# variables

HistHours = abs(int(config.get('plotting','HistoryHours')))

# print(HistHours)

# get location from config file
location = [float(config.get('location','latitude')), float(config.get('location','longitude'))]


# how often script should run (sleep time)
UPDATE_INTERVAL = int(config.get('general','UpdateInterval'))

var = 1

while var > 0:
	##########################################################################
	#####
	#####
	#####
	##### Sensors 
	#####
	#####
	
	# we only want to look at data from the database from the last x hours, so create two datetime objects, one for this moment now, and one from 6hrs ago. Remove the microseconds as this creates issues later on

	# NOW
	oDateNow = dt.datetime.now().replace(microsecond=0)

	# PREV - this provides the history of the graphs
	oDatePrev = oDateNow - dt.timedelta(hours=HistHours)
	#############################################
	# connect to sensor database
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
	# var = 0

	# create 2d list for sensor data as it's the same for both wired and wireless data. [wired:wireless]
	#print(WeatherOutput)

	print("convert output to manageable variables")	
	# print(list(zip(*WiredOutput))[0])
	# transpose rows to columns so that we can easily take all dates, all humidity's and all pressures from output from database

	#print("wiredoutput",WiredOutput)
	#print("wirelessoutput",WirelessOutput)
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
		#ax.yaxis.set_major_formatter(ScalarFormatter('%.0f'))
		# show non-scientific notation on y axis
		ax.ticklabel_format(useOffset=False, style='plain', axis='y')
		# save the plot with narrow border
		fig.savefig(''.join([GRAPH_ROOT,kwords[k][5],'.png']),bbox_inches='tight')
		#plt.show()
		#print("Graph ", kwords[k][5], " saved")
	
	#print(time.time()-start_time)	
	# close all the plots to save memory
	plt.close('all')
	print("End of Sensors code")
	##########################################################################
	#####
	#####
	#####
	##### Day Graph 
	#####
	#####
	now = dt.datetime.today() #- dt.timedelta(hours=6)
	DST = DaylightSavingTime(now)
	#print(DST)
	#print(now)

	# initiate the Sun module
	s = Sun(now,location,DST)

	#print(s.Rise()['Official'])

	# get sunrise and set times and convert to a datetime object

	today = dt.datetime(now.year,now.month,now.day,0,0,0)
	Sunrise = today + s.Rise()['Official']
	Sunset = today + s.Set()['Official']
	Dawn = today + s.Rise()['Civil']
	Dusk = today + s.Set()['Civil']
	Noon = today + s.Transit()
	GoldenRise = today + s.Rise()['Golden']
	GoldenSet = today + s.Set()['Golden']
	LengthOfDay = today + s.LengthOfDay()
	# DawnToDusk = today + (s.Set()['Civil'] - s.Rise()['Civil'])

	# datetime object allows individual attributes to be taken such as hour, minute and second. Convert to decimal format for calculations.

	dSunrise = DecimalTime(Sunrise) #Sunrise.hour + (Sunrise.minute / 60)
	dSunset = DecimalTime(Sunset) #Sunset.hour + (Sunrise.minute / 60)
	dLengthOfDay = DecimalTime(LengthOfDay) #LengthOfDay.hour + (LengthOfDay.minute / 60)
	dNow = DecimalTime(now) #now.hour + (now.minute / 60)
	dDawn = DecimalTime(Dawn) #Dawn.hour + (Dawn.minute / 60)
	dDusk = DecimalTime(Dusk) #Dusk.hour + (Dusk.minute / 60)
	dDawnToDusk = dDusk - dDawn
	#dNoon = Noon.hour + (Noon.minute / 60)


	# print(dSunrise,dSunset,dLengthOfDay)

	# create an array of times in the day

	xd = [] # datetime objects - for x-axis of graph
	xn = [] # time in decimal

	# x values will be at 15 minute intervals
	WhenIsNow = 0 # used to determine when "now" is reached in the x value array - used for shading
	# iterate the number of 15 min intervals between 0 and 3 hrs after the length of day
	for i in range (0,int((dDawnToDusk + 2)/(15/60))+1):
		#print(dDawnToDusk + 2)
		# start at 1 hr before Dawn and add 15mins and place into an array
		xval = dt.datetime(now.year,now.month,now.day,int(dDawn),0,0) + dt.timedelta(minutes=(i * 15))
		xd.append(xval)
		#print((xval.hour + (xval.minute / 60)),"<",dNow)
		# we need to know the index of when "now" is achieved for the shading logic
		if DecimalTime(xval) < dNow:
			WhenIsNow = WhenIsNow + 1
			#print(WhenIsNow)
		
		# Decimal version of time - allows calculation with sine curve	
		xn.append(DecimalTime(xd[i]))
		#print(xd[i].minute)
		#print("xval:", xval)	
		#print("i:",i)
		#print("WhenIsNow:",WhenIsNow)
	
	# create y values 
	#print(xd)
	y = [SunCurve(i,dSunrise,dLengthOfDay) for i in xn ]


	# logic for shading
	# create new set for x values based that ends at now. This is for shading up to now in teh graph
	# create x vals up to now for shading later on. Can be up to 15 mins short though
	# slice the array to include up to "now". It misses the current "now" so it'll need adding in
	xdnow = xd[:WhenIsNow]
	#print(xdnow)
	#print(xd)
	#print(xdnow)
	xdnow.append(dt.datetime(now.year,now.month,now.day,now.hour,now.minute,now.second)) # add in calc for now

	#print(xdnow)
	# create y values based on shortened x values up to now. Again can be one item short so it'll need adding
	y2 = y[:WhenIsNow]
	# add in last element for now
	y2.append(SunCurve(dNow,dSunrise,dLengthOfDay))
	#print(y2)

	# format how the times are to be displayed
	xfmt = mdates.DateFormatter('%H:%M')

	# matplotlib - create graph
	fig, ax = plt.subplots()

	# plot x and y values
	ax.plot(xd, y)

	# set the labels of the axes
	ax.set(xlabel=" ", ylabel=" ")

	# bound the graph so it doesn't show all negative values 
	ax.set_ylim([-0.25,1.1])

	# remove the labels on the y axis as they don't really mean anything and remove the frame of the graph
	ax.set_yticklabels([])
	ax.set_frame_on(False)
	ax.get_yaxis().set_ticks([])
	
	# show only vertical gridlines
	ax.grid(which='major', axis='x',linestyle='dotted')

	# put some lines on the plot
	# TODO - migrate properties into a variable to reduce chance of errors when updating code
	plt.axhline(y=0, color='black') # horizon
	plt.vlines(x=Dawn, ymin = -0.1, ymax = 0.1, color='grey')
	plt.vlines(x=Dusk, ymin = -0.1, ymax = 0.1, color='grey')
	plt.vlines(x=Noon, ymin = -0.1, ymax = 0.1, color='gold')
	plt.vlines(x=Sunrise, ymin = -0.1, ymax = 0.1, color='grey')
	plt.vlines(x=Sunset, ymin = -0.1, ymax = 0.1, color='grey')
	plt.vlines(x=GoldenRise, ymin = -0.1, ymax = 0.1, color='gold')
	plt.vlines(x=GoldenSet, ymin = -0.1, ymax = 0.1, color='gold')

	# only draw hour line if its 1 hours before Dawn and 1 hours after Dusk, otherwise the graph stretches to accommodate the hour line
	if (dNow > (dDawn - 1)) and (dNow < (dDusk + 1)):
	#print("within graph")
		plt.axvline(x=now, color='red') # time now

	# bound axis to 1 hrs before Dawn and 1 hours after Dusk
	ax.set_xlim(Dawn - dt.timedelta(hours=1),Dusk + dt.timedelta(hours=1))

	# add text to graph
	# TODO migrate some of the strings to functions
	ax.text(Dawn, 0.15, ''.join(['Dawn: ', str(Dawn.hour).zfill(2),":",str(Dawn.minute).zfill(2)]), ha='center', va='bottom', rotation=90)
	ax.text(Dusk, 0.15, ''.join(['Dusk: ', str(Dusk.hour).zfill(2),":",str(Dusk.minute).zfill(2)]), ha='center', va='bottom', rotation=90)
	ax.text(Noon, 0.15, ''.join(['Noon: ', str(Noon.hour).zfill(2),":",str(Noon.minute).zfill(2)]), ha='center', va='bottom', rotation=90)
	ax.text(Sunrise, 0.15, ''.join(['Sunrise: ', str(Sunrise.hour).zfill(2),":",str(Sunrise.minute).zfill(2)]), ha='center', va='bottom', rotation=90)
	ax.text(Sunset, 0.15, ''.join(['Sunset: ', str(Sunset.hour).zfill(2),":",str(Sunset.minute).zfill(2)]), ha='center', va='bottom', rotation=90)
	ax.text(GoldenRise, 0.15, ''.join(['Golden: ', str(GoldenRise.hour).zfill(2),":",str(GoldenRise.minute).zfill(2)]), ha='center', va='bottom', rotation=90)
	ax.text(GoldenSet, 0.15, ''.join(['Golden: ', str(GoldenSet.hour).zfill(2),":",str(GoldenSet.minute).zfill(2)]), ha='center', va='bottom', rotation=90)
	ax.text(Noon,1.1,''.join(['Length Of Day: ', str(LengthOfDay.hour).zfill(2),":",str(LengthOfDay.minute).zfill(2)]), ha='center', va='bottom')



	#shade graph as day progresses using adjusted curves

	plt.fill_between(xdnow, 0, y2,interpolate=True, color='skyblue')

	# autoformat the times


	# set x axis to show every month
	locator = mdates.HourLocator()
	plt.gca().xaxis.set_major_locator(locator)
	plt.gcf().autofmt_xdate()
	plt.gca().xaxis.set_major_formatter(xfmt)


	# save the plot
	fig.savefig(''.join([GRAPH_ROOT,'Day','.png']),bbox_inches='tight')
	# close all the plots to save memory
	plt.close('all')
	print("end of Day Graph code")

	##########################################################################
	#####
	#####
	#####
	##### Year Graph 
	#####
	#####

	now = dt.datetime.now()
	

	#get seasons
	
	SPRING = dt.datetime(now.year,int(config.get('seasons','Spring').split('/')[1]),int(config.get('seasons','Spring').split('/')[0]),0,0)
	#print(SPRING)
	SUMMER = dt.datetime(now.year,int(config.get('seasons','Summer').split('/')[1]),int(config.get('seasons','Summer').split('/')[0]),0,0)
	AUTUMN = dt.datetime(now.year,int(config.get('seasons','Autumn').split('/')[1]),int(config.get('seasons','Autumn').split('/')[0]),0,0)
	WINTER = dt.datetime(now.year,int(config.get('seasons','Winter').split('/')[1]),int(config.get('seasons','Winter').split('/')[0]),0,0)

	#print(Now)

	# initialise x values
	x = []

	# create an array of dates from 1st Jan this year to 31st Dec this year. LeapYear function returns 1 for a leap year and 0 for non-leap years so can be used to add the extra day in leap years. 
	for i in range(0,365+LeapYear(now)):
		# print(i)
		x.append(dt.datetime(now.year,1,1,0,0,0)+dt.timedelta(days=i))

		#print(x[i])


	# use list comprehension to get the y-vals. As Sun module returns a timedelta - we need a date to offset against to get the times. Use the first day of the year as the offset

	Midnight = dt.datetime(now.year,1,1,0,0,0)
	# only make one call to LeapYear
	LeapYearAdjustment = LeapYear(now)

	DST = [DaylightSavingTime(x[i]) for i in range(0,365 + LeapYear(now))]
	#print(DST)

	# get rise and set for civil twilight and official sun rise/set
	y_RiseOfficial = [ Midnight + Sun(x[i],location,DST[i]).Rise()['Official'] for i in range(0,365 + LeapYearAdjustment) ]
	y_SetOfficial = [ Midnight + Sun(x[i],location,DST[i]).Set()['Official'] for i in range(0,365 + LeapYearAdjustment) ]
	y_RiseCivil = [ Midnight + Sun(x[i],location,DST[i]).Rise()['Civil'] for i in range(0,365 + LeapYearAdjustment) ]
	y_SetCivil = [ Midnight + Sun(x[i],location,DST[i]).Set()['Civil'] for i in range(0,365 + LeapYearAdjustment) ]
	y_Midday = [ Midnight + Sun(x[i],location,DST[i]).Transit() for i in range(0,365 + LeapYear(now)) ]
	#print(x[1])

	#print(y_rise)


	# format how the dates and times are to be displayed
	xfmt = mdates.DateFormatter('%b')
	yfmt = mdates.DateFormatter('%H:%M')

	# matplotlib - create graph
	fig, ax = plt.subplots()

	# plot x and y values
	ax.plot(x, y_RiseOfficial,'navy',label = 'Rise/Set')
	ax.plot(x, y_SetOfficial,'navy')
	ax.plot(x, y_RiseCivil,'black',label = 'Dawn/Dusk')
	ax.plot(x, y_SetCivil,'black')
	ax.plot(x, y_Midday,'Gold', label = 'Noon')

	# show vertical and horizontal gridlines
	ax.grid(which='major', axis='x',linestyle='dotted')
	ax.grid(which='major', axis='y',linestyle='dotted')


	# add in seasons lines
	plt.axvline(x=SPRING,color = 'orange')
	plt.axvline(x=SUMMER,color = 'orange')
	plt.axvline(x=AUTUMN,color = 'orange')
	plt.axvline(x=WINTER,color = 'orange')
	# show where we are in the year
	plt.axvline(x=now, color='red') # time now

	# add in season text
	ax.text(SPRING, dt.datetime(now.year,1,1,12,0), 'Spring', ha='left', va='center', rotation=90)
	ax.text(SPRING, dt.datetime(now.year,1,1,12,0), 'Winter', ha='right', va='center', rotation=90)
	ax.text(SUMMER, dt.datetime(now.year,1,1,12,0), 'Summer', ha='left', va='center', rotation=90)
	ax.text(SUMMER, dt.datetime(now.year,1,1,12,0), 'Spring', ha='right', va='center', rotation=90)
	ax.text(AUTUMN, dt.datetime(now.year,1,1,12,0), 'Autumn', ha='left', va='center', rotation=90)
	ax.text(AUTUMN, dt.datetime(now.year,1,1,12,0), 'Summer', ha='right', va='center', rotation=90)
	ax.text(WINTER, dt.datetime(now.year,1,1,12,0), 'Winter', ha='left', va='center', rotation=90)
	ax.text(WINTER, dt.datetime(now.year,1,1,12,0), 'Autumn', ha='right', va='center', rotation=90)


	#format the axis text

	# set x axis to show every month
	locator = mdates.MonthLocator()
	plt.gca().xaxis.set_major_locator(locator)

	# format how the dates/times are shown on each axis
	plt.gca().xaxis.set_major_formatter(xfmt)
	plt.gcf().autofmt_xdate()
	plt.gca().yaxis.set_major_formatter(yfmt)

	# add in legend below graph
	ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1),ncol=3)

	# save the plot
	fig.savefig(''.join([GRAPH_ROOT,'Year','.png']),bbox_inches='tight')
	# close all the plots to save memory
	plt.close('all')
	print("end of Year Graph code")
	time.sleep(UPDATE_INTERVAL)


