import json

class Metadata:
	def __init__(self, version, id, name, clock={}):
		self.version = version
		self.id = id
		self.name = name
		if clock == {}:
			self.dict = {"version":self.version,"id":self.id,"name":self.name}
		else:
			self.clock = clock.getClockDict()
			self.dict = {"version":self.version,"id":self.id,"name":self.name, "clock":self.clock}
	def getMetaDict(self):
		return self.dict
	def setMetaDict(self, key, value):
		self.dict[key] = value
		return self.dict
	class Clock:
		def __init__(self,currentTime,startTime,endTime,multiplier,timeRange,step):
			self.currentTime = currentTime
			self.startTime = startTime
			self.endTime = endTime
			self.multiplier = multiplier
			self.timeRange = timeRange
			self.step = step
			self.interval = str(self.startTime + '/' + self.endTime)
			self.clockDict = {"interval":self.interval,"currentTime":self.currentTime,"multiplier":int(self.multiplier),"range":self.timeRange,"step":self.step}
		def getClockDict(self):
			return self.clockDict
		def setClockDict(self, key, value):
			if lower(key) == "interval":
				print("You should use setClockInterval method!")
			else:
				self.clockDict[key] = value
				return self.clockDict
		def setClockInterval(self,startTime,endTime):
			interval = str(startTime + '/' + endTime)
			self.clockDict["interval"] = interval
			return self.clockDict
