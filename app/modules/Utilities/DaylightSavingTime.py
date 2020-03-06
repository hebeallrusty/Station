import datetime as dt

def DaylightSavingTime(oDate):
	# Returns 1 if in DST or 0 if in GMT
	# start at the end of the relevant month and deduct 1 day until the last Sunday of the month is achieved
	Start = dt.datetime(oDate.year,3,31,0,0)
	End = dt.datetime(oDate.year,10,31,0,0)	

	# check if the current date is a Sunday, if not, keep deducting 1 day until it is
	while Start.isoweekday() != 7:
		Start = Start - dt.timedelta(days=1)
		# print(Start)

	while End.isoweekday() !=7:
		End = End - dt.timedelta(days=1)
		# print(End)

	# check to see if the date supplied is between the start and end dates
	if (oDate > Start) and (oDate < End):
		return(1)
	else:
		return(0)
