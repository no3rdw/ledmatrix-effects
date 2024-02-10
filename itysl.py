import displayio, random, math, colorsys, time, vectorio

class ITYSL:
	def __init__(self, device:Device):
		self.name = 'ITYSL'
		self.device = device

		self.maxlines = 6
		self.freeze = 0
				
		self.p = displayio.Palette(6)
		self.p[0] = colorsys.hls_to_rgb(.49, .3, .35) # cyan bg
		#self.p[0] = 0x000000
		self.p[1] = colorsys.hls_to_rgb(.17, .5, 1) #yellow
		self.p[2] = colorsys.hls_to_rgb(.49, .7, .5) # light cyan
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

		self.linegroup = displayio.Group()
		self.lines = []

		device.effect_group.append(self.linegroup)

		self.menu = []
		self.lastFrame = 0
		self.lastLineCheck = 0

	def addLine(self):
		newline = {}
		newline['directionx'] = random.choice([1,-1])
		newline['directiony'] = random.choice([1,-1])
		newline['speed'] = random.choice([.03,.04,.05]) # percent of completion per frame
		newline['pcomplete'] = 0
		newline['stage'] = 0 # 0=the line grows over the screen, 1=pause at full length, 2=the line shrinks and then is deleted
		#h = random.randrange(self.device.display.height, round((self.device.display.height*3)))
		h = self.device.display.height+10 # final line height
		newline['timer'] = 0
		
		newline['width'] = 4 # line thickness
		t = random.randrange(-10, 5) # line tilt range

		#starting positions
		x = random.randrange(-newline['width'],self.device.display.width+newline['width'])
		if newline['directiony'] == 1:
			y = 0 # start off the top of the screen
		else:
			y = self.device.display.height # start off the bottom of the screen

		newline['endx'] = newline['directionx']*t
		newline['endy'] = newline['directiony']*h

		# switched to vectorio polygon to allow for thicker lines AND less memory usage
		newline['poly'] = vectorio.Polygon(pixel_shader=self.p, points=[(0,0),(0+newline['width'],0),(0+newline['width'],0),(0,0)], x=x, y=y, color_index=random.randrange(1, self.colorcount))
		
		self.lines.append(newline)
		return newline['poly']

	def removeLine(self, i):
		#print('line ', i, 'removed')
		self.linegroup.pop(i)
		self.lines.pop(i)

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
		if (self.device.limitStep(.2, self.lastLineCheck) and self.freeze == 0):
			if len(self.linegroup) < self.maxlines:
				self.linegroup.append(self.addLine())
				self.device.gc(1)
			self.lastLineCheck = time.monotonic()

		if (self.freeze == 0):
			i = 0
			while i < len(self.lines):
				me = self.lines[i]
				if me['pcomplete'] < 1 and me['stage'] == 0:
					newx = round(me['pcomplete']*me['endx'])
					newy = round(me['pcomplete']*me['endy'])
					me['poly'].points = [(0,0),(0+me['width'],0),(newx+me['width'],newy),(newx,newy)]
					me['pcomplete'] = me['pcomplete'] + me['speed']
				elif me['pcomplete'] >= 1 and me['stage'] == 0:
					me['stage'] = 1 #switching to pause
					me['pcomplete'] = 0
				elif me['stage'] == 1 and me['timer'] == 0:
					me['timer'] = time.monotonic() + 1
					#print('waiting until ', me['timer'])
				elif me['stage'] == 1 and me['timer'] != 0 and me['timer'] - time.monotonic() < 0:
					me['stage'] = 2 #switching to shrink
				elif me['pcomplete'] < 1 and me['stage'] == 2:
					newx = round(me['pcomplete']*me['endx'])
					newy = round(me['pcomplete']*me['endy'])
					me['poly'].points = [(newx,newy),(newx+me['width'],newy),(me['endx']+me['width'],me['endy']),(me['endx'],me['endy'])]
					me['pcomplete'] = me['pcomplete'] + me['speed']
				elif me['pcomplete'] >= 1 and me['stage'] == 2:
					self.removeLine(i)
				i = i + 1
			self.lastFrame = time.monotonic()

		if self.freeze == 1:
			if not locals()['keys'][0]:
				self.freeze = 0

		if self.device.menu_group.hidden and sum(locals()['keys']):
			if locals()['keys'][0]:
				self.freeze = 1
				