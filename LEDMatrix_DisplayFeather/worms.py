import time, random, displayio
from effect import Effect

class Effect(Effect):
	def __init__(self, device:Device):
		self.name = 'Worms'
		super().__init__(device, self.name)
		
		self.device = locals()['device']
		if not self.settings: #set defaults
			self.settings = {"count":5}

		device.clearDisplayGroup(device.effect_group)

		self.p = displayio.Palette(10)
		self.p[0] =  device.hls(.04, .05, .5) # bg
		self.p[1] = device.hls(.04, .06, .5) # worm poop
		
		self.p[2] = device.hls(.01, .2, .6) # worm
		self.p[3] = device.hls(.015, .25, .65) # worm2

		self.p[4] = device.hls(.04, .1, .3) # mineral
		self.p[5] = device.hls(.04, .08, .35) # mineral2
		self.p[6] = device.hls(.04, .06, .4) # mineral3

		# Create a bitmap with the number of colors in the selected palette
		self.bitmap = displayio.Bitmap(device.display.width, device.display.height, len(self.p))
		self.tile_grid = displayio.TileGrid(self.bitmap, pixel_shader=self.p)
		device.effect_group.append(self.tile_grid)

		self.wormtrailcolor = 0
		self.wormTrailColorSwitch = 0
		self.mineralGrowTime = time.monotonic()

		x = 0
		while x < 25:
			# draw some random dots
			self.bitmap[(random.randint(0,self.device.display.width-1), random.randint(0,self.device.display.height-1))] = random.randint(4,6)
			x = x + 1
		
		
		self.createWorms(self.settings['count'])

		self.menu = [
			{
				'label': 'Count',
				'set': self.setCount,
				'get': lambda: str(self.settings['count'])
			}
        ]
		self.menu.extend(self.effectmenu)
		
		self.lastFrame = 0

	def setCount(self, d):
		self.settings['count'] = self.device.cycleOption([1,3,5,10,15,20,25], self.settings['count'], d)
		x = 1 if self.wormtrailcolor == 0 else 0
		self.bitmap.fill(x)
		self.wormTrailColorSwitch = time.monotonic()
		self.createWorms(self.settings['count'])

	def createWorms(self, count:int=5):
		x = 0
		self.worms = []
		while x < count:
			z = self.initWorm()
			self.worms.append(z)
			x = x+1

	def initWorm(self):
		me = {}
		me['y'] = random.randint(0, self.device.display.height-1)
		me['x'] = random.randint(0, self.device.display.width-1)
		me['cells'] = [(me['x'],me['y'])]
		me['color'] = random.randint(2,3)
		me['cd'] = 2 #change direction countdown
		me['fc'] = False # force change direction

		self.bitmap[me['cells'][0]] = me['color']

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
		elif me['x'] < 0:
			me['x'] = 0

		if me['y'] > self.device.display.height-1:
			me['y'] = self.device.display.height-1
			me['fc'] = True
		elif me['y'] <= 0:
			me['y'] = 0
			me['fc'] = True

		me['cells'].append((me['x'],me['y']))
		self.bitmap[(me['x'],me['y'])] = me['color']
		if len(me['cells']) > 7:
			self.bitmap[(me['cells'][0][0], me['cells'][0][1])] = self.wormtrailcolor
			me['cells'].pop(0)

		move = random.randint(1,5)
		if me['fc'] == True and (me['x'] == self.device.display.width-1 or (me['y'] == self.device.display.height-1)):
			me['direction'] = self.device.cycleOption([1,2,3,4,5,6,7,8], me['direction'], -3) # large counterclockwise move
			me['fc'] = False
			me['cd'] = 2
		elif me['fc'] == True and (me['x'] == 0 or (me['y'] == 0)):
			me['direction'] = self.device.cycleOption([1,2,3,4,5,6,7,8], me['direction'], 3) # large clockwise move
			me['fc'] = False
			me['cd'] = 2
		elif (move == 5 and me['cd'] <= 0):
			me['direction'] = self.device.cycleOption([1,2,3,4,5,6,7,8], me['direction'], 1)
			me['cd'] = 2
		elif (move == 4 and me['cd'] <= 0):
			me['direction'] = self.device.cycleOption([1,2,3,4,5,6,7,8], me['direction'], -1)
			me['cd'] = 2
		else:
			me['cd'] = me['cd'] - 1

	def play(self):
		if (self.device.limitStep(.1, self.lastFrame)):
			x = 0
			while x < len(self.worms):
				self.moveWorm(self.worms[x])
				x = x+1

			self.lastFrame = time.monotonic()
		if (self.device.limitStep(round(300/len(self.worms),0), self.wormTrailColorSwitch)):
			self.wormtrailcolor = 1 if self.wormtrailcolor == 0 else 0
			self.wormTrailColorSwitch = time.monotonic()

		if (self.device.limitStep(round(30/len(self.worms),0), self.mineralGrowTime)):
			self.bitmap[(random.randrange(0,self.device.display.width-1),random.randrange(0,self.device.display.height-1))] = random.randrange(4,6)
			self.mineralGrowTime = time.monotonic()


	def handleRemote(self, key:str):
		if key == 'Enter':
			self.worms.append(self.initWorm())