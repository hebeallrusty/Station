import math # bring in the math library
import datetime

# calculate the sun rise and set times based on a date, location and convert to local time
#
# oDate is a datetime date object
# location is a tuple of [latitude, longitude]

class Sun:
	def __init__(self,oDate,location,tOffset):
		self.oDate = oDate
		self.location = location
		self.tOffset = tOffset
	

	def SunTime(self):
		#print("--------- start ----------")
		dt = datetime #dt is now the datetime object
		#print(oDate.year)
		#print(oDate.month)
		#print(oDate.day)
		#print(location)
		
		# already cos(zenith) for step 7a below
		#zenith ] 0.01454  # golden
		#zenith = -0.01454 # official
		#zenith = -0.10453 # civil
		#zenith = -0.20791 # nautical
		#zenith = -0.30902 # astronomical
		zenith = [0.01454,-0.01454, -0.10453, -0.20791, -0.30902]
		
		# 1) calculate the day of the year
		
		N1 = math.floor(275 * self.oDate.month / 9)
		N2 = math.floor((self.oDate.month + 9) / 12)
		N3 = (1 + math.floor((self.oDate.year - (4 * math.floor(self.oDate.year /4 )) + 2) / 3))
		N = N1 - (N2 * N3) + self.oDate.day - 30
		#print([N1,N2,N3,N])
		
		# 2) convert the longitude to hour value and calculate an approximate time
		#print(location[0],location
		lngHour = self.location[1] / 15
		#print(lngHour)
		
		# t contains both rise and set info in form [t_rise,t_set]
		t = [float(N + ((6 - lngHour)/24)),float(N + ((18 - lngHour) / 24))]
		#print("t:",t)
	
		# 3) Calculate the Sun's mean anomaly
		# use list compression to create another list in form [M_rise,M_set] 
		# 	M = (0.9856 * t) -3.289
		M = [((i * 0.9856) - 3.289) for i in t]
		
		#print(M)

		# 4) calculate the Sun's true longitude	
		# 	L = M + (1.916 * sin(M)) + (0.020 * sin(2 * M)) + 282.634
		# calcs need to use Radians and result needs to be in range [0,360)

		L = [(i + (1.916 * math.sin(math.radians(i))) + (0.020 * math.sin(math.radians(2 * i))) + 282.634) % 360 for i in M]
		#print(L)
		# adjust for L to be in range [0,360]


		# 5a) Calculate the sun's Right Assention
		# RA = atan(0.91764 * tan(L))
		# calcs need to use Radians and result needs to be in range [0,360)
		
		RA = [(math.degrees(math.atan(0.91764 * math.tan(math.radians(i))))) for i in L]
		#print(RA)
	
		# 5b) right ascension value needs to be in the same quadrant as L
		#	Lquadrant  = (floor( L/90)) * 90
		#	RAquadrant = (floor(RA/90)) * 90
		#	RA = RA + (Lquadrant - RAquadrant)

		Lquadrant = [(math.floor(i/90)) * 90 for i in L]
		RAquadrant = [(math.floor(i/90)) * 90 for i in RA]
		#print(Lquadrant,RAquadrant)
		#RAtemp is temp var to do the two list subtractions of Lquadrant and RAquadrant
		RAtemp =[j - k for j,k in zip(Lquadrant,RAquadrant)]
		#print(RAtemp)
		RA = [j + k for j,k in zip(RA,RAtemp)]
		#print(RA)

		# 5c) right ascension value needs to be converted into hours
		#	RA = RA / 15

		RA = [i / 15 for i in RA]
		#print("RA:",RA)

	
		# 6) calculate the Sun's declination
		#	sinDec = 0.39782 * sin(L)
		#	cosDec = cos(asin(sinDec))
	
		sinDec = [0.39782 * math.sin(math.radians(i)) for i in L]
		cosDec = [math.cos(math.radians(math.degrees(math.asin(i)))) for i in sinDec]
		#print(sinDec,cosDec)

		# 7a) calculate the Sun's local hour angle
		#	cosH = (cos(zenith) - (sinDec * sin(latitude))) / (cosDec * cos(latitude))
		# sinDec * sin(latitude:
		cosHtempn = [i * math.sin(math.radians(self.location[0])) for i in sinDec]
		# cosDec * cos(latitude):
		cosHtempd = [i * math.cos(math.radians(self.location[0])) for i in cosDec]
		#print(cosHtempn,cosHtempd)
	
		# look at matrix dimensional cosH in form (rise[4]; set[4])
		#print("zenith - cosHtempn")
		cosH=[0,0]
		#print(zenith[0],cosHtempn[0],cosHtempd[0],(zenith[0]-cosHtempn[0])/cosHtempd[0])

		# create a matrix of two vectors, upper[0] being rise, lower[1] being the sets
		for i in range(0,2):
			#print([(j - cosHtempn[0])/cosHtempd[0] for j in zenith])
			cosH[i]=[(j-cosHtempn[i])/cosHtempd[i] for j in zenith]
		#print("cosH")
		#print("cosH:",cosH)

		# if any item of cosH > 1 then sun never rises
		
		# if any item of cosH < -1 then sun never sets
		# replace the item in cosH with None type if this occurs then do step 7 whilst iterating through the array
		H=[[0,0,0,0,0],[0,0,0,0,0]]
		for j in range (5):
			#print(0,j)
			if abs(cosH[0][j]) > 1:
				cosH[0][j] = None
			else:
				# 7b) finish calculating H and convert into hours	
				H[0][j] = (360 - math.degrees(math.acos(cosH[0][j]))) / 15 
		for j in range (5):
			#print(1,j)
			if abs(cosH[1][j]) > 1:
				cosH[1][j] = None
			else: 
				# 7b) finish calculating H and convert into hours
				H[1][j] = math.degrees(math.acos(cosH[1][j])) / 15 
		#print("H:",H)
		
		# 8) calculate local mean time of rising/setting
		#	T = H + RA - (0.06571 * t) - 6.622
		# + 6.622 below as factoring with the minus taken with the RA
		# 9) UT = T- lngHour : wrap it into one go around the loop
		Ttemp = [(0.06571 * i) + 6.622 for i in t]
		#print("Ttemp:",Ttemp)
		Ttemp = [j - k for j,k in zip(RA,Ttemp)]
		#print("Ttemp:",Ttemp)
		T=[0,0]
		for i in range(0,2):
			#print("H[i]:",H[i],"RA[i]:",RA[i])
			# T = H + RA - (0.06571 * t) - 6.622 - lngHour 
			T[i]=([j + Ttemp[i] - (lngHour) for j in H[i]])
			#print("The T[i]'s:",T[i])
		#print("T:",T)
	
		#print(T[0][0])
		#print(dt.timedelta(hours=T[0][0]))
	
		# make T into times and discard
		localtime=[[0,0,0,0,0],[0,0,0,0,0]]
		#print(localtime)
		for i in range(2):
			for j in range (5):
				# from step 7a
				if cosH[i][j] is None:
					localtime[i][j] = None
				else:
					# convert into range [0,24)
					T[i][j] = T[i][j] % 24
					#print(T[i][j])
					localtime[i][j] = dt.timedelta(hours=T[i][j]+self.tOffset)
		
		#print(localtime)
		#print(localtime[0][0])
		#self.Rise = {'Golden':localtime[0][0],'Official':localtime[0][1],'Civil':localtime[0][2],'Nautical':localtime[0][3],'Astronomical':localtime[0][4]}
		#self.Set = {'Golden':localtime[1][0],'Official':localtime[1][1],'Civil':localtime[1][2],'Nautical':localtime[1][3],'Astronomical':localtime[1][4]}
		#return {'Sunrise':{'Rise':localtime[0][0],'Civil':localtime[0][1],'Nautical':localtime[0][2],'Astronomical':localtime[0][3]},'Sunset':{'Set':localtime[1][0],'Civil':localtime[1][1],'Nautical':localtime[1][2],'Astronomical':localtime[1][3]}}
		return {'Rise':{'Golden':localtime[0][0],'Official':localtime[0][1],'Civil':localtime[0][2],'Nautical':localtime[0][3],'Astronomical':localtime[0][4]},'Set':{'Golden':localtime[1][0],'Official':localtime[1][1],'Civil':localtime[1][2],'Nautical':localtime[1][3],'Astronomical':localtime[1][4]}}

	##########################################
	### Sun Rise
	###
	### returns the sunrise  dictionary. Times are stated in time deltas
	##########################################
	def Rise(self):
		#print(self.Rise)
		return Sun.SunTime(self)['Rise']

	##########################################
	### Sun Set
	###
	### returns the sunrise  dictionary. Times are stated in time deltas
	##########################################
	def Set(self):
		return Sun.SunTime(self)['Set']


	##########################################
	### Length of day
	###
	### returns the current length of the day - the time between sunrise and sunset
	###########################################
	def LengthOfDay(self):
		return Sun.Set(self)['Official'] - Sun.Rise(self)['Official']

	##########################################
	### Time of "noon"
	###
	### returns the time when the sun is the highest in the sky
	##########################################
	def Transit(self):
		return Sun.Rise(self)['Official'] + (Sun.LengthOfDay(self) / 2)

