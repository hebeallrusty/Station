from app.modules.Utilities.LeapYear import LeapYear
import datetime as dt



def DaysInMonth(oDate):
	# create an array of the days of the month
	MonthArray = [31,28,31,30,31,30,31,31,30,31,30,31]
	
	# plug the month into the array and return. Array is 0 indexed so deduct one
	Days = MonthArray[oDate.month-1]
	
	# feb may be a leapyear
	if oDate.month == 2:
		# LeapYear returns 1 for a leapyear and 0 otherwise, so this can be added on to the days
		Days = Days + LeapYear(oDate)
	
	return Days
