import time

class Clock:
	def __init__(self, device):
		self.type = 'Clock'
		self.lastTick = 0
		#self.mytime = time.mktime((2023, 12, 31, 16, 17, 00, 6, 365, -1))
		#print(time.localtime(self.mytime))
		
	def play(self, device): 
		if (device.limitStep(1, self.lastTick)):
			self.lastTick = time.monotonic()
			cursec = time.localtime().tm_sec
			for x in range(0,device.pixelcount):
				if x == cursec:
					device.pixels[x] = (0,0,0,50)
				elif x == 15 or x == 30 or x == 45:
					device.pixels[x] = (10,0,0,5)
				elif x % 5 == 0:
					device.pixels[x] = (10,0,0,0)
				else:  
					device.pixels[x] = (0,0,0,0)
			