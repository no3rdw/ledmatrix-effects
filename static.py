import displayio, random, math

class Static:
	def __init__(self, device:Device, colorcount=8, maxchanged=10):
		self.name = 'Static'

		# Customize
		self.speed = .05
		self.maxchanged = maxchanged

		# Create a bitmap with X colors
		self.colorcount = colorcount
		self.bitmap = displayio.Bitmap(device.display.width, device.display.height, self.colorcount)

		# Create a color palette
		palette = displayio.Palette(self.colorcount)
		palette[0] = 0x000000
		palette[1] = 0x253B21
		if (self.colorcount > 2):
			palette[2] = 0xFF00FF
			palette[3] = 0x00FF00
			palette[4] = 0x0000FF
			palette[5] = 0xCC00FF
			palette[6] = 0x00CCFF
			palette[7] = 0xFF00CC

		# Create a TileGrid using the Bitmap and Palette
		tile_grid = displayio.TileGrid(self.bitmap, pixel_shader=palette)

		device.clearDisplayGroup(device.effect_group)
		device.effect_group.append(tile_grid)

		# init iterators
		self.i = 1
		self.x = 1

		self.menu = ['Color', 'Speed']

		for x in range(0, device.display.width):
			for y in range(0, device.display.height):
				self.bitmap[x, y] = random.randrange(0,self.colorcount) #initially only set to first two colors

	def setoption1(self, device):
		if self.colorcount > 2:
			self.__init__(device=device, colorcount=2, maxchanged=self.maxchanged)
		else:
			self.__init__(device=device, maxchanged=self.maxchanged)

	def setoption2(self, device):
		self.maxchanged = self.maxchanged + 10 if self.maxchanged < 300 else 10

	def optionlabel1(self, device):
		return 'Color' if self.colorcount > 2 else 'B&W'

	def optionlabel2(self, device):
		return str(self.maxchanged)

	# https://easings.net/
	def easeInOutSine(self, x:int):
		return -(math.cos(math.pi * x) - 1) / 2

	def easeInOutQuad(self, x:int):
		if x < .5:
			return 2 * x * x
		else:
			return 1 - math.pow(-2 * x + 2, 2) / 2
		
	def easeInOutQuart(self, x:int):
		if x < 0.5:
			return  8 * x * x * x * x 
		else:
			return 1 - math.pow(-2 * x + 2, 4) / 2

	def play(self, device:Device):
		#for x in range(0, self.x):
		for x in range(0, self.maxchanged):
			randpixel = [random.randrange(0, device.display.width), random.randrange(0, device.display.height)]
			self.bitmap[randpixel] = random.randrange(0,self.colorcount)
		
		'''self.x = self.easeInOutQuart(self.i / self.maxchanged) * self.maxchanged

		if self.x > self.maxchanged:
			self.i = self.maxchanged
		elif self.x < 0:
			self.i = 0
		else:
			self.i = self.i + self.speed'''
		
		if device.menu_group.hidden and sum(locals()['keys']):
			if locals()['keys'][0]:
				if (device.limitStep(.15, device.lastButtonTick)):
					self.bitmap.fill(0)
			
