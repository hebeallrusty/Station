import pyowm
from configparser import SafeConfigParser
import os

# Config file location has to be static
KEY_FILE=os.path.expanduser('~/Station/config/key.ini')
CONFIG_FILE=os.path.expanduser('~/Station/config/config.ini')

config = SafeConfigParser()

# get api key from file
config.read(KEY_FILE)

# INI format is as follows:
# [OpenWeatherMap]
# API_Key=**api key**
OWM_Key=config.get('OpenWeatherMap','API_Key')

# read config file
config.read(CONFIG_FILE)

# set object as call on OWM with user api key
owm = pyowm.OWM(OWM_Key)

#get longitude and latitude from config file and convert to floats as required by owm
Longitude = float(config.get('location','Longitude'))
Latitude = float(config.get('location','Latitude'))

# get observation at coords saved in config file.
observation = owm.weather_at_coords(Latitude,Longitude)

# get current weather and allow object to be interrogated for conditions
w = observation.get_weather()

# get uv data
uv = owm.uvindex_around_coords(Latitude,Longitude)

print(w.get_detailed_status())
print(uv.get_value())

# put current conditions into variables for use later
CurrentConditions = w.get_detailed_status()
Temperature = w.get_temperature('celsius')['temp']
Humidity = w.get_humidity()
UVIndex = uv.get_value()
Wind = w.get_wind()
# convert Wind Speed from m/s to mph
WindSpeed = float(Wind['speed'])*2.23694
# convert Wind direction to compass point
WindDirection = int(Wind['deg'])
if 0 <= WindDirection < 22.5:
	WindBearing = "N"
elif 22.5 <= WindDirection < 67.5:
	WindBearing = "NE"
elif 67.5 <= WindDirection < 112.5:
	WindBearing = "E"
elif 112.5 <= WindDirection < 157.5:
	WindBearing = "SE"
elif 157.5 <= WindDirection < 202.5:
	WindBearing = "S"
elif 202.5 <= WindDirection < 247.5:
	WindBearing = "SW"
elif 247.5 <= WindDirection < 292.5:
	WindBearing = "W"
elif 292.5 <= WindDirection < 337.5:
	WindBearing = "NW"
elif 337.5 <= WindDirection <= 360:
	WindBearing = "N"

print(WindDirection,WindBearing)


# print(CurrentConditions)
# print(Temperature)
# print(Humidity)
# print(WindSpeed)
# print(WindDirection)







