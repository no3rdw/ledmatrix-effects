import displayio, random, time
from effect import Effect

class Effect(Effect):
	def __init__(self, device:Device):
		self.name = 'Static'
		super().__init__(device, self.name)
		self.device = device

		self.speed = .05
		self.maxchangedOptions = [0,10,50,100,300,500,self.device.display.width*self.device.display.height]
		
		if not self.settings: #set defaults
			self.settings = {"selectedPalette":0, "maxchanged":300}

		# Create color palettes
		self.palettes = []
		self.paletteNames = ['Pinks', 'B&W', 'Rainbow','Geode']
		
		p = displayio.Palette(6)
		p[0] = device.hls(.8, .1, 1)
		p[1] = device.hls(.85, .3, 1)
		p[2] = device.hls(.9, .5, 1)
		p[3] = device.hls(.95, .6, 1)
		p[4] = device.hls(.5, .7, 1)
		p[5] = device.hls(.8, .8, 1)
		self.palettes.append(p)

		p = displayio.Palette(6)
		p[0] = device.hls(0, .05, 0)
		p[1] = device.hls(0, .15, 0)
		p[2] = device.hls(0, .25, 0)
		p[3] = device.hls(0, .3, 0)
		p[4] = device.hls(0, .5, 0)
		p[5] = device.hls(0, 1, 0)
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

		p = displayio.Palette(14)
		p[0] = device.hls(0, 0, 0) # black
		p[1] = device.hls(.2, .5, .7) # yellow
		p[2] = device.hls(.5, .4, .7) # cyan
		p[3] = device.hls(.3, .25, .8) # green
		p[4] = device.hls(.8, .2, .8) # magenta
		p[5] = device.hls(0, .35, .85) # red
		p[6] = device.hls(.65, .1, 1) # blue
		p[7] = device.hls(.65, .04, .9) # navy
		p[8] = device.hls(.75, .04, .8) # purple
		p[9] = device.hls(.65, .04, .9) # navy
		p[10] = device.hls(.75, .04, .8) # purple
		p[11] = device.hls(0, 0, 0) # black
		p[12] = device.hls(0, 0, 0) # black
		p[13] = device.hls(0, 0, 0) # black
		self.palettes.append(p)

		self.clockcolors = [0x000000,0x000000,0x000000,0xFFFFFF]

		self.colorcount = len(self.palettes[self.settings['selectedPalette']])
		self.bitmap = displayio.Bitmap(self.device.display.width, self.device.display.height, self.colorcount)
		self.tile_grid = displayio.TileGrid(self.bitmap, pixel_shader=self.palettes[self.settings['selectedPalette']])

		device.clearDisplayGroup(device.effect_group)
		device.effect_group.append(self.tile_grid)

		# init iterators
		self.i = 1
		self.x = 1

		self.menu = [
			{
				'label': 'Color',
				'set': self.setPalette,
				'get': self.getPalette
			},
			{
				'label': 'Speed',
				'set': self.setSpeed,
				'get': self.getSpeed
			}
		]
		self.menu.extend(self.effectmenu)

		for x in range(0, device.display.width):
			for y in range(0, device.display.height):
				self.bitmap[x, y] = random.randrange(0,self.colorcount)

	def setPalette(self, direction:int):
		a = self.settings['selectedPalette'] + direction if self.settings['selectedPalette'] + direction < len(self.palettes) else 0
		if a < 0: a = len(self.palettes)-1
		self.settings['selectedPalette'] = a
		self.colorcount = len(self.palettes[self.settings['selectedPalette']]) 
		self.bitmap.fill(0)
		self.tile_grid.pixel_shader=self.palettes[self.settings['selectedPalette']]
		self.device.clockcolor = self.clockcolors[self.settings['selectedPalette']]

	def setSpeed(self, direction:int):
		self.settings['maxchanged'] = self.device.cycleOption(self.maxchangedOptions, self.settings['maxchanged'], direction)

	def getPalette(self):
		return self.paletteNames[self.settings['selectedPalette']]

	def getSpeed(self):
		return str(self.settings['maxchanged'])

	def play(self):
		#for x in range(0, self.x):
		if (self.device.limitStep(.05, self.lastFrame)):
			if self.settings['maxchanged'] == self.device.display.width*self.device.display.height:
				for x in range(0, self.device.display.width):
					for y in range(0, self.device.display.height):
						self.bitmap[x,y] = random.randrange(0,self.colorcount)
			else:
				for x in range(0, self.settings['maxchanged']):
					randpixel = [random.randrange(0, self.device.display.width), random.randrange(0, self.device.display.height)]
					self.bitmap[randpixel] = random.randrange(0,self.colorcount)
			
			self.lastFrame = time.monotonic()

	def handleRemote(self, key:str):
		if key == 'Enter':
			self.bitmap.fill(0)
		elif key == 'VolDown':
			self.setPalette(-1)
		elif key == 'VolUp':
			self.setPalette(1)