import random, time, random
from rainbowio import colorwheel

class Worms:
	def __init__(self, device):
		self.type = 'Worms'
		self.chosen = [] # Array of worms (arrays), 0=pos, 1=length, 2=color
		self.lastChosenTick = 0
		self.lastGrownTick = 0

	def play(self, device):
		device.init_pixelStatus()

		if (device.limitStep(1, self.lastChosenTick)):
			self.lastChosenTick = time.monotonic()
			self.chosen.append([random.randint(0, device.pixelcount-1), 0, random.randint(0,255)])
			
		if (device.limitStep(.1, self.lastGrownTick)):
			self.lastGrownTick = time.monotonic()
			x = len(self.chosen)-1 # reversing the loop so later added worms get stacked above earlier worms
			while x > -1:
				for y in range(self.chosen[x][0] - self.chosen[x][1], self.chosen[x][0] + self.chosen[x][1]):
					if (y >= 0 and y <= device.pixelcount-1 and device.pixelStatus[y] == False):
						device.pixels[y] = colorwheel(self.chosen[x][2])
						device.pixelStatus[y] = True

				self.chosen[x][1] += 1
				if (self.chosen[x][1] >= random.randint(15,25)):
					self.chosen.pop(x)
				x -= 1
