import displayio, random, math, colorsys

class Static:
	def __init__(self, device:Device, palette:int=0, maxchanged:int=10):
		self.name = 'Static'
		self.device = device

		self.speed = .05
		self.maxchanged = maxchanged
		self.selectedPalette = palette

		# Create color palettes
		self.palettes = []
		self.paletteNames = ['Pinks', 'B&W', 'Rainbow']
		
		p = displayio.Palette(6)
		p[0] = colorsys.hls_to_rgb(.8, .1, 1)
		p[1] = colorsys.hls_to_rgb(.85, .3, 1)
		p[2] = colorsys.hls_to_rgb(.9, .5, 1)
		p[3] = colorsys.hls_to_rgb(.95, .6, 1)
		p[4] = colorsys.hls_to_rgb(.5, .7, 1)
		p[5] = colorsys.hls_to_rgb(.1, .8, 1)
		self.palettes.append(p)

		p = displayio.Palette(6)
		p[0] = colorsys.hsv_to_rgb(0, .01, .05)
		p[1] = colorsys.hsv_to_rgb(0, .01, .15)
		p[2] = colorsys.hsv_to_rgb(0, .01, .25)
		p[3] = colorsys.hsv_to_rgb(0, .01, .3)
		p[4] = colorsys.hsv_to_rgb(0, .01, .5)
		p[4] = colorsys.hsv_to_rgb(0, .01, 1)
		self.palettes.append(p)

		p = displayio.Palette(10)
		p[0] = colorsys.hsv_to_rgb(.1, 1, .5)
		p[1] = colorsys.hsv_to_rgb(.2, 1, .5)
		p[2] = colorsys.hsv_to_rgb(.3, 1, .5)
		p[3] = colorsys.hsv_to_rgb(.4, 1, .5)
		p[4] = colorsys.hsv_to_rgb(.5, 1, .5)
		p[5] = colorsys.hsv_to_rgb(.6, 1, .5)
		p[6] = colorsys.hsv_to_rgb(.7, 1, .5)
		p[7] = colorsys.hsv_to_rgb(.8, 1, .5)
		p[8] = colorsys.hsv_to_rgb(.9, 1, .5)
		p[9] = colorsys.hsv_to_rgb(.0, 1, .5)
		self.palettes.append(p)

		self.colorcount = len(self.palettes[self.selectedPalette])

		# Create a bitmap with the number of colors in the selected palette
		self.bitmap = displayio.Bitmap(device.display.width, device.display.height, self.colorcount)

		# Create a TileGrid using the Bitmap and Palette
		tile_grid = displayio.TileGrid(self.bitmap, pixel_shader=self.palettes[self.selectedPalette])

		device.clearDisplayGroup(device.effect_group)
		device.effect_group.append(tile_grid)

		# init iterators
		self.i = 1
		self.x = 1

		self.menu = ['Color', 'Speed']

		for x in range(0, device.display.width):
			for y in range(0, device.display.height):
				self.bitmap[x, y] = random.randrange(0,self.colorcount)

	def setoption1(self, direction:int):
		a = self.selectedPalette + direction if self.selectedPalette + direction < len(self.palettes) else 0
		if a < 0: a = len(self.palettes)-1
		print(a)

		self.__init__(device=self.device, palette=a, maxchanged=self.maxchanged)

	def setoption2(self, direction:int):
		self.maxchanged = self.maxchanged + (direction*10) if self.maxchanged <= 300 else (direction*10)
		if self.maxchanged < 0: self.maxchanged = 300

	def optionlabel1(self):
		return self.paletteNames[self.selectedPalette]

	def optionlabel2(self):
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

	def play(self):
		#for x in range(0, self.x):
		for x in range(0, self.maxchanged):
			randpixel = [random.randrange(0, self.device.display.width), random.randrange(0, self.device.display.height)]
			self.bitmap[randpixel] = random.randrange(0,self.colorcount)
		
		'''self.x = self.easeInOutQuart(self.i / self.maxchanged) * self.maxchanged

		if self.x > self.maxchanged:
			self.i = self.maxchanged
		elif self.x < 0:
			self.i = 0
		else:
			self.i = self.i + self.speed'''
		
		if self.device.menu_group.hidden and sum(locals()['keys']):
			if locals()['keys'][0]:
				if (self.device.limitStep(.15, self.device.lastButtonTick)):
					self.bitmap.fill(0)
			
