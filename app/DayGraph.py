import datetime as dt
#import math
import os
#import time
#t0 = time.time()
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from configparser import SafeConfigParser # for reading ini files
# use the custom Sunrise module - path may change as things progress
from modules.Sun.Sun import Sun
from modules.Sun.SunCurve import SunCurve
from modules.Utilities.DecimalTime import DecimalTime
matplotlib.use('Agg')
#print(time.time()-t0)

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

# Make "now" static for each run to avoid the problem of an inconsistant date if it clicks over at midnight, and to minimise calls

now = dt.datetime.today() #- dt.timedelta(hours=6)
#print(now)

# initiate the Sun module
s = Sun(now,location,0)

#print(s.Rise()['Official'])

# get sunrise and set times and convert to a datetime object

today = dt.datetime(now.year,now.month,now.day,0,0,0)
Sunrise = today + s.Rise()['Official']
Sunset = today + s.Set()['Official']
LengthOfDay = today + s.LengthOfDay()
Dawn = today + s.Rise()['Civil']
Dusk = today + s.Set()['Civil']
Noon = today + s.Transit()
GoldenRise = today + s.Rise()['Golden']
GoldenSet = today + s.Set()['Golden']

# datetime object allows individual attributes to be taken such as hour, minute and second. Convert to decimal format for calculations.

dSunrise = DecimalTime(Sunrise) #Sunrise.hour + (Sunrise.minute / 60)
dSunset = DecimalTime(Sunset) #Sunset.hour + (Sunrise.minute / 60)
dLengthOfDay = DecimalTime(LengthOfDay) #LengthOfDay.hour + (LengthOfDay.minute / 60)
dNow = DecimalTime(now) #now.hour + (now.minute / 60)
dDawn = DecimalTime(Dawn) #Dawn.hour + (Dawn.minute / 60)
dDusk = DecimalTime(Dusk) #Dusk.hour + (Dusk.minute / 60)
#dNoon = Noon.hour + (Noon.minute / 60)


# print(dSunrise,dSunset,dLengthOfDay)

# create an array of times in the day

xd = [] # datetime objects - for x-axis of graph
xn = [] # time in decimal

# x values will be at 15 minute intervals
WhenIsNow = 0 # used to determine when "now" is reached in the x value array - used for shading
# iterate the number of 15 min intervals between 0 and 3 hrs after the length of day
for i in range (0,int((dLengthOfDay + 3)/(15/60))):
	# start at 1 hr before sunrise and add 15mins and place into an array
	xval = dt.datetime(now.year,now.month,now.day,int(dSunrise - 1),0,0) + dt.timedelta(minutes=(i * 15))
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
plt.vlines(x=Noon, ymin = -0.1, ymax = 0.1, color='grey')
plt.vlines(x=Sunrise, ymin = -0.1, ymax = 0.1, color='grey')
plt.vlines(x=Sunset, ymin = -0.1, ymax = 0.1, color='grey')
plt.vlines(x=GoldenRise, ymin = -0.1, ymax = 0.1, color='grey')
plt.vlines(x=GoldenSet, ymin = -0.1, ymax = 0.1, color='grey')
# only draw hour line if its 1 hours before Dawn and 1 hours after Dusk, otherwise the graph stretches to accommodate the hour line
if (dNow > (dDawn - 1)) and (dNow < (dDusk - 1)):
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
ax.text(GoldenRise, 0.7, ''.join(['Golden: ', str(GoldenRise.hour).zfill(2),":",str(GoldenRise.minute).zfill(2)]), ha='right', va='bottom')
ax.text(GoldenSet, 0.7, ''.join(['Golden: ', str(GoldenSet.hour).zfill(2),":",str(GoldenSet.minute).zfill(2)]), ha='left', va='bottom')
ax.text(Noon,1.1,''.join(['Length Of Day: ', str(LengthOfDay.hour).zfill(2),":",str(LengthOfDay.minute).zfill(2)]), ha='center', va='bottom')



#shade graph as day progresses using adjusted curves

plt.fill_between(xdnow, 0, y2,interpolate=True, color='blue')

# autoformat the times
plt.gcf().autofmt_xdate()
plt.gca().xaxis.set_major_formatter(xfmt)


# save the plot
fig.savefig(''.join([GRAPH_ROOT,'Day','.png']),bbox_inches='tight')



