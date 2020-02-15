import datetime as dt
import math
import os
#import time
#t0 = time.time()
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from configparser import SafeConfigParser # for reading ini files
# use the custom Sunrise module - path may change as things progress
from modules.Sun.Sun import Sun
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

now = dt.datetime.today()
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

# datetime object allows individual attributes to be taken such as hour, minute and second. Convert to decimal format for calculations. Ignore seconds.

# TODO - migrate these to a function
dSunrise = Sunrise.hour + (Sunrise.minute / 60)
dSunset = Sunset.hour + (Sunrise.minute / 60)
dLengthOfDay = LengthOfDay.hour + (LengthOfDay.minute / 60)
dNow = now.hour + (now.minute / 60)
dDawn = Dawn.hour + (Dawn.minute / 60)
dDusk = Dusk.hour + (Dusk.minute / 60)
#dNoon = Noon.hour + (Noon.minute / 60)
dNow = now.hour+(now.minute / 60)

# print(dSunrise,dSunset,dLengthOfDay)

# Make "today" static for each run to avoid the problem of an inconsistant date if it clicks over at midnight, and to minimise calls


# create an array of times in the day

xd = [] # datetime objects - for x-axis of graph
xn = [] # time in decimal

# x values will be at 15 minute intervals

for i in range (0,int((dLengthOfDay + 3)/(15/60))):
	xd.append(dt.datetime(now.year,now.month,now.day,int(dSunrise - 1),0,0) + dt.timedelta(minutes=(i * 15)))
	# Decimal version of time - allows calculation with sine curve	
	xn.append(xd[i].hour + (xd[i].minute / 60))
	#print(xd[i].minute)

# create y values 
# TODO migrate formula to a function
y = [math.sin(math.pi*(i - dSunrise) / dLengthOfDay) for i in xn ]

# logic for shading
# create new set for x values based that ends at now. This is for shading up to now in teh graph
xdnow = [i for i in xd if i <now] # create x vals up to now for shading later on. Can be up to 15 mins short though
#print(xdnow)
xdnow.append(dt.datetime(now.year,now.month,now.day,now.hour,now.minute,now.second)) # add in calc for now

#print(xdnow)
# create y values based on shortened x values up to now. Again can be one item short so it'll need adding
y2 = [math.sin(math.pi*(i - dSunrise) / dLengthOfDay) for i in xn if i < dNow]
# add in last element for now
y2.append(math.sin(math.pi*(dNow - dSunrise) / dLengthOfDay))
#print(y2)

# format how the times are to be displayed
xfmt = mdates.DateFormatter('%H:%M')

# matplotlib - create graph
fig, ax = plt.subplots()

# plot x and y values
ax.plot(xd, y)

# set the labels of the axes
ax.set(xlabel="Time", ylabel=" ", title="Sun")

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
# only draw hour line if its 1 hours before Dawn and 1 hours after Dusk, otherwise the graph stretches to accommodate the hour line
if (dNow > (dDawn - 1)) and (dNow < (dDusk - 1)):
	#print("within graph")
	plt.axvline(x=now, color='red') # time now

# bound axis to 1 hrs before Dawn and 1 hours after Dusk
ax.set_xlim(Dawn - dt.timedelta(hours=1),Dusk + dt.timedelta(hours=1))

# add text to graph
# TODO migrate some of the strings to functions
ax.text(Dawn, 0.2, ''.join(['Dawn: ', str(Dawn.hour).zfill(2),":",str(Dawn.minute).zfill(2)]), ha='center', va='bottom', rotation=90)
ax.text(Dusk, 0.2, ''.join(['Dusk: ', str(Dusk.hour).zfill(2),":",str(Dusk.minute).zfill(2)]), ha='center', va='bottom', rotation=90)
ax.text(Noon, 0.2, ''.join(['Noon: ', str(Noon.hour).zfill(2),":",str(Noon.minute).zfill(2)]), ha='center', va='bottom', rotation=90)
ax.text(Sunrise, 0.2, ''.join(['Sunrise: ', str(Sunrise.hour).zfill(2),":",str(Sunrise.minute).zfill(2)]), ha='center', va='bottom', rotation=90)
ax.text(Sunset, 0.2, ''.join(['Sunset: ', str(Sunset.hour).zfill(2),":",str(Sunset.minute).zfill(2)]), ha='center', va='bottom', rotation=90)



#shade graph as day progresses using adjusted curves

plt.fill_between(xdnow, 0, y2,interpolate=True, color='blue')

# autoformat the times
plt.gcf().autofmt_xdate()
plt.gca().xaxis.set_major_formatter(xfmt)


# save the plot
fig.savefig(''.join([GRAPH_ROOT,'Day','.png']),bbox_inches='tight')


