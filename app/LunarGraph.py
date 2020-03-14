import datetime as dt
import time
#import math
import os
import configparser # for reading ini files
import json
# use the custom Moon module - path may change as things progress
from modules.Moon.Moon import Moon
from modules.Utilities.DaysInMonth import DaysInMonth

CWD = os.getcwd()

# get config file location
CONFIG_FILE=''.join([CWD,'/config/config.ini'])
print(CONFIG_FILE)

# set up config file object
config = configparser.ConfigParser()
config._interpolation = configparser.ExtendedInterpolation()

# open config file
config.read(CONFIG_FILE)

# get location of save folder
LUNAR_JSON=''.join([CWD,config.get('files','MoonJSON')])
LUNAR_PHASES_JSON=''.join([CWD,config.get('files','MoonPhaseJSON')])

# how often script should run (sleep time)
UPDATE_INTERVAL = int(config.get('general','UpdateInterval'))

var = 1

# make now static through each run through
now = dt.datetime.now()

illuminated = []
phase = []
LunarCalendar = []
Lunar_phases = [] # the first day will always need to be included

# get the moon illumination for each day of the month, and the phase
for i in range(1,DaysInMonth(dt.datetime(now.year,now.month,1,0,0))+1):
	# print(i)
	# look at the 'i'th day in month for the moon
	m = Moon(dt.datetime(now.year,now.month,i,0,0))
	# get how much of the moon is illuminated
	illuminated.append(m.MoonPercent())
	# get the moon phase
	phase.append(m.MoonPhase())
	# convert date to string - needed for JSON	
	strdate = ''.join([str(now.year),"-",str(now.month).zfill(2),"-",str(i).zfill(2)," ",str(0).zfill(2),":",str(0).zfill(2),":",str(0).zfill(2)])
	
	# build the dictionary which has the date, percentage illuminated and moon phase for the month
	LunarCalendar.append({'Date':strdate,'Percent':illuminated[i-1],'Phase':phase[i-1]})
	
	# get date of changes in phase. Needs to have first item filled otherwise index will be out of bounds	
	if i==1:
		Lunar_phases.append({'Date':strdate,'Phase':phase[i-1]})
	if i > 1:	
		if phase[i-1] != phase[i-2]:
			# this will be the key number for plugging into y_phase to get what the phase is and what the date is
			Lunar_phases.append({'Date':strdate,'Phase':phase[i-1]})

# fill array for x vals for each day of the week (list comprehension quicker than list append)
x_dates = [dt.datetime(now.year,now.month,i,0,0) for i in range(1, DaysInMonth(dt.datetime(now.year,now.month,1,0,0))+1)]

# convert dates to strings for JSON
#x_strdates = [''.join([str(i.year),"-",str(i.month).zfill(2),"-",str(i.day).zfill(2)," ",str(i.hour).zfill(2),":",str(i.minute).zfill(2),":",str(i.second).zfill(2)]) for i in x_dates]

#print("x_dates: ",x_dates)
#print("illuminated: ",illuminated[1])
#print("y_phase: ",y_phase)
#print("x_phase: ",x_phase)
#print(x_strdates)


#LunarCalendar = list(zip(x_strdates,y_illum,y_phase))

#print(LunarCalendar)
#print(Lunar_phases)


# write current conditions to JSON file
with open(LUNAR_JSON,'w') as outfile:
	json.dump(LunarCalendar,outfile)

with open(LUNAR_PHASES_JSON,'w') as outfile:
	json.dump(Lunar_phases,outfile)

	

