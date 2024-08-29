import displayio, random, time, vectorio, math
from effect import Effect

class Effect(Effect):
	def __init__(self, device:Device):
		self.name = 'ITYSL'
		super().__init__(device, self.name)
		
		self.device = device
		self.menu = [
			{
				'label': 'Speed',
				'set': self.setSpeed,
				'get': self.getSpeed
			}
		]
		self.menu.extend(self.effectmenu)

		self.subEffects = ['Lines', 'Spiral', 'Circles']
		self.lastFrame = 0

		self.subEffectSwitch = time.monotonic()

		if not self.settings: #set defaults
			self.settings['self.selectedSwitchTime'] = 5 # seconds
			
		self.subEffectSwitchTimes = [0,5,10,30,60]

		self.subEffect = self.subEffects[random.randrange(0, len(self.subEffects))]
		self.cycleSubEffect(0)
	
	def initCircles(self, device:Device):
		self.subEffect = 'Circles'
		self.maxcircles = 10
				
		self.p = displayio.Palette(3)
		self.p[0] = device.hls(.49, .1, .35) # cyan bg
		self.p[1] = self.device.hls(0.075, .2, 1) #orange
		self.p[2] = self.device.hls(.95, .25, .75)  #pink
		self.colorcount = len(self.p)

		# Create a bitmap with the number of colors in the selected palette
		self.bitmap = displayio.Bitmap(device.display.width, device.display.height, self.colorcount)

		# Create a TileGrid using the Bitmap and Palette
		tile_grid = displayio.TileGrid(self.bitmap, pixel_shader=self.p)
		
		device.clearDisplayGroup(device.effect_group)
		device.effect_group.append(tile_grid)

		self.polygroup = displayio.Group()
		self.polys = []

		device.effect_group.append(self.polygroup)

		self.lastCircleCheck = 0
		self.totalCircles = 0
		self.maxsize = self.device.display.width * 2

	def initSpiral(self, device:Device):
		self.subEffect = 'Spiral'

		self.linethickness = 2 # line thickness
		self.spacer = 1 # space between lines
				
		self.palettes = []
		self.paletteNames = ['Blue', 'Red']
		self.selectedPalette = random.randrange(0,len(self.paletteNames))

		p = displayio.Palette(6)
		p[0] = device.hls(.6, .25, .3) # baby blue bg
		p[1] = device.hls(.17, .5, 1) #yellow
		p[2] = device.hls(.42, .4, .45) # cyan
		p[3] = device.hls(.68, .05, .7) # navy blue
		p[4] = device.hls(.5, .55, .45) # cyan
		p[5] = device.hls(.17, .5, 1) #yellow (again)
		self.palettes.append(p)

		p = displayio.Palette(9)
		p[0] = device.hls(.05, .15, .7) # red-brown bg
		p[1] = device.hls(.17, .25, .3) #tan
		p[2] = device.hls(.17, .2, .8) # mustard
		p[3] = device.hls(.02, .03, .6) # dark red-brown
		p[4] = device.hls(.85, .3, .5) # bright purple
		p[5] = device.hls(.6, .25, .3) # baby blue
		p[6] = device.hls(.42, .3, .25) # cyan
		p[7] = device.hls(.17, .25, .7) #tan
		p[8] = device.hls(.42, .02, .35) #dark green
		self.palettes.append(p)

		self.colorcount = len(self.palettes[self.selectedPalette])

		# Create a bitmap with the number of colors in the selected palette
		self.bitmap = displayio.Bitmap(device.display.width, device.display.height, self.colorcount)

		# Create a TileGrid using the Bitmap and Palette
		tile_grid = displayio.TileGrid(self.bitmap, pixel_shader=self.palettes[self.selectedPalette])
		
		device.clearDisplayGroup(device.effect_group)
		device.effect_group.append(tile_grid)
		self.polygroup = displayio.Group()
		device.effect_group.append(self.polygroup)

		self.lastLineCheck = 0
		self.lastColorChange = 0
		self.disappearDirection = random.choice([0,1])

		self.usablewidth = device.display.width
		self.usableheight = device.display.height
		self.usespacer = 0
		self.done = False
		self.prevline = {}
		self.prevline['length'] = self.device.display.width
		self.prevline['rotation'] = 180
		self.prevline['direction'] = 0
		self.prevline['x'] = self.usableheight
		self.prevline['y'] = -self.linethickness
		self.polys = [] # not used, but keep for consistancy w/ removePoly

	def initLines(self, device:Device):
		self.subEffect = 'Lines'
		self.maxlines = round(device.display.width / 5)
				
		self.p = displayio.Palette(6)
		self.p[0] = device.hls(.49, .3, .35) # cyan bg
		self.p[1] = device.hls(.17, .5, 1) #yellow
		self.p[2] = device.hls(.49, .7, .5) # light cyan
		self.p[3] = device.hls(.01, .55, 1) # coral
		self.p[4] = device.hls(.68, .05, .7) # navy blue
		self.p[5] = device.hls(.2, .3, .2) # tan
		self.colorcount = len(self.p)

		# Create a bitmap with the number of colors in the selected palette
		self.bitmap = displayio.Bitmap(device.display.width, device.display.height, self.colorcount)

		# Create a TileGrid using the Bitmap and Palette
		tile_grid = displayio.TileGrid(self.bitmap, pixel_shader=self.p)
		
		device.clearDisplayGroup(device.effect_group)
		device.effect_group.append(tile_grid)

		self.polygroup = displayio.Group()
		self.polys = []

		device.effect_group.append(self.polygroup)
		self.lastFrame = 0
		self.lastLineCheck = 0

	def addCircle(self):
		newcircle = {}

		if self.totalCircles % 10 == 0 or self.totalCircles % 10 == 1:
			color = 0
		elif self.totalCircles % 2 == 1:
			color = 1
		else:
			color = 2
		newcircle['poly'] = vectorio.Circle(pixel_shader=self.p, x=round(self.device.display.width/2), y=0, radius=1, color_index=color)
		newcircle['pcomplete'] = 1

		self.polys.append(newcircle)
		self.totalCircles = self.totalCircles + 1
		return newcircle['poly']

	def rotatePoint(self, point, center, angle):
		angle = (angle) * (math.pi/180) #Convert to radians
		rotatedX = math.cos(angle) * (point[0] - center[0]) - math.sin(angle) * (point[1]-center[1]) + center[0]
		rotatedY = math.sin(angle) * (point[0] - center[0]) + math.cos(angle) * (point[1] - center[1]) + center[1]
		return (round(rotatedX), round(rotatedY))

	def addLineToSpiral(self):
		newline = {}
		#newline['stage'] = 0 # 0=the line grows over the screen, 1=pause at full length, 2=the line shrinks and then is deleted

		newline['direction'] = self.prevline['direction'] + 1 if self.prevline['direction'] < 4 else 1
		newline['rotation'] = self.prevline['rotation'] - 90

		if newline['direction'] == 1: #down
			newline['length'] = self.usableheight
			newline['x'] = self.prevline['x'] - self.prevline['length'] 
			newline['y'] = self.prevline['y'] + self.linethickness
			self.usablewidth = self.usablewidth - self.linethickness - self.usespacer	
		elif newline['direction'] == 2: #left to right
			newline['length'] = self.usablewidth
			newline['x'] = self.prevline['x'] + self.linethickness
			newline['y'] = self.prevline['y'] + self.prevline['length']
			self.usableheight = self.usableheight - self.linethickness - self.usespacer
		elif newline['direction'] == 3: #up
			newline['length'] = self.usableheight
			newline['x'] = self.prevline['x'] + self.prevline['length']
			newline['y'] = self.prevline['y'] - self.linethickness
			self.usespacer = self.spacer # needs to be set after the first three lines are drawn because there is no spacer around the outside of the frame
			self.usablewidth = self.usablewidth - self.linethickness - self.usespacer
		else: # right to left
			newline['length'] = self.usablewidth
			newline['x'] = self.prevline['x'] - self.linethickness
			newline['y'] = self.prevline['y'] - self.prevline['length']
			self.usableheight = self.usableheight - self.linethickness - self.usespacer

		points = [(0,0),(newline['length'],0),(newline['length'],-self.linethickness),(0,-self.linethickness)]
		points = list(map(lambda i: self.rotatePoint(i, (0,0), newline['rotation']), points))
		#print(points, 'x:', newline['x'], 'y:', newline['y'], 'rotation:', newline['rotation'] , 'len:', newline['length'], 'direction:', newline['direction'], self.usablewidth, self.usableheight)

		if newline['length'] < self.linethickness:
			self.done = True
			# display nothing for the last polygon if it would have been shorter than the set line thickness, stop the display loop
			newline['poly'] = vectorio.Polygon(pixel_shader=self.palettes[self.selectedPalette], points=[(0,0),(0,0),(0,0),(0,0)], x=0, y=0, color_index=0)
		else:
			newline['poly'] = vectorio.Polygon(pixel_shader=self.palettes[self.selectedPalette], points=points, x=newline['x'], y=newline['y'], color_index=random.randrange(1,self.colorcount))
		
		self.prevline = newline
		return newline['poly']

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
		t = random.randrange(-9, 6) # line tilt range

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
		
		self.polys.append(newline)
		return newline['poly']

	def removePoly(self, i:int=0):
		#print('poly ', i, 'removed')
		self.polygroup.pop(i)
		if len(self.polys)-1 >= i:
			self.polys.pop(i)
	
	def cycleSubEffect(self, direction:int):
		currentIndex = self.subEffects.index(self.subEffect)
		newIndex = currentIndex + direction
		if newIndex > len(self.subEffects)-1:
			newIndex = 0
		elif newIndex < 0:
			newIndex = len(self.subEffects)-1
		getattr(self, 'init'+self.subEffects[newIndex])(self.device)
		self.device.gc(1)
		self.subEffectSwitch = time.monotonic()

	def setSpeed(self, direction:int):
		self.settings['self.selectedSwitchTime'] = self.device.cycleOption(self.subEffectSwitchTimes, self.settings['self.selectedSwitchTime'], direction)
		self.subEffectSwitch = time.monotonic()

	def getSpeed(self):
		if self.settings['self.selectedSwitchTime'] == 0:
			return 'Manual'
		else:
			return str(self.settings['self.selectedSwitchTime']) + 's'

	def play(self):
		if (self.device.limitStep(.01, self.lastFrame)):
			if (self.settings['self.selectedSwitchTime'] and self.device.limitStep(self.settings['self.selectedSwitchTime'], self.subEffectSwitch)):
				# For spiral, we only advance to the next subeffect if the spiral animation completes
				if self.subEffect == 'Spiral' and self.done == True and len(self.polygroup) == 0:
					self.cycleSubEffect(1)
				# for the other effects, we can advance immediately
				elif self.subEffect != 'Spiral':
					self.cycleSubEffect(1)
			if self.device.menu_group.hidden and sum(locals()['keys']):
				if locals()['keys'][3]:
					if (self.device.limitStep(self.device.buttonPause, self.device.lastButtonTick)):
						self.cycleSubEffect(1)					
						self.device.lastButtonTick = time.monotonic()
			# -----------------------------------------------------------------------------------------
			# -----------------------------------------------------------------------------------------
			if self.subEffect == 'Lines':
				if (self.device.limitStep(.2, self.lastLineCheck)):
					if len(self.polygroup) < self.maxlines:
						self.polygroup.append(self.addLine())
						self.device.gc()
					self.lastLineCheck = time.monotonic()
				i = 0
				while i < len(self.polys):
					me = self.polys[i]
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
						self.removePoly(i)
					i = i + 1
				self.lastFrame = time.monotonic()
			# -----------------------------------------------------------------------------------------
			# -----------------------------------------------------------------------------------------
			elif self.subEffect == 'Circles':	
				if (self.device.limitStep(.15, self.lastCircleCheck)):
					if len(self.polygroup) < self.maxcircles:
						self.polygroup.append(self.addCircle())
						self.device.gc()
						self.lastCircleCheck = time.monotonic()
				i = 0
				while i < len(self.polys):
					me = self.polys[i]
					me['poly'].radius = round(self.device.easeOutSine(me['pcomplete'] / self.maxsize) * self.maxsize)
					me['pcomplete'] = me['pcomplete'] + 1
					me['poly'].y = round(me['poly'].radius)-1
					if me['poly'].radius >= self.maxsize:
						self.removePoly(i)
					i = i + 1
			# -----------------------------------------------------------------------------------------
			# -----------------------------------------------------------------------------------------
			elif self.subEffect == 'Spiral':
				if self.done != True:
					if (self.device.limitStep(.11, self.lastLineCheck)):
						self.polygroup.append(self.addLineToSpiral())
						self.device.gc()
						self.lastLineCheck = time.monotonic()
				else:
					if (self.device.limitStep(.11, self.lastLineCheck)):
						if (len(self.polygroup)):
							if(self.device.limitStep(.3, self.lastColorChange)):
								for n in self.polygroup:
									n.color_index = random.randrange(1,self.colorcount)
								self.lastColorChange = time.monotonic()

							if self.disappearDirection == 1:
								self.removePoly()
							else:
								self.removePoly(len(self.polygroup)-1)
							self.device.gc()
							self.lastLineCheck = time.monotonic()
						else:
							self.initSpiral(device=self.device)
			self.lastFrame = time.monotonic()

	def handleRemote(self, key:str):
		if key == 'VolUp':
			self.cycleSubEffect(1)
		elif key == 'VolDown':
			self.cycleSubEffect(-1)