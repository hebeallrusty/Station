import time
import sqlite3
import pywapi

# database connection
WEATHERDATABASE='/home/pi/Python/station/app/db/weather.db'
WeatherLocation="UKXX3662"
var=1
while var > 0:
	# Weather bits - get the arrays from Weather.com - two versions - the metric units (for everything except windspeed) and imperial (mainly for windspeed in MPH not KPH
	weather = pywapi.get_weather_from_weather_com(WeatherLocation,units="metric")
	weatherImp = pywapi.get_weather_from_weather_com(WeatherLocation,units="imperial")
	print(var)
	# forecast arrays
	#afday=[] # the forecast day
	#aftemph=[] # the forecast high temperature of the day
	#aftempl=[] # the forecast low temperature of the day
	#afcondd=[] # the forecast condition for the daytime
	#afcondn=[] # the forecast condition for the evening/night
	#afprecipd=[] # the chance of rain in the daytime
	#afprecipn=[] # the chance of rain in the evening/nighttime
	
	# if a connection to Weather.com is not available, or the website is not supplying the information then allow a failsafe (i.e don't crash but create "not available" data)
	try:
		db=sqlite3.connect(WEATHERDATABASE)
		c=db.cursor()
		# enumerate through each days forecast, then add it to the database - database only contains the last forecast - it is replace on each run through of the full code.
		for i in range(0,3):
			afday=weather.get("forecasts",{})[i].get("day_of_week","N/A")
			aftemph=weather.get("forecasts",{})[i].get("high","N/A")
			aftempl=weather.get("forecasts",{})[i].get("low","N/A")
			afcondd=weather.get("forecasts",{})[i].get("day",{}).get("text","N/A")
			afcondn=weather.get("forecasts",{})[i].get("night",{}).get("text","N/A")
			afprecipd=weather.get("forecasts",{})[i].get("day",{}).get("chance_precip","N/A")
			afprecipn=weather.get("forecasts",{})[i].get("night",{}).get("chance_precip","N/A")
			
			c.execute("Replace into Forecast (ID, fday, ftemph, ftempl, fcondd, fcondn, fprecipd, fprecipn) values (?, ?, ?, ?, ?, ?, ?, ?);", (i, afday, aftemph, aftempl, afcondd, afcondn, afprecipd, afprecipn))
			db.commit()
			db.close

	except Exception as e:
		print(e)
		db.rollback
		db.close
		# if there is an error, fill the arrays with "not availables"
		#afday.append("N/A")
		#aftemph.append("N/A")
		#aftempl.append("N/A")
		#afcondd.append("N/A")
		#afcondn.append("N/A")
		#afprecipd.append("N/A")
		#afprecipn.append("N/A")

	#Current Conditions
	Temperature=weather.get("current_conditions",{}).get("temperature","N/A")
	RTemperature=weather.get("current_conditions",{}).get("feels_like","N/A")
	Wind=weatherImp.get("current_conditions",{}).get("wind",{}).get("speed","N/A")
	WindText=weatherImp.get("current_conditions",{}).get("wind",{}).get("text","N/A")
	Pressure=weather.get("current_conditions",{}).get("barometer",{}).get("reading","N/A")
	PressureTrend=weather.get("current_conditions",{}).get("barometer",{}).get("direction","N/A")
	Humidity=weather.get("current_conditions",{}).get("humidity","N/A")
	UVIndex=weather.get("current_conditions",{}).get("uv",{}).get("index","N/A")
	WeatherText=weather.get("current_conditions",{}).get("text","N/A")
	#print("DAY:",afday)
	#print("HIGH TEMP:", aftemph)
	

	# weather database
	try:
		db=sqlite3.connect(WEATHERDATABASE)
		c=db.cursor()
		c.execute("Insert into Current (ATemp, RTemp, Humidity, Pressure, wText, Wind, WindText, UVIndex) values (?, ?, ?, ?,?,?,?,?);",(float(Temperature), float(RTemperature), float(Humidity), float(Pressure), WeatherText, Wind, WindText, UVIndex))
		db.commit()
		db.close
		failure=-1
	except Exception as e:
		print(e)
		failure=2
		db.rollback
		db.close		
		#failure=0/0
	
	#var = var+1	
	time.sleep(300)

db.close


