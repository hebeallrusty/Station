from math import exp

def SeaLevel(MetersAboveSeaLevel,LocalPressure,Temperature):
	return LocalPressure / exp((-MetersAboveSeaLevel) / ((Temperature + 273.15) * 29.263))
