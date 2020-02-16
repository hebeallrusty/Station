def DecimalTime(TimeObj):
	# converts a DateTime object's time to decimal i.e 15:45 = 15.75. Useful for calculations involving time
	return TimeObj.hour + (TimeObj.minute / 60) + (TimeObj.second / 3600)
