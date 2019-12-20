def Bearing (Compass):
	if 0 <= Compass < 22.5:
		return "N"
	elif 22.5 <= Compass < 67.5:
		return "NE"
	elif 67.5 <= Compass < 112.5:
		return "E"
	elif 112.5 <= Compass < 157.5:
		return "SE"
	elif 157.5 <= Compass < 202.5:
		return "S"
	elif 202.5 <= Compass < 247.5:
		return "SW"
	elif 247.5 <= Compass < 292.5:
		return "W"
	elif 292.5 <= Compass < 337.5:
		return "NW"
	elif 337.5 <= Compass <= 360:
		return "N"
