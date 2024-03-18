import time, vectorio, displayio, random, math, bitmaptools

class Grow:

	def __init__(self, device:Device):
		self.name = type(self).__name__
		self.displayname = 'Grow'
		self.device = locals()['device']

		device.clearDisplayGroup(device.effect_group)

		self.menu = [
			#{
			#	'label': 'Setting',
			#	'set': self.setFunction,
			#	'get': self.getFunction
			#}
		]
		self.lastFrame = 0
		self.lastPlantInit = 0
		self.lastCloudFrame = 0
		self.beeFrame = 0
		
		self.p = displayio.Palette(22)
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

		self.stemfade = [
			[1,2,3,4],
			[5,6,7,8],
			[9,10,11,12]
		]

		self.flowercolors = [13,15,16,17,18,21]
		self.dotcolors = [13,15,16]
		self.plants = []

		# Create a bitmap with the number of colors in the selected palette
		self.bitmap = displayio.Bitmap(device.display.width, device.display.height, len(self.p))
		tile_grid = displayio.TileGrid(self.bitmap, pixel_shader=self.p)
		bitmaptools.fill_region(dest_bitmap=self.bitmap, x1=0, y1=0, x2=device.display.width, y2=device.display.height, value=0)
		device.effect_group.append(tile_grid)

		self.cloudgroup = displayio.Group()
		device.effect_group.append(self.cloudgroup)

		self.cloud_b = displayio.OnDiskBitmap('images/cloud2.bmp')
		self.cloudshader = self.device.alphaPalette(self.cloud_b.pixel_shader, True)
		self.cloudshader.make_transparent(2)

		self.ground = vectorio.Rectangle(pixel_shader=self.p, x=0, y=device.display.height-1, width=device.display.width, height=1, color_index=2)
		self.sun = vectorio.Circle(pixel_shader=self.p, x=0, y=0, radius=5, color_index=21)

		self.cloudbg = self.initCloud(1)
		self.cloudfg = self.initCloud(2)
		self.cloudgroup.append(self.sun)
		self.cloudgroup.append(self.cloudbg['group'])
		self.cloudgroup.append(self.cloudfg['group'])

		self.beegroup = displayio.Group()
		self.bee = self.initBee()
		self.bee2 = self.initBee()
		self.bee3 = self.initBee()
		self.beegroup.append(self.bee['group'])
		self.beegroup.append(self.bee2['group'])
		self.beegroup.append(self.bee3['group'])

		self.plantgroup = displayio.Group()
		device.effect_group.append(self.plantgroup)
		device.effect_group.append(self.ground)

		device.effect_group.append(self.beegroup)

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
		return me

	def moveBee(self, me):
		me['group'].x = me['group'].x + random.randint(0,2)-1
		me['group'].y = me['group'].y + random.randint(0,2)-1

		if me['group'].x < -3 or me['group'].x > self.device.display.width or me['group'].y < 0 or me['group'].y > self.device.display.height-3:
			me['group'].y = 16
			me['group'].x = 16
			# re-init params when goes offscreen
			me['delay'] = random.randrange(10,30)

	def initPlant(self):
		plant = {}
		plant['leaves'] = []
		plant['stage'] = 0 # 0 = leaves grow, 1 = flower grow, 2 = wait, 3 = fade, pop

		plant['flowersize'] = random.randint(4,5)
		plant['dotsize'] = plant['flowersize'] - 1
		plant['height'] = random.randint(12,self.device.display.height-(plant['flowersize']*2))
		plant['currentheight'] = 1
		plant['color'] = random.randint(0,2)
		plant['colorindex'] = 0
		plant['polygroup'] = displayio.Group()
		plant['startx'] = random.randint(3, self.device.display.width-6)
		plant['leafleftmod'] = random.randint(4,6)
		plant['leafrightmod'] = plant['leafleftmod'] + (random.randint(0,2)-1)
		plant['leafscale'] = random.randint(100, 150)
		plant['leafrotation'] = -random.randint(20,50)

		plant['stempoints'] = [(1,0),(-1,0),(-1,1),(1,1)]
		plant['stem'] = vectorio.Polygon(pixel_shader=self.p, 
								   	points=plant['stempoints'],
								    x=plant['startx'],
								    y=self.device.display.height,
									color_index=self.stemfade[plant['color']][0])
		plant['polygroup'].append(plant['stem'])
		plant['life'] =  random.randint(15,35)/10
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
		if plant['flowercolor'] == plant['dotcolor']:
			plant['dotcolor'] = 15
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
		self.device.gc(1)
		
	def play(self):
		if (self.device.limitStep(2.7, self.lastCloudFrame)):
			self.moveCloud(self.cloudfg)
			self.moveCloud(self.cloudbg)
			self.lastCloudFrame = time.monotonic()
		if (self.device.limitStep(1.3, self.lastPlantInit)):
			if len(self.plants) < 3:
				self.plants.append(self.initPlant())
			self.lastPlantInit = time.monotonic()
		if (self.device.limitStep(.02, self.lastFrame)):
			self.lastFrame = time.monotonic()
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
		if (self.device.limitStep(.08, self.beeFrame)):
			self.moveBee(self.bee)
			self.moveBee(self.bee2)
			self.moveBee(self.bee3)
			self.beeFrame = time.monotonic()