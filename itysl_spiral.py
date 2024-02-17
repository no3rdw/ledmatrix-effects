import displayio, random, math, time, vectorio

class ITYSL1:

	def initPrevline(self):
		prevline = {}
		prevline['length'] = self.device.display.width
		prevline['rotation'] = 180
		prevline['direction'] = 0
		prevline['x'] = self.usableheight
		prevline['y'] = -self.linethickness
		return prevline
	
	def __init__(self, device:Device, palette:int=random.choice([0,1])):
		self.name = 'ITYSL1'
		self.device = device

		self.linethickness = 2 # line thickness
		self.spacer = 1 # space between lines
				
		self.selectedPalette = palette
		self.palettes = []
		self.paletteNames = ['Blue', 'Red']

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
		self.linegroup = displayio.Group()
		device.effect_group.append(self.linegroup)

		self.menu = []
		self.lastLineCheck = 0
		self.lastColorChange = 0
		self.disappearDirection = random.choice([0,1])
		self.nextPalette = random.choice([0,1])

		self.usablewidth = device.display.width
		self.usableheight = device.display.height
		self.usespacer = 0
		self.done = False
		self.prevline = self.initPrevline()


	def rotatePoint(self, point, center, angle):
		angle = (angle) * (math.pi/180) #Convert to radians
		rotatedX = math.cos(angle) * (point[0] - center[0]) - math.sin(angle) * (point[1]-center[1]) + center[0]
		rotatedY = math.sin(angle) * (point[0] - center[0]) + math.cos(angle) * (point[1] - center[1]) + center[1]
		return (round(rotatedX), round(rotatedY))

	def addLineToSpiral(self):
		newline = {}
		#newline['pcomplete'] = 0
		#newline['stage'] = 0 # 0=the line grows over the screen, 1=pause at full length, 2=the line shrinks and then is deleted
		#newline['timer'] = 0

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

	def play(self):
		if self.done != True:
			if (self.device.limitStep(.11, self.lastLineCheck)):
				self.linegroup.append(self.addLineToSpiral())
				self.device.gc(1)
				self.lastLineCheck = time.monotonic()
		else:
			if (self.device.limitStep(.11, self.lastLineCheck)):
				if (len(self.linegroup)):
					if(self.device.limitStep(.3, self.lastColorChange)):
						for n in self.linegroup:
							n.color_index = random.randrange(1,self.colorcount)
						self.lastColorChange = time.monotonic()

					if self.disappearDirection == 1:
						self.linegroup.pop(0)
					else:
						self.linegroup.pop(len(self.linegroup)-1
						 )
					self.device.gc(1)
					self.lastLineCheck = time.monotonic()
				else:
					self.__init__(device=self.device, palette=self.nextPalette)

		if self.device.menu_group.hidden and sum(locals()['keys']):
			if locals()['keys'][3]:
				if (self.device.limitStep(.3, self.device.lastButtonTick)):
					self.__init__(device=self.device, palette=self.nextPalette)
					self.device.lastButtonTick = time.monotonic()
				