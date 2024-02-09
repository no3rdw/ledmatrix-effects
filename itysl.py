import displayio, random, math, colorsys, time, vectorio

class ITYSL:
	def __init__(self, device:Device):
		self.name = 'ITYSL'
		self.device = device

		self.speed = .05
		self.freeze = 0
				
		self.p = displayio.Palette(6)
		self.p[0] = colorsys.hls_to_rgb(.49, .3, .35) # teal bg
		#self.p[0] = 0x000000
		self.p[1] = colorsys.hls_to_rgb(.17, .5, 1) #yellow
		self.p[2] = colorsys.hls_to_rgb(.49, .5, .35) # light teal
		self.p[3] = colorsys.hls_to_rgb(.01, .55, 1) # coral
		self.p[4] = colorsys.hls_to_rgb(.68, .05, .7) # navy blue
		self.p[5] = colorsys.hls_to_rgb(.2, .3, .2) # tan
		self.colorcount = len(self.p)

		# Create a bitmap with the number of colors in the selected palette
		self.bitmap = displayio.Bitmap(device.display.width, device.display.height, self.colorcount)

		# Create a TileGrid using the Bitmap and Palette
		tile_grid = displayio.TileGrid(self.bitmap, pixel_shader=self.p)
		
		device.clearDisplayGroup(device.effect_group)
		device.effect_group.append(tile_grid)

		self.lines = displayio.Group()
		self.linedirectionx = []
		self.linedirectiony = []
		self.linespeed = []
		self.lineheight = []

		device.effect_group.append(self.lines)

		self.menu = []
		self.lastFrame = 0
		self.lastLineCheck = 0

	def addLine(self):
		self.linedirectionx.append(random.choice([1,-1]))
		self.linedirectiony.append(random.choice([1,-1]))
		self.linespeed.append(random.choice([2,3]))
		#h = random.randrange(self.device.display.height, round((self.device.display.height*3)))
		h = self.device.display.height*5
		self.lineheight.append(h)
		
		tilt = 20
		x = random.randrange(-4,self.device.display.width+4)
		x0 = 0
		y0 = 0
		if self.linedirectiony[len(self.linedirectiony)-1] == 1:
			y = 0-h
		else:
			y = self.device.display.height
		x1 = x0 + random.randrange(-tilt, tilt)
		y1 = y0 + h

		# switched to vectorio polygon to allow for thicker lines AND less memory usage
		return vectorio.Polygon(pixel_shader=self.p, points=[(x0,y0),(x1,y1),(x1+3,y1),(x0+3,y0)], x=x, y=y, color_index=random.randrange(1, self.colorcount))

	def removeLine(self, i):
		#print('line ', i, 'removed')
		self.lines.pop(i)
		self.linedirectionx.pop(i)
		self.linedirectiony.pop(i)
		self.lineheight.pop(i)
		self.linespeed.pop(i)

	def setoption1(self, direction:int):
		pass
		#a = self.selectedPalette + direction if self.selectedPalette + direction < len(self.palettes) else 0
		#if a < 0: a = len(self.palettes)-1
		#print(a)

		#self.__init__(device=self.device, palette=a, maxchanged=self.maxchanged)

	def setoption2(self, direction:int):
		pass
		#self.maxchanged = self.maxchanged + (direction*10) if self.maxchanged <= 300 else (direction*10)
		#if self.maxchanged < 0: self.maxchanged = 300

	def optionlabel1(self):
		return ''

	def optionlabel2(self):
		return ''

	def play(self):
		if (self.device.limitStep(.1, self.lastLineCheck)):
			if len(self.lines) < 10:
				self.lines.append(self.addLine())
				self.device.gc(1)
				#print(len(self.lines), len(self.linedirectionx), len(self.linedirectiony), len(self.lineheight), len(self.linespeed))
			self.lastLineCheck = time.monotonic()

		if (self.device.limitStep(.02, self.lastFrame) and self.freeze == 0):
			i = 0
			while i < len(self.lines)-1:	
				self.lines[i].y = self.lines[i].y + (self.linedirectiony[i]*self.linespeed[i])
				self.lines[i].x = self.lines[i].x + self.linedirectionx[i]
				if (self.linedirectiony[i] == 1 and self.lines[i].y > self.device.display.height) or (self.linedirectiony[i] == -1 and self.lines[i].y < -1-self.lineheight[i]):
					self.removeLine(i)
				if (self.linedirectiony[i] == 1 and self.lines[i].x > self.device.display.width+20) or (self.linedirectiony[i] == -1 and self.lines[i].x < -20):
					self.removeLine(i)
				i = i + 1
			self.lastFrame = time.monotonic()

		self.freeze = 0
		if self.device.menu_group.hidden and sum(locals()['keys']):
			if locals()['keys'][0]:
				self.freeze = 1
				