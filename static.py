import displayio, random

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
		p[0] = device.hls(.8, .1, 1)
		p[1] = device.hls(.85, .3, 1)
		p[2] = device.hls(.9, .5, 1)
		p[3] = device.hls(.95, .6, 1)
		p[4] = device.hls(.5, .7, 1)
		p[5] = device.hls(.8, .8, 1)
		self.palettes.append(p)

		p = displayio.Palette(6)
		p[0] = device.hls(0, .05, .01)
		p[1] = device.hls(0, .15, .01)
		p[2] = device.hls(0, .25, .01)
		p[3] = device.hls(0, .3, .01)
		p[4] = device.hls(0, .5, .01)
		p[4] = device.hls(0, 1, .01)
		self.palettes.append(p)

		p = displayio.Palette(10)
		p[0] = device.hls(.1, .4, 1)
		p[1] = device.hls(.2, .4, 1)
		p[2] = device.hls(.3, .4, 1)
		p[3] = device.hls(.4, .4, 1)
		p[4] = device.hls(.5, .4, 1)
		p[5] = device.hls(.6, .4, 1)
		p[6] = device.hls(.7, .4, 1)
		p[7] = device.hls(.8, .4, 1)
		p[8] = device.hls(.9, .4, 1)
		p[9] = device.hls(.0, .4, 1)
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

	def play(self):
		#for x in range(0, self.x):
		for x in range(0, self.maxchanged):
			randpixel = [random.randrange(0, self.device.display.width), random.randrange(0, self.device.display.height)]
			self.bitmap[randpixel] = random.randrange(0,self.colorcount)
		
		if self.device.menu_group.hidden and sum(locals()['keys']):
			if locals()['keys'][3]:
				if (self.device.limitStep(.15, self.device.lastButtonTick)):
					self.bitmap.fill(0)
			
