import time, vectorio, displayio, random
from effect import Effect

class Effect(Effect):

	def initStatic(self):
		for i in self.staticLines:
			i.tile_grid.hidden = not self.settings['staticOn']

	def setStaticOn(self, direction:int):
		self.settings['staticOn'] = self.device.cycleOption([False,True], self.settings['staticOn'], direction)
		self.initStatic()

	def getStaticOn(self):
		return str(self.settings['staticOn'])
	
	def setShiftHue(self, direction:int):
		self.settings['shiftHue'] = self.device.cycleOption([False,True], self.settings['shiftHue'], direction)
		self.initHSLs()

	def getShiftHue(self):
		return str(self.settings['shiftHue'])


	def __init__(self, device:Device):
		self.name = 'Colorbars'
		super().__init__(device, self.name)
		Effect.device = locals()['device']

		if not self.settings: #set defaults
			self.settings = {'staticOn':True,'shiftHue':True}

		device.clearDisplayGroup(device.effect_group)

		self.menu = [
			{
				'label': 'Static',
				'set': self.setStaticOn,
				'get': lambda: self.getStaticOn()
			},
			{
				'label': 'ShiftHue',
				'set': self.setShiftHue,
				'get': lambda: self.getShiftHue()
			},
		]

		Effect.device.clockcolor = 0xFFFFFF
		Effect.device.clockposition = {'anchor_point':[1,1],'anchored_position':[31,30]}
		
		self.p = displayio.Palette(11)
		self.initHSLs()

		bars = [
				vectorio.Rectangle(pixel_shader=self.p, color_index=1, width=4, height=20, x=2, y=2),
				vectorio.Rectangle(pixel_shader=self.p, color_index=2, width=4, height=20, x=6, y=2),
				vectorio.Rectangle(pixel_shader=self.p, color_index=3, width=4, height=20, x=10, y=2),
				vectorio.Rectangle(pixel_shader=self.p, color_index=4, width=4, height=20, x=14, y=2),
				vectorio.Rectangle(pixel_shader=self.p, color_index=5, width=4, height=20, x=18, y=2),
				vectorio.Rectangle(pixel_shader=self.p, color_index=6, width=4, height=20, x=22, y=2),
				vectorio.Rectangle(pixel_shader=self.p, color_index=7, width=4, height=20, x=26, y=2),
				vectorio.Rectangle(pixel_shader=self.p, color_index=7, width=4, height=3, x=2, y=22),
				vectorio.Rectangle(pixel_shader=self.p, color_index=0, width=4, height=3, x=6, y=22),
				vectorio.Rectangle(pixel_shader=self.p, color_index=5, width=4, height=3, x=10, y=22),
				vectorio.Rectangle(pixel_shader=self.p, color_index=0, width=4, height=3, x=14, y=22),
				vectorio.Rectangle(pixel_shader=self.p, color_index=3, width=4, height=3, x=18, y=22),
				vectorio.Rectangle(pixel_shader=self.p, color_index=0, width=4, height=3, x=22, y=22),
				vectorio.Rectangle(pixel_shader=self.p, color_index=1, width=4, height=3, x=26, y=22),
				vectorio.Rectangle(pixel_shader=self.p, color_index=8, width=4, height=5, x=2, y=25),
				vectorio.Rectangle(pixel_shader=self.p, color_index=9, width=4, height=5, x=6, y=25),
				vectorio.Rectangle(pixel_shader=self.p, color_index=10, width=4, height=5, x=10, y=25),
			]
		
		for bar in bars:
			device.effect_group.append(bar)

		self.menu.extend(self.effectmenu)
		
		self.lastFrame = 0

		Effect.staticP = displayio.Palette(6)
		Effect.staticP[0] = device.hls(0, 0, 0)
		Effect.staticP[1] = device.hls(0, 0, 0)
		Effect.staticP[2] = device.hls(0, .2, 0)
		Effect.staticP[3] = device.hls(0, .4, 0)
		Effect.staticP[4] = device.hls(0, .6, 0)
		Effect.staticP[5] = device.hls(0, 1, 0)

		Effect.staticP.make_transparent(1)

		self.staticLines = [self.StaticLine(), self.StaticLine(), self.StaticLine()]

		for i in self.staticLines:
			device.effect_group.append(i.tile_grid)

		self.tvframe1 = vectorio.Polygon(pixel_shader=Effect.staticP, 
						points=[(0,0),(32,0),(30,2),(2,2),(2,30),(0,32)],
						x=0,
						y=0,
						color_index=0)
		self.tvframe2 = vectorio.Polygon(pixel_shader=Effect.staticP, 
						points=[(30,2),(32,0),(32,32),(0,32),(2,30),(30,30)],
						x=0,
						y=0,
						color_index=0)
		
		device.effect_group.append(self.tvframe1)
		device.effect_group.append(self.tvframe2)


	def play(self):
		if (Effect.device.limitStep(.04, self.lastFrame)):
			# do stuff
			if self.settings['shiftHue']:
				i = 0
				while i < 11:
					self.hues[i], self.directions[i][0]  = self.cycleColor(i, self.hues[i], random.randint(1, 10)/1000, self.directions[i][0], 0, 1)
					self.saturations[i], self.directions[i][1] = self.cycleColor(i, self.saturations[i], random.randint(1, 10)/1000, self.directions[i][1], .5, 1)
					i = i + 1
				self.setPalette()

			for i in self.staticLines:
				i.update()

			self.lastFrame = time.monotonic()

	def initHSLs(self):
		self.hues = [0,1,.2,.5,.3,.8,0,.65,.65,1,.75]
		self.levels = [0,.5,.5,.4,.25,.2,.35,.1,.04,.7,.04]
		self.saturations = [0,0,.7,.7,.8,.8,.85,.1,.9,.0,.8]
		# direction arrays seeded 'randomly', hold the direction the hue and saturation values are cycling for each palette color
		self.directions = [[0,1],[0,0],[1,0],[1,1],[1,0],[0,1],[0,0],[1,1],[1,0],[0,1],[1,1]]
		self.setPalette()

	def handleRemote(self, key:str):
		if key == 'Up':
			self.initHSLs()

	def cycleColor(self, i, v, step, direction, min, max):
		if direction == 0:
			if v+step < max:
				return v+step, direction
			else:
				direction = 1 		
				return max, direction
		else:
			if v-step > min:
				return v-step, direction
			else:
				direction = 0
				return min, direction

	def setPalette(self):
		i = 0
		while i < 11:
			self.p[i] = Effect.device.hls(self.hues[i], self.levels[i], self.saturations[i])
			i = i + 1

	class StaticLine(Effect):
		def __init__(self):
			self.bitmap = displayio.Bitmap(Effect.device.display.width, 3, 5)
			self.tile_grid = displayio.TileGrid(self.bitmap, pixel_shader=Effect.staticP, x=0, y=0)
			self.reinit()
		
		def reinit(self):
			self.bitmap.fill(1)
			self.tile_grid.y = 0 # start behind tvframe
			self.moveTick = time.monotonic()
			self.speed = random.randint(5,15)/100
			self.initialDelay = time.monotonic() + random.randint(0,20)
			self.height = random.choice([1,1,1,2,2])

		def update(self):
			if time.monotonic() > self.initialDelay:
				i = 0
				while i < Effect.device.display.width:
					self.bitmap[i,0] = random.choice([1,2,3,4,4,5,5]) # no black, weighted brighter
					if self.height > 1:
						self.bitmap[i,1] = random.randint(0,5) # random all palette
					else:
						self.bitmap[i,1] = 1
					i = i + 1
					
				if (Effect.device.limitStep(self.speed, self.moveTick)):
					if(self.tile_grid.y <= Effect.device.display.height):
						self.tile_grid.y = self.tile_grid.y + 1
					else:
						self.reinit()

					self.moveTick = time.monotonic()
