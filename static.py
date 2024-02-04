import terminalio
import displayio, time, random, math
from micropython import const

class Static:
	def __init__(self, device):
		self.name = 'Static'
		self.lastButtonTick = 0

		# Create a bitmap with X colors
		self.bitmap = displayio.Bitmap(device.display.width, device.display.height, 4)

		# Create a two color palette
		palette = displayio.Palette(4)
		palette[0] = 0x000000
		palette[1] = 0x253B21
		palette[2] = 0xFF00FF
		palette[3] = 0x00FF00

		# Create a TileGrid using the Bitmap and Palette
		tile_grid = displayio.TileGrid(self.bitmap, pixel_shader=palette)

		# Create a Group
		group = displayio.Group()

		# Add the TileGrid to the Group
		group.append(tile_grid)

		# Add the Group to the Display
		device.display.root_group = group

		
		self.direction = 'speedup'
		self.speed = .1
		self.maxchanged = 10
		self.i = 1
		self.x = 1

		for x in range(0, device.display.width-1):
			for y in range(0, device.display.height-1):
				self.bitmap[x, y] = random.randrange(0,2) #initially only set to first two colors

	# https://easings.net/
	def easeInOutSine(self, x):
		return -(math.cos(math.pi * x) - 1) / 2

	def easeInOutQuad(self, x):
		if x < .5:
			return 2 * x * x
		else:
			return 1 - math.pow(-2 * x + 2, 2) / 2
		
	def easeInOutQuart(self, x):
		if x < 0.5:
			return  8 * x * x * x * x 
		else:
			return 1 - math.pow(-2 * x + 2, 4) / 2

	def play(self, device):
		for x in range(0, self.x):
			randpixel = [random.randrange(0, device.display.width-1), random.randrange(0, device.display.height-1)]
			old = self.bitmap[randpixel]
			'''if old == 1:
				self.bitmap[randpixel] = 0
			else:
				self.bitmap[randpixel] = 1'''
			self.bitmap[randpixel] = random.randrange(0,4)
		
		self.x = self.easeInOutQuart(self.i / self.maxchanged) * self.maxchanged

		if self.x > self.maxchanged:
			self.i = self.maxchanged
		elif self.x < 0:
			self.i = 0
		else:
			self.i = self.i + self.speed
		
		if device.keypixelStatus[0]:
			if (device.limitStep(.15, self.lastButtonTick)):
				self.bitmap.fill(0)
		
	def play2(self, device):
		pass