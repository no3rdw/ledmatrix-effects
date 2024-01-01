import random
from rainbowio import colorwheel

class Sparkle:
	def __init__(self, device):
		self.fadeSpeed = 5
		self.colorMode = True
		self.type = 'Sparkle'
		device.init_pixelStatus()

	def tryNewPixel(self, device):
		chosen = random.randint(0, device.pixelcount-1)
		if device.pixelStatus[chosen] == False:
			device.pixelStatus[chosen] = True
			#pixels[chosen] = (random.randint(100,255),random.randint(100,255),random.randint(100,255),0)
			if (self.colorMode):
				device.pixels[chosen] = colorwheel(random.randint(0,255))
			else:
				device.pixels[chosen] = (0,0,0,255)

	def fadeOnePixel(self, device, i:int, speed:int):
		# fades one pixel the provided number of ticks evenly across RGBW
		newR = 0 if device.pixels[i][0] - speed < 0 else device.pixels[i][0] - speed
		newG = 0 if device.pixels[i][1] - speed < 0 else device.pixels[i][1] - speed
		newB = 0 if device.pixels[i][2] - speed < 0 else device.pixels[i][2] - speed
		newW = 0 if device.pixels[i][3] - speed < 0 else device.pixels[i][3] - speed
		device.pixels[i] = (newR, newG, newB, newW)

	def play(self, device): 
		self.tryNewPixel(device)
		for x in range(0,device.pixelcount):
			if device.pixels[x][0] + device.pixels[x][1] + device.pixels[x][2] + device.pixels[x][3] < 1:
				device.pixelStatus[x] = False
			else:
				self.fadeOnePixel(device, x, self.fadeSpeed)