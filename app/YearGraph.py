import datetime as dt
import os
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from configparser import SafeConfigParser # for reading ini files
# use the custom Sunrise module - path may change as things progress
from modules.Sun.Sun import Sun
from modules.Utilities.LeapYear import LeapYear
matplotlib.use('Agg')


# Config file location has to be static
CONFIG_FILE=os.path.expanduser('~/Station/config/config.ini')

#print("opening config file")
config = SafeConfigParser()
# open config file
config.read(CONFIG_FILE)

# get location from config file
location = [float(config.get('location','latitude')), float(config.get('location','longitude'))]

# get location of save folder
GRAPH_ROOT=config.get('folder','Graph')
# print(GRAPH_ROOT)

#print(location)

#get current date and time as a reference point
Now = dt.datetime.now()
print(Now)

# initialise x values
x = []

# create an array of dates from 1st Jan this year to 31st Dec this year. LeapYear function returns 1 for a leap year and 0 for non-leap years so can be used to add the extra day in leap years. 
for i in range(0,365+LeapYear(Now)):
	# print(i)
	x.append(dt.datetime(Now.year,1,1,0,0,0)+dt.timedelta(days=i))
	#print(x[i])


# use list comprehension to get the y-vals. As Sun module returns a timedelta - we need a date to offset against to get the times. Use the first day of the year as the offset

Midnight = dt.datetime(Now.year,1,1,0,0,0)

# get rise and set for civil twilight and official sun rise/set
y_RiseOfficial = [ Midnight + Sun(x[i],location,0).Rise()['Official'] for i in range(0,365 + LeapYear(Now)) ]
y_SetOfficial = [ Midnight + Sun(x[i],location,0).Set()['Official'] for i in range(0,365 + LeapYear(Now)) ]
y_RiseCivil = [ Midnight + Sun(x[i],location,0).Rise()['Civil'] for i in range(0,365 + LeapYear(Now)) ]
y_SetCivil = [ Midnight + Sun(x[i],location,0).Set()['Civil'] for i in range(0,365 + LeapYear(Now)) ]
y_Midday = [ Midnight + Sun(x[i],location,0).Transit() for i in range(0,365 + LeapYear(Now)) ]
#print(x[1])

#print(y_rise)


# format how the dates and times are to be displayed
xfmt = mdates.DateFormatter('%b')
yfmt = mdates.DateFormatter('%H:%M')

# matplotlib - create graph
fig, ax = plt.subplots()

# plot x and y values
ax.plot(x, y_RiseOfficial,'Orange')
ax.plot(x, y_SetOfficial,'Blue')
ax.plot(x, y_RiseCivil,'Green')
ax.plot(x, y_SetCivil,'Black')
ax.plot(x, y_Midday,'Yellow')

# show vertical and horizontal gridlines
ax.grid(which='major', axis='x',linestyle='dotted')
ax.grid(which='major', axis='y',linestyle='dotted')


# show where we are in the year
plt.axvline(x=Now, color='red') # time now


#format the axis text

# set x axis to show every month
locator = mdates.MonthLocator()
plt.gca().xaxis.set_major_locator(locator)

# format how the dates/times are shown on each axis
plt.gca().xaxis.set_major_formatter(xfmt)
plt.gcf().autofmt_xdate()
plt.gca().yaxis.set_major_formatter(yfmt)

# save the plot
fig.savefig(''.join([GRAPH_ROOT,'Year','.png']),bbox_inches='tight')



