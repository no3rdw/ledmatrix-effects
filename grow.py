import time, vectorio, displayio, random, math, bitmaptools
from effect import Effect

class Effect(Effect):

	def setDaySpeed(self, direction:int):
		self.settings['daycyclespeed'] = self.device.cycleOption([1,2,4,8,10], self.settings['daycyclespeed'], direction)

	def getDaySpeed(self):
		return str(self.settings['daycyclespeed'])

	def __init__(self, device:Device):
		self.name = 'Grow'
		super().__init__(device, self.name)
		self.device = locals()['device']

		device.clearDisplayGroup(device.effect_group)

		if not self.settings: #set defaults
			self.settings['daycyclespeed'] = 1

		self.offset_x = 0
		self.offset_y = 0
		self.currentscreen = 'Grow'
		self.screenmoving = 0

		self.menu = [
			{
				'label': 'Speed',
				'set': self.setDaySpeed,
				'get': self.getDaySpeed
			}
		]
		self.menu.extend(self.effectmenu)

		self.lastFrame = 0
		self.lastPlantInit = 0
		self.lastCloudFrame = 0
		self.beeFrame = 0
		self.wormFrame = 0
		self.wormTrailColorSwitch = 0
		self.lastTwinkleFrame = 0
		
		self.p = displayio.Palette(35)
		self.p[0] = device.hls(.6, .1, .8) # bg

		self.p[1] = device.hls(.35, .3, .8) # green
		self.p[2] = device.hls(.35, .25, .8) # dark green
		self.p[3] = device.hls(.35, .15, .85) # darker green
		self.p[4] = device.hls(.6, .15, .8) # bg

		self.p[5] = device.hls(.30, .3, .5) # blue-green
		self.p[6] = device.hls(.37, .2, .5) # dark blue-green
		self.p[7] = device.hls(.37, .15, .5) # darker blue-green
		self.p[8] = device.hls(.6, .15, .8) # bg

		self.p[9] = device.hls(.38, .2, .8) # blue-green
		self.p[10] = device.hls(.38, .15, .8) # dark blue-green
		self.p[11] = device.hls(.38, .1, .85) # darker blue-green
		self.p[12] = device.hls(.6, .15, .8) # bg

		self.p[13] = device.hls(1, 1, 0) # white
		self.p[14] = device.hls(.25, .6, 1) # yellow-green
		self.p[15] = device.hls(.2, .6, 1) # yellow
		self.p[16] = device.hls(.1, .4, 1) # orange
		self.p[17] = device.hls(.8, .4, 1) # purple
		self.p[18] = device.hls(.9, .4, 1) # violet
		self.p[19] = device.hls(.9, 0, 0) # black
		self.p[20] = device.hls(1, .4, 0) # grey
		self.p[21] = device.hls(.13, .8, 1) # cream?
		

		self.p[22] = device.hls(.6, .2, .85) # bglighter
		self.p[23] = device.hls(.6, .25, .9) # bglighter
		self.p[24] = device.hls(.59, .3, .8) # bglighter
		self.p[25] = device.hls(.58, .3, .9) # bglighter
		self.p[26] = device.hls(.57, .35, .8) # bglighter
		self.p[27] = device.hls(.56, .35, .9) # bglighter
		self.p[28] = device.hls(.55, .38, .8) # bglighter
		self.p[29] = device.hls(.54, .95, .9) # moon
		self.p[30] = device.hls(.54, .7, .9) # star1
		self.p[31] = device.hls(.54, .8, .9) # star2

		self.p[32] = device.hls(.7, .8, 1) # lavender
		self.p[33] = device.hls(.99, .8, .8) # pink

		self.w = displayio.Palette(9)
		self.w[0] =  device.hls(.04, .05, .5) # bg
		self.w[1] = device.hls(.04, .06, .5) # worm poop
		self.w[2] = device.hls(.01, .2, .6) # worm
		self.w[3] = device.hls(.015, .25, .65) # worm2
		self.w[4] = device.hls(.04, .1, .3) # mineral
		self.w[5] = device.hls(.04, .08, .35) # mineral2
		self.w[6] = device.hls(.04, .06, .4) # mineral3
		self.w[7] = device.hls(0, 0, 0) # transparent
		self.w[8] = device.hls(.04, .4, .35)  # roots
		self.w.make_transparent(7)

		self.wormtrailcolor = 1

		self.wormsbitmap = displayio.Bitmap(device.display.width, device.display.height, len(self.w))
		self.worms_tilegrid = displayio.TileGrid(self.wormsbitmap, pixel_shader=self.w)
		
		self.worms_fg = displayio.Group(x=0, y=32)
		self.worms_fg.append(self.worms_tilegrid)

		self.rootsbitmap = displayio.Bitmap(device.display.width, device.display.height, len(self.w))
		self.roots_tilegrid = displayio.TileGrid(self.rootsbitmap, pixel_shader=self.w)
		self.rootsbitmap.fill(7)
		self.worms_fg.append(self.roots_tilegrid)

		self.stemfade = [
			[1,2,3,4],
			[5,6,7,8],
			[9,10,11,12]
		]

		self.flowercolors = [13,15,16,17,18,21,32,33]
		self.dotcolors = [13,15,16]
		self.plants = []
		self.bees = []

		# Create a bitmap with the number of colors in the selected palette
		self.bitmap = displayio.Bitmap(device.display.width, device.display.height, len(self.p))
		self.tile_grid = displayio.TileGrid(self.bitmap, pixel_shader=self.p)
		
		#bitmaptools.fill_region(dest_bitmap=self.bitmap, x1=0, y1=0, x2=device.display.width, y2=device.display.height, value=0)
		device.effect_group.append(self.tile_grid)

		self.far_bg = displayio.Group()
		self.grow_fg = displayio.Group()
		

		self.cloudgroup = displayio.Group()

		self.cloud_b = displayio.OnDiskBitmap('images/cloud2.bmp')
		self.cloudshader = self.device.alphaPalette(self.cloud_b.pixel_shader, True)
		self.cloudshader.make_transparent(2)

		self.ground = vectorio.Rectangle(pixel_shader=self.p, x=0, y=device.display.height-1, width=device.display.width, height=1, color_index=2)
		
		sun1 = vectorio.Circle(pixel_shader=self.p, x=0, y=0, radius=85, color_index=22)
		sun3 = vectorio.Circle(pixel_shader=self.p, x=0, y=0, radius=65, color_index=24)
		sun5 = vectorio.Circle(pixel_shader=self.p, x=0, y=0, radius=45, color_index=26)
		#sun7 = vectorio.Circle(pixel_shader=self.p, x=0, y=0, radius=25, color_index=28)
		sunYellow = vectorio.Circle(pixel_shader=self.p, x=0, y=0, radius=5, color_index=21)
		self.sungroup = displayio.Group()
		self.sungroup.x = -10
		self.sungroup.y = -10
		self.sungroup.append(sun1)
		self.sungroup.append(sun3)
		self.sungroup.append(sun5)
		#self.sungroup.append(sun7)
		self.sungroup.append(sunYellow)

		self.far_bg.append(self.sungroup)

		moon = vectorio.Circle(pixel_shader=self.p, x=0, y=4, radius=4, color_index=29)
		mooncutout = vectorio.Circle(pixel_shader=self.p, x=-2, y=4, radius=3, color_index=0)
		self.moongroup = displayio.Group()
		self.moongroup.append(moon)
		self.moongroup.append(mooncutout)
		self.far_bg.append(self.moongroup)
		device.effect_group.append(self.far_bg)

		self.cloudbg = self.initCloud(1)
		self.cloudfg = self.initCloud(2)
		self.cloudgroup.append(self.cloudbg['group'])
		self.cloudgroup.append(self.cloudfg['group'])
		self.far_bg.append(self.cloudgroup)

		self.beegroup = displayio.Group()
		self.bees.append(self.initBee())
		self.bees.append(self.initBee())
		self.bees.append(self.initBee())

		self.plantgroup = displayio.Group()
		self.grow_fg.append(self.plantgroup)
		self.grow_fg.append(self.ground)

		self.grow_fg.append(self.beegroup)
		device.effect_group.append(self.grow_fg)
		device.effect_group.append(self.worms_fg)

		# Object properties
		self.arc_radius = 64
		self.arc_center = (16, 64)
		self.sun_angle = math.radians(270)
		self.moon_angle = math.radians(90)
		self.day = 1
		self.stars = []

	def initWormScreen(self):
		self.wormsbitmap.fill(0)
		self.wormTrailColorSwitch = time.monotonic()
		self.worms = []
		self.wormtrailcolor = 1
		self.roots = []
		self.rootsbitmap.fill(7)
		self.bonegroup = displayio.Group()

		bone = vectorio.Polygon(pixel_shader=self.p, 
								   	points=[(0,0),(2,2), (0,2)],
									x=0,
									y=0,
									color_index=2)
		self.bonegroup.append(bone)
		self.worms_fg.append(self.bonegroup)


		x = 0
		while x < 25:
			# draw some random dots
			self.wormsbitmap[(random.randint(0,self.device.display.width-1), random.randint(0,self.device.display.height-1))] = random.randint(4,6)
			x = x + 1
		
		x = 0
		while x < 3:
			self.worms.append(self.initWorm())
			x = x+1

	def initGrowScreen(self):
		pass
		#x = 0
		#while x < len(self.plants):
		#	self.removePlant(0)

	def initRoot(self, x=0, y=0):
		me = {}
		if x == 0: x = random.randint(5, self.device.display.width-5)
		me['x'] = x
		me['y'] = y
		me['currentleftwidth'] = 0
		me['currentrightwidth'] = 0
		me['currentleftx'] = 0
		me['currentrightx'] = 0
		me['stage'] = 0 # 0 = growing vertical 1 = growing horizontal 2 = grow joints 3 = delete root
		me['height'] = random.randint(1,6)
		me['currentheight'] = 1
		me['leftwidth'] = random.randint(1,4)
		me['rightwidth'] = random.randint(1,4)
		return me

	def growRoot(self, me):
		if me['stage'] == 0:
			self.rootsbitmap[( me['x'], me['y'])] = 8
			me['y'] += 1
			if me['y'] > self.device.display.height-1: 
				self.removeRoot()
				return
			me['currentheight'] += 1
			if me['currentheight'] >= me['height']: me['stage'] += 1
		elif me['stage'] == 1:
			if abs(me['currentleftwidth']) < me['leftwidth']:
				me['currentleftwidth'] -= 1
				if me['currentleftwidth']+me['x'] < 0:
					me['currentleftx']  = 0
				else: 
					me['currentleftx'] = me['currentleftwidth']+me['x']
				self.rootsbitmap[(me['currentleftx'],me['y'])] = 8
				#print('left',(me['currentleftx'],me['y']))
			if abs(me['currentrightwidth']) < me['rightwidth']:
				me['currentrightwidth'] += 1
				if me['currentrightwidth']+me['x'] > self.device.display.height-1:
					me['currentrightx'] = self.device.display.height-1
				else: 
					me['currentrightx'] = me['currentrightwidth' ]+ me['x']
					#print('right',( me['currentrightx'] ,me['y']))
				self.rootsbitmap[( me['currentrightx'] ,me['y'])] = 8
			if abs(me['currentleftwidth']) >= me['leftwidth'] and abs(me['currentrightwidth']) >= me['rightwidth']:
				me['stage'] += 1
		elif me['stage'] == 2:
			if random.randint(1,3) != 1:
				self.roots.append(self.initRoot(me['currentleftx'],me['y']))
			if random.randint(1,3) != 1:
				self.roots.append(self.initRoot(me['currentrightx'],me['y']))
			me['stage'] += 1
		elif me['stage'] == 3:
			pass

	def removeRoot(	self):
		self.roots = []
		self.rootsbitmap.fill(7)

	def initWorm(self):
		me = {}
		me['y'] = random.randint(0, self.device.display.height-1)
		me['x'] = random.randint(0, self.device.display.width-1)
		me['cells'] = [(me['x'],me['y'])]
		me['color'] = random.randint(2,3)
		me['cd'] = 2 #change direction countdown
		me['fc'] = False # force change direction

		self.wormsbitmap[me['cells'][0]] = me['color']

		me['direction'] = random.randint(1,8)
		return me

	def moveWorm(self, me):
		if me['direction'] == 1: #up
			me['y'] = me['y'] - 1
		elif me['direction'] == 2: #up-right
			me['y'] = me['y'] - 1
			me['x'] = me['x'] + 1
		elif me['direction'] == 3: #right
			me['x'] = me['x'] + 1
		elif me['direction'] == 4: #down-right
			me['y'] = me['y'] + 1
			me['x'] = me['x'] + 1
		elif me['direction'] == 5: #down
			me['y'] = me['y'] + 1
		elif me['direction'] == 6: #down-left
			me['y'] = me['y'] + 1
			me['x'] = me['x'] - 1
		elif me['direction'] == 7: #left
			me['x'] = me['x'] - 1
		elif me['direction'] == 8: #up-left
			me['y'] = me['y'] - 1
			me['x'] = me['x'] - 1

		if me['x'] > self.device.display.width-1:
			me['x'] = self.device.display.width-1
			me['fc'] = True
		elif me['x'] < 0:
			me['x'] = 0
			me['fc'] = True

		if me['y'] > self.device.display.height-1:
			me['y'] = self.device.display.height-1
			me['fc'] = True
		elif me['y'] <= 0:
			me['y'] = 0
			me['fc'] = True

		me['cells'].append((me['x'],me['y']))
		self.wormsbitmap[(me['x'],me['y'])] = me['color']
		if len(me['cells']) > 7:
			# remove the last cell from the worm and set the pixel to the bg color
			self.wormsbitmap[(me['cells'][0][0], me['cells'][0][1])] = self.wormtrailcolor
			me['cells'].pop(0)

		move = random.randint(1,5)
		if me['fc'] == True and (me['x'] == self.device.display.width-1 or me['y'] == self.device.display.height-1):
			me['direction'] = self.device.cycleOption([1,2,3,4,5,6,7,8], me['direction'], -random.randint(2,4)) # counterclockwise move
			me['fc'] = False
			me['cd'] = 2
		elif me['fc'] == True and (me['x'] == 0 or me['y'] == 0):
			me['direction'] = self.device.cycleOption([1,2,3,4,5,6,7,8], me['direction'], random.randint(2,4)) # clockwise move
			me['fc'] = False
			me['cd'] = 2
		elif move == 5 and me['cd'] <= 0:
			me['direction'] = self.device.cycleOption([1,2,3,4,5,6,7,8], me['direction'], 1)
			me['cd'] = 2
		elif move == 4 and me['cd'] <= 0:
			me['direction'] = self.device.cycleOption([1,2,3,4,5,6,7,8], me['direction'], -1)
			me['cd'] = 2
		else:
			me['cd'] = me['cd'] - 1

	def rotatePoint(self, point, angle, center=(0,0)):
		angle = (angle) * (math.pi/180) #Convert to radians
		rotatedX = math.cos(angle) * (point[0] - center[0]) - math.sin(angle) * (point[1]-center[1]) + center[0]
		rotatedY = math.sin(angle) * (point[0] - center[0]) + math.cos(angle) * (point[1] - center[1]) + center[1]
		return (round(rotatedX), round(rotatedY))
	
	def scalePoint(self, point, scale, origin=(0,0)):		
		scaled_x = origin[0] + (point[0] - origin[0]) * (scale / 100)
		scaled_y = origin[1] + (point[1] - origin[1]) * (scale / 100)
		return (round(scaled_x), round(scaled_y))
	
	def reflectPoint(self, point, linepoint1, linepoint2):
		# Calculate the slope of the line
		if linepoint1[0] != linepoint2[0]:
			m = (linepoint2[1] - linepoint1[1]) / (linepoint2[0] - linepoint1[0])
		else:
			# avoid division by zero
			m = float(0.0001)
		# Calculate the y-intercept of the line
		c = linepoint1[1] - m * linepoint1[0]
		# Calculate the coordinates of the reflected point
		reflected_x = point[0] - 2 * (m * (point[1] - c) + point[0]) / (m ** 2 + 1)
		reflected_y = point[1] - 2 * (m * (point[1] - c) + point[0]) * m / (m ** 2 + 1)
		return (round(reflected_x), round(reflected_y))

	def initCloud(self, scale):
		me = {}
		me['scale'] = scale
		me['group'] = displayio.Group(scale=me['scale'])
		me['group'].y = 2
		me['group'].x = round(random.randrange(-self.device.display.width, self.device.display.width) / scale)
		me['delay'] = random.randrange(10,30)
		c = displayio.TileGrid(bitmap=self.cloud_b,
						 pixel_shader=self.cloudshader,
						 x=0, y=0)
		me['group'].append(c)
		return me
	
	def shadeCloud(self, me, shade:float):
		newBitmap = displayio.OnDiskBitmap('images/cloud2.bmp')
		me['group'][0].pixel_shader = self.device.alphaPalette(newBitmap.pixel_shader, True, shade)
		me['group'][0].pixel_shader.make_transparent(2)

	def moveCloud(self, me):
		me['group'].x = me['group'].x + me['scale']
		if me['group'].x > self.device.display.width+(me['delay']*me['scale']):
			# re-init params after cloud goes offscreen
			me['group'].x = 0 - round(13 * me['scale'])
			me['delay'] = random.randrange(10,30)

	def initBee(self):
		me = {}
		me['group'] = displayio.Group()
		me['group'].y = 16
		me['group'].x = 16
		me['group'].append(vectorio.Rectangle(pixel_shader=self.p, width=3, height=1,x=1,y=1,color_index=19))
		me['group'].append(vectorio.Rectangle(pixel_shader=self.p, width=1, height=1,x=2,y=1,color_index=15))
		me['group'].append(vectorio.Rectangle(pixel_shader=self.p, width=2, height=1,x=1,y=0,color_index=20))
		me['delay'] = random.randrange(10,30)
		self.beegroup.append(me['group'])
		return me
	
	def moveBee(self, me):
		if self.day == 1:
			me['group'].x = me['group'].x + random.randint(0,2)-1
			me['group'].y = me['group'].y + random.randint(0,2)-1

			if me['group'].x < -3 or me['group'].x > self.device.display.width or me['group'].y < 0 or me['group'].y > self.device.display.height-3:
				me['group'].y = 16
				me['group'].x = 16
				# re-init params when goes offscreen
				me['delay'] = random.randrange(10,30)
		else:
			if me['group'].x < self.device.display.width:
				me['group'].x = me['group'].x + 1
				me['group'].y = me['group'].y + random.randint(0,2)-1

	def initPlant(self):
		plant = {}
		plant['leaves'] = []
		plant['stage'] = 0 # 0 = leaves grow, 1 = flower grow, 2 = wait, 3 = fade, pop
		plant['flowertype'] = random.randint(1,2)
		if plant['flowertype'] == 1:
			plant['flowersize'] = random.randint(4,5)
			plant['leafrotation'] = -random.randint(20,50)
			plant['leafleftmod'] = random.randint(4,6)
			plant['leafrightmod'] = plant['leafleftmod'] + (random.randint(0,2)-1)
		else:
			plant['flowersize'] = 3
			plant['leafrotation'] = -random.randint(70,85)
			plant['leafleftmod'] = 9
			plant['leafrightmod'] = plant['leafleftmod']
		plant['dotsize'] = plant['flowersize'] - 1
		plant['height'] = random.randint(12,self.device.display.height-plant['flowersize']-5)
		plant['currentheight'] = 1
		plant['color'] = random.randint(0,2)
		plant['colorindex'] = 0
		plant['polygroup'] = displayio.Group()
		plant['startx'] = random.randint(3, self.device.display.width-6)
		
		plant['leafscale'] = random.randint(100, 150)
		plant['stempoints'] = [(1,0),(-1,0),(-1,1),(1,1)]
		plant['stem'] = vectorio.Polygon(pixel_shader=self.p, 
								   	points=plant['stempoints'],
									x=plant['startx'],
									y=self.device.display.height,
									color_index=self.stemfade[plant['color']][0])
		plant['polygroup'].append(plant['stem'])
		plant['life'] =  random.randint(15,35)/(10*self.settings['daycyclespeed'])
		plant['timer'] = 0

		self.plantgroup.append(plant['polygroup'])

		return plant
	
	def initLeaf(self, plant, x, y, side='right'):
		leaf = {}
		leaf['y'] = y
		leaf['points'] = [(0,0), (3,4), (7,3), (9,3), (10,2)]
		leaf['points'] = list(map(lambda i: self.rotatePoint(i, plant['leafrotation']), leaf['points']))
		leaf['scale'] = 10
		leaf['done'] = False
		if side != 'right':
			leaf['points'] = list(map(lambda i: self.reflectPoint(i, (0,0), (0,1)), leaf['points']))

		leaf['poly'] = vectorio.Polygon(pixel_shader=self.p, 
								  points=list(map(lambda i: self.scalePoint(i, leaf['scale']), leaf['points'])),
								  x=x, y=self.device.display.height+y, 
								  color_index=self.stemfade[plant['color']][0])
		plant['polygroup'].append(leaf['poly'])
		return leaf
	
	def initFlower(self, plant):
		plant['flowercolor'] = self.flowercolors[random.randint(0,len(self.flowercolors)-1)]		
		plant['dotcolor'] = self.dotcolors[random.randint(0,len(self.dotcolors)-1)]
		if plant['flowercolor'] == plant['dotcolor']: plant['dotcolor'] = 15
		if plant['flowertype'] == 1:
			# daisy / circle flower
			flower = vectorio.Circle(pixel_shader=self.p, radius=plant['flowersize'],
									x=plant['startx']-1,
									y=self.device.display.height + plant['currentheight'],
									color_index=plant['flowercolor'])
			dot = vectorio.Rectangle(pixel_shader=self.p, width=plant['dotsize'], height=plant['dotsize'],
									x=round(plant['startx']-(plant['dotsize']/2)), 
									y=round(self.device.display.height + plant['currentheight']-(plant['dotsize']/2)),
									color_index=plant['dotcolor'])
			plant['polygroup'].append(flower)
			plant['polygroup'].append(dot)
		else:
			#tulip
			flower = vectorio.Polygon(pixel_shader=self.p,color_index=plant['flowercolor'],
							 			points=[(0,0),(2,2),(4,0),(6,2),(8,0),(8,6),(5,9),(3,9),(0,6)],
							 			x=round(plant['startx']-4), 
										y=round(self.device.display.height + plant['currentheight']-5))
										
			plant['polygroup'].append(flower)

	def growPlant(self, plant):
		if -plant['currentheight'] < plant['height']:	
			plant['stempoints'] = [(1,0),(-1,0),(-1,plant['currentheight']),(1,plant['currentheight'])]
			plant['stem'].points = plant['stempoints']

			if -plant['currentheight'] < plant['height'] - plant['flowersize']:
				#only draw leaves if we aren't too close to the top of the stem
				if plant['currentheight'] % plant['leafrightmod'] == 0 and plant['currentheight'] != 0:
					plant['leaves'].append(self.initLeaf(plant, plant['startx'], plant['currentheight']))

				if plant['currentheight'] % plant['leafleftmod'] == 0 and plant['currentheight'] != 0:
					plant['leaves'].append(self.initLeaf(plant, plant['startx'], plant['currentheight'], 'left'))
						
			plant['currentheight'] = plant['currentheight'] - 1

		plant['leavesgrowing'] = 0
		for leaf in plant['leaves']:
			if leaf['done'] == False:
				plant['leavesgrowing'] += 1
				leaf['scale'] = leaf['scale'] + 10
				leaf['poly'].points = list(map(lambda i: self.scalePoint(i, leaf['scale']), leaf['points']))
				if leaf['scale'] >= plant['leafscale'] * (leaf['y']/self.device.display.height) + plant['leafscale']:
					leaf['done'] = True
		if  -plant['currentheight'] >= plant['height'] and plant['leavesgrowing'] == 0:
			plant['timer'] = time.monotonic()
			plant['stage'] = 1

	def fadePlant(self, i):
		self.plants[i]['colorindex'] += 1
		if self.plants[i]['colorindex'] < 4:
			p = 0
			while p < len(self.plants[i]['polygroup']):
				self.plants[i]['polygroup'][p].color_index = self.stemfade[self.plants[i]['color']][self.plants[i]['colorindex']]
				p += 1
		else:
			self.removePlant(i)
		
	def removePlant(self, i):
		p = 0
		while p < len(self.plants[i]['polygroup']):
			self.plants[i]['polygroup'].pop(0)
		self.plants.pop(i)
		self.plantgroup.pop(i)

	def _bytes_per_row(self, source_width: int) -> int:
		pixel_bytes = 3 * source_width
		padding_bytes = (4 - (pixel_bytes % 4)) % 4
		return pixel_bytes + padding_bytes
	
	'''def bgRainDown(self):
		y = self.device.display.height-1
		while y > 0:
			x = 0
			while x < self.device.display.width:
				self.bitmap[x,y] = self.bitmap[x,y-1]
				x = x + 1
			y = y - 1
	'''

	def bgFillLine(self):
		x = 0
		while x < self.device.display.width:
			self.bitmap[x,0] = random.randrange(0,7)+22
			x = x + 1

	def drawStars(self):
		x = 0
		while x < 6:
			y = 0
			while y < 6:
				myx = round(x*5 + random.randrange(0,5))
				myy = round(y*4.5 + random.randrange(0,5))
				self.bitmap[myx,myy] = 22
				self.stars.append((myx,myy))
				y = y + 1
			x = x + 1

	def twinkleStars(self):
		for s in self.stars:
			self.bitmap[s[0],s[1]] = random.randrange(0,8)+22

	def moveMoon(self):
		x = self.arc_center[0] + self.arc_radius * math.cos(self.moon_angle)
		y = self.arc_center[1] + self.arc_radius * math.sin(self.moon_angle)
		self.moon_angle += self.settings['daycyclespeed']/300
		self.moongroup.x = int(x)
		self.moongroup.y = int(y)

	def moveSun(self):
		x = self.arc_center[0] + self.arc_radius * math.cos(self.sun_angle)
		y = self.arc_center[1] + self.arc_radius * math.sin(self.sun_angle)
		self.sungroup.x = int(x)
		self.sungroup.y = int(y)
		self.sun_angle += self.settings['daycyclespeed']/300
		angle = math.fmod(math.degrees(self.sun_angle), 360)

		if (self.device.limitStep(2/self.settings['daycyclespeed'], self.lastTwinkleFrame)):
			if angle > 330 or angle < 200:
				self.twinkleStars()
			angle1 = math.fmod(angle + 90, 360)

			brightness = abs((180-angle1)/360) * 0.9 + .25
			self.shadeCloud(self.cloudfg, brightness)
			self.shadeCloud(self.cloudbg, brightness)	
			self.lastTwinkleFrame = time.monotonic()
		if angle > 330 or angle < 200:
			if self.day == 1:
				self.drawStars()
				self.day = 0
		else:
			if self.day == 0:
				self.bitmap.fill(0)
				self.day = 1
				self.stars = [] # deleteStars

	def moveScreen(self, direction, target):
		self.offset_y = self.offset_y + direction
		self.grow_fg.y = self.offset_y
		self.worms_fg.y = self.offset_y + 32
		if self.offset_y % 32 == 0:
			self.screenmoving = 0
			self.currentscreen = target
			#if target == 'Worms':
				
		#print(self.offset_y, self.screenmoving, self.currentscreen)

	def play(self):
		if self.currentscreen == 'Grow' and self.screenmoving == 0:
			if (self.device.limitStep(2.2/self.settings['daycyclespeed'], self.lastCloudFrame)):
				self.moveCloud(self.cloudfg)
				self.moveCloud(self.cloudbg)
				self.lastCloudFrame = time.monotonic()
			
			if (self.device.limitStep(1.3, self.lastPlantInit)):
				if len(self.plants) < 3:
					self.plants.append(self.initPlant())
				self.lastPlantInit = time.monotonic()
		
			if (self.device.limitStep(.02, self.lastFrame)):
				self.moveSun()
				self.moveMoon()
			
			x = 0
			while x < len(self.plantgroup):
				plant = self.plants[x]
				if plant['stage'] == 0:
					self.growPlant(plant)
				elif plant['stage'] == 1:
					self.initFlower(plant)
					plant['stage'] = 2
				elif plant['stage'] == 2:
					if (self.device.limitStep(plant['life'], plant['timer'])):
						plant['stage'] = 3
						plant['timer'] = time.monotonic()
				elif plant['stage'] == 3:
					if (self.device.limitStep(.1, plant['timer'])):
						self.fadePlant(x)
						plant['timer'] = time.monotonic()
				x = x + 1

			if (self.device.limitStep(.08/self.settings['daycyclespeed'], self.beeFrame)):
				x = 0
				while x < len(self.bees):
					self.moveBee(self.bees[x])
					x = x + 1
				self.beeFrame = time.monotonic()

		elif self.currentscreen == 'Worms' and self.screenmoving == 0:
			if (self.device.limitStep(.15/self.settings['daycyclespeed'], self.wormFrame)):
				x = 0
				while x < len(self.worms):
					self.moveWorm(self.worms[x])
					x = x+1
				x = 0
				movingcount = 0
				if len(self.roots) > 0 and len(self.roots) < 30:
					while x < len(self.roots):
						if self.roots[x]['stage'] != 3:
							movingcount += 1
						self.growRoot(self.roots[x])
						x = x+1
					if movingcount == 0:
						self.removeRoot()
				elif len(self.roots) >= 30:
					self.removeRoot()
				else:
					self.roots.append(self.initRoot())

				self.wormFrame = time.monotonic()

			if (self.device.limitStep(60/self.settings['daycyclespeed'], self.wormTrailColorSwitch)):
				self.wormtrailcolor = 1 if self.wormtrailcolor == 0 else 0
				self.wormTrailColorSwitch = time.monotonic()

		if (self.device.limitStep(.02, self.lastFrame)):
			self.lastFrame = time.monotonic()

			if self.device.menu_group.hidden and sum(locals()['keys']):
				if locals()['keys'][3]:
					self.changeTarget()

			if self.screenmoving != 0:
				self.moveScreen(self.screenmoving, self.target)

	def changeTarget(self):
		if self.currentscreen == 'Grow' and self.screenmoving == 0:
			self.screenmoving = -1
			self.target = 'Worms'
			self.initWormScreen()
		elif self.currentscreen == 'Worms' and self.screenmoving == 0:
			self.screenmoving = 1
			self.target = 'Grow'
			self.initGrowScreen()

	def handleRemote(self, key:str):
		if key == 'Enter':
			self.changeTarget()
		print(key)