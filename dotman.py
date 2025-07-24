import time, displayio, random
from effect import Effect


class Effect(Effect):
	
	class Dotman:
		def __init__(self):
			self.reset()

		def reset(self):
			self.x = 15
			self.y = random.choice([21, 9])
			self.heading = random.choice([1,3])
			self.back = 3 if self.heading == 1 else 1 

		def decideMove(self):
			# check visibility in four directions
			vis = Effect.checkVisRange(self)
			#print(vis)
			pos = 0
			posList = [] # possible directions not blocked by wall
			while pos < 4:
				if 88 in vis[pos] and vis[pos].index(88) < 2:
					posList = [self.back] # ghost is close, turn around
					#print('ghost spotted nearby', pos) # not a valid direction
					break
				elif 88 in vis[pos] and vis[pos].index(88):
					#print ('ghost further away', pos)
					posList.append(pos)
				elif len(vis[pos]):
					posList.append(pos)
				pos += 1
			
			if len(posList) > 1:
				posList.remove(self.back) # remove the option to reverse direction unless its the only option
			
			if len(posList) > 1: #if at a crossroads
				i = 0 # direction index
				m = [] # dots count list
				while i < 4:
					m.append(vis[i].count(7))
					i = i + 1

				if self.heading in posList and m[self.heading] > 0 and random.randrange(0,10) > 6:
					# go in the same direction as previously headed
					direction = self.heading
					#print('straight', direction, posList)
				elif sum(m) > 0: # at least one direction has dots in view, go that way
					direction = m.index(max(m))
					#print('dots',direction, posList)
				else:
					# choose a random direction
					direction = posList[random.randrange(0,len(posList))]
					#print('rand',direction, posList)
			elif len(posList) == 1:
				direction = posList[0]
				#print('noopt', direction)
			else:
				pass
				#print('how did we get here?')
			#print(posList)

			#direction = posList[random.randrange(0,len(posList))]
			Effect.moveObj(self, direction)
			
	class Ghost(Effect):
		def __init__(self, color):
			self.x = 15
			self.y = 15
			self.heading = 0
			self.back = 2
			self.color = color

		def checkHit(self):
			if Effect.dotman.x == self.x and Effect.dotman.y == self.y:
				# DOTMAN DIED
				Effect.dotman.reset()

		def decideMove(self):
			vis = Effect.checkVisRange(self)
			#print(vis)
			pos = 0
			posList = [] # possible directions not blocked by wall
			while pos < 4:
				if 99 in vis[pos]:
					posList = [pos]
					#print('dotman spotted', posList)
					break
				elif len(vis[pos]) != 0:
					posList.append(pos)
				pos += 1
			
			if len(posList) > 1:
				posList.remove(self.back) # remove the option to reverse direction unless its the only option
			
			if len(posList) > 1: #if at a crossroads
				if self.heading in posList and random.randrange(0,10) > 6:
					# go in the same direction as previously headed
					direction = self.heading
					#print('straight', direction, posList)
				else:
					# choose a random direction
					direction = posList[random.randrange(0,len(posList))]
					#print('rand',direction, posList)
			else:
				direction = posList[0]
				#print('noopt', direction)

			Effect.moveObj(self, direction)

	
	def __init__(self, device:Device):
		self.name = 'Dotman'
		super().__init__(device, self.name)
		Effect.device = locals()['device']

		if not self.settings: #set defaults
			self.settings = {'setting':'default'}

		self.p = displayio.Palette(10)
		self.p[0] = Effect.device.hls(0, 0, 0) # outside maze / transparent
		self.p[1] = Effect.device.hls(0, 0, 0) # cleared dot / black
		self.p[2] = Effect.device.hls(.12, .35, .85) # yellow
		self.p[3] = Effect.device.hls(.8, .3, .85) # violet
		self.p[4] = Effect.device.hls(.05, .35, .85) # orange
		self.p[5] = Effect.device.hls(.4, .3, .85) # teal
		self.p[6] = Effect.device.hls(.99, .3, .85) # red
		self.p[7] = Effect.device.hls(.07, .05, .1) #dots
		self.p[8] = (0,0,0) # currently unused
		self.p[9] = Effect.device.hls(.6, .3, .85) # blue (walls)
		self.p.make_transparent(0)
		

		self.effectGroup = displayio.Group()
		Effect.device.clearDisplayGroup(device.effect_group)
		Effect.maze = displayio.Bitmap(device.display.width, device.display.height, 10)
		Effect.sprites = displayio.Bitmap(device.display.width, device.display.height, 10)
		Effect.sprites.fill(0)

		self.mazegrid = displayio.TileGrid(Effect.maze, pixel_shader=self.p)
		self.spritesgrid = displayio.TileGrid(Effect.sprites, pixel_shader=self.p)
		self.effectGroup.append(self.mazegrid)
		self.effectGroup.append(self.spritesgrid)
		
		
		self.loadMaze()

		self.device.clockcolor = self.p[2]
		self.device.clockposition = {'anchor_point':[.5,1],'anchored_position':[17,32]}

		self.menu = [
			#{
			#	'label': 'Label',
			#	'set': self.saveSetting,
			#	'get': lambda: '<Press>'
			#}
        ]
		self.menu.extend(self.effectmenu)
		
		self.lastFrame = 0
		self.lastDotmanMove = 0
		self.lastGhostMove = 0
		self.lastDotCheck = 0
		self.maxGhosts = 4

		Effect.ghosts = []
		g = 0
		while g < self.maxGhosts:
			self.ghosts.append(self.Ghost(g))
			#self.effectGroup.append(self.ghosts[g].px)
			g = g + 1

		Effect.dotman = self.Dotman()
		#self.effectGroup.append(self.dotman.px)

		Effect.device.effect_group.append(self.effectGroup)

		Effect.device.gc(1)

	def play(self):
				
		if (Effect.device.limitStep(.02, self.lastFrame)):
			Effect.sprites.fill(0) # reset sprites layer, to be refreshed in move()
			self.drawSprites()
			self.lastFrame = time.monotonic()
			
		if (self.device.limitStep(.2, self.lastGhostMove)):
			g = 0
			while g < self.maxGhosts:
				self.ghosts[g].decideMove() # ghosts move first, see dotman's last x,y position and write new ghost positions
				g = g + 1
			self.lastGhostMove = time.monotonic()

		if (self.device.limitStep(.14, self.lastDotmanMove)):
			self.dotman.decideMove() # dotman moves second, looks to sprites layer for ghosts' updated positions
			self.lastDotmanMove = time.monotonic()

		if (self.device.limitStep(1, self.lastDotCheck)):
			dotcount = 0
			for y in range(0, self.device.display.height):
				for x in range(0, self.device.display.width):
					if self.maze[x,y] == 7:
						dotcount = dotcount + 1
			if dotcount == 0:
				self.loadMaze()
			self.lastDotCheck = time.monotonic()

	def handleRemote(self, key:str):
		#if key == 'Left':
		#	Effect.moveObj(self.dotman,3)
		#elif key == 'Right':
		#	Effect.moveObj(self.dotman,1)
		#elif key == 'Up':
		#	Effect.moveObj(self.dotman,0)
		#elif key == 'Down':
		#	Effect.moveObj(self.dotman,2)
		pass
	
	def loadMaze(self):
		save = Effect.device.loadData('/dotmansaves/level1.json')
		n = 0
		for y in range(0, Effect.device.display.height):
			for x in range(0, Effect.device.display.width):
				Effect.maze[x,y] = int(save['data'][n])
				n += 1

	def drawSprites(self):
		self.sprites[self.dotman.x,self.dotman.y] = 2 # write dotman sprite to sprites layer
		g = 0
		while g < self.maxGhosts:
			self.sprites[self.ghosts[g].x,self.ghosts[g].y] = self.ghosts[g].color+3 # write ghost to sprites layer
			self.ghosts[g].checkHit()
			g = g + 1


	@classmethod
	def moveObj(self, obj, direction):
		if direction == 3:
			obj.heading = 3
			obj.back = 1
			obj.x = [lambda: Effect.device.display.width-1, lambda: obj.x - 1][obj.x > 0]()
		elif direction == 1:
			obj.heading = 1
			obj.back = 3
			obj.x = [lambda: 0, lambda: obj.x + 1][obj.x + 1 < Effect.device.display.width]()
		elif direction == 0:
			obj.heading = 0
			obj.back = 2
			obj.y = [lambda: Effect.device.display.height-1, lambda: obj.y - 1][obj.y > 0]()
		else:
			obj.heading = 2
			obj.back = 0
			obj.y = [lambda: 0, lambda: obj.y + 1][obj.y + 1 < Effect.device.display.height]()
			
		if obj.__class__.__name__ == 'Dotman' and Effect.maze[obj.x,obj.y] > 0:
			Effect.maze[obj.x,obj.y] = 1 # remove dots by painting over with black
			pass

		return (obj.x,obj.y)
			

	@classmethod
	def checkVizDirection(self, obj, i, axis, direction):
		x = obj.x
		y = obj.y
		range = []
		if axis == 'x':
			while Effect.maze[x+direction,y] != 9:
				
				range.append(Effect.maze[x+direction,y])
				x = x + direction
				if Effect.dotman.x == x+direction and Effect.dotman.y == y:
					range.append(99) # saw dotman
				elif obj.heading == i and Effect.sprites[x+direction,y] == 3:
					range.append(88) # found ghost in direction we're heading
				elif x+direction <= 0 or x+direction >= Effect.device.display.width-1:
					return [0] # edge of screen
			return range	
		else:
			while Effect.maze[x,y+direction] != 9:
				range.append(Effect.maze[x,y+direction])
				y = y + direction
				if Effect.dotman.x == x and Effect.dotman.y == y+direction:
					range.append(99) # saw dotman 
					return range 
				elif obj.heading == i and Effect.sprites[x,y+direction] == 3:
					range.append(88) # found ghost in direction we're heading
					return range 
				elif y+direction <= 0 or y+direction >= Effect.device.display.height-1:
					return [0] # edge of screen
			return range	

	@classmethod
	def checkVisRange(self, obj):
		# check visibility in four directions
		up = self.checkVizDirection(obj, 0, 'y', -1)
		right = self.checkVizDirection(obj, 1, 'x', 1)
		down = self.checkVizDirection(obj, 2, 'y', 1)
		left = self.checkVizDirection(obj, 3, 'x', -1)
		return [up, right, down, left]
