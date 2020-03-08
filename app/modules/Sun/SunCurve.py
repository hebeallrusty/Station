import math

def SunCurve(Now,Sunrise,LengthOfDay):
	# return a sine curve of the sun's journey throughout the day. Only valid between Dawn and Dusk.
	# values must be "Decimal Time" i.e 13:20 = 13.66666
	return math.sin(math.pi*(Now - Sunrise) / LengthOfDay)
