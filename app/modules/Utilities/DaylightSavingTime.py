import datetime as dt
import configparser
import os
from app.modules.Utilities.DaysInMonth import DaysInMonth

def DaylightSavingTime(oDate):
	# must be passed a datetime object
	# Returns the offset in hours 
	# basis start at the end of the relevant month and deduct 1 day until the last Sunday of the month is achieved
	
	CWD = os.getcwd()

	# Config file location has to be static

	CONFIG_FILE=''.join([CWD,'/config/config.ini'])
	
	# print(CONFIG_FILE)
	
	#print("opening config file")
	config = configparser.ConfigParser()
	config._interpolation = configparser.ExtendedInterpolation()

	# open config file
	config.read(CONFIG_FILE)
	
	# first, second, last, second to last etc	
	WeekNo = [int(config.get('daylightsavingtime','StartWeekNo')),int(config.get('daylightsavingtime','EndWeekNo'))]

	# day of week mon = 1, sun = 7
	DayName = [int(config.get('daylightsavingtime','StartDayNo')),int(config.get('daylightsavingtime','EndDayNo'))]

	# month of change
	Month = [int(config.get('daylightsavingtime','StartMonth')),int(config.get('daylightsavingtime','EndMonth'))]

	# time in which change happens
	Hour = [int(config.get('daylightsavingtime','StartHour')),int(config.get('daylightsavingtime','EndHour'))]

	Offset = int(config.get('daylightsavingtime','Offset'))

	# loop through the items of WeekNo and if negative, the Day will be the last day of the month, else it will be the first day of the month as the starting point
	Day = []
	for i in range(0,2):
		if WeekNo[i] < 0:
			Day.append(DaysInMonth(dt.datetime(oDate.year,Month[i],1,0,0)))
		else:
			Day.append(1)
	#print("Day: ", Day)
	#print(WeekNo)
	#print(Day)



	
	# starting point for DST calcs
	DSTRange = [dt.datetime(oDate.year,Month[0],Day[0],Hour[0],0),dt.datetime(oDate.year,Month[1],Day[1],Hour[1],0)]
	

	# move two while loops into one with a for i in range (0,2) etc

	# check if the current date is a Sunday, if not, keep deducting 1 day until it is
	
	for i in range(0,2):
		# whilst the date we have doesn't equal the event day
		n = 0 # this is so we can keep track of first, second third etc day in month
		# check for edge case where the date is the first or last day. If not then we need to increment by one and check the day
		if (DSTRange[i].isoweekday() == DayName[i]) and (abs(WeekNo[i]) == 1):
			continue # go onto the next
		else:
			# have to use "or" between them for the loop (not "and" as if one statement is true, the loop ends. See https://stackoverflow.com/questions/54163163/python-while-with-two-conditions-and-or-or for explanation
			while (DSTRange[i].isoweekday() != DayName[i]) or (n != abs(WeekNo[i])):
				#print("n:",n,"WeekNo:",WeekNo[i])
				# increment the day by one. Going forward or back is governed by the WeekNo (<0 is deduction; >0 is addition. By dividing over the absolute value, the increment is either + or - 1
				DSTRange[i] = DSTRange[i] + dt.timedelta(days=(WeekNo[i]/abs(WeekNo[i])))
				#print("DSTRange:",DSTRange[i].isoweekday(),"DayName:", abs(DayName[i]))

				# check if the DSTRange is now the event date. If it is, then we need to increment the counter which checks if it is the first, second or third event.				
				if DSTRange[i].isoweekday() == abs(DayName[i]):
					#print("YES")
					n = n + 1
				
				#print(i,": ",DSTRange[i])

	#print("Final Range:",DSTRange)
	#while End.isoweekday() !=7:
	#	End = End - dt.timedelta(days=1)
		# print(End)

	# check to see if the date supplied is between the start and end dates
	if (oDate > DSTRange[0]) and (oDate < DSTRange[1]):
		return(Offset)
	else:
		return(0)
