import displayio, random, time, vectorio, math

class ITYSL2:
	def addCircle(self):
		newcircle = {}

		if	self.totalCircles % 10 == 0 or self.totalCircles % 10 == 1:
			color = 0
		elif self.totalCircles % 2 == 1:
			color = 1
		else:
			color = 2
		newcircle['poly'] = vectorio.Circle(pixel_shader=self.p, x=round(self.device.display.width/2), y=0, radius=1, color_index=color)
		newcircle['pcomplete'] = 1

		self.circles.append(newcircle)
		self.totalCircles = self.totalCircles + 1
		return newcircle['poly']
	
	def __init__(self, device:Device):
		self.name = 'ITYSL2'
		self.device = device

		self.maxcircles = 10
		self.freeze = 0
				
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

		self.circlegroup = displayio.Group()
		self.circles = []

		device.effect_group.append(self.circlegroup)

		self.menu = []
		#self.lastFrame = 0
		self.lastCircleCheck = 0
		self.totalCircles = 0
		self.maxsize = self.device.display.width * 2

	def removeCircle(self, i:int=0):
		#print('circle ', i, 'removed')
		self.circlegroup.pop(i)
		self.circles.pop(i)

	def easeOutSine(self, x:float):
		return math.sin((x * math.pi) / 2)
	
	def play(self):
		if (self.freeze == 0):
			if (self.device.limitStep(.15, self.lastCircleCheck)):
				if len(self.circlegroup) < self.maxcircles:
					self.circlegroup.append(self.addCircle())
					self.device.gc()
					self.lastCircleCheck = time.monotonic()
			i = 0
			while i < len(self.circles):
				me = self.circles[i]
				me['poly'].radius = round(self.easeOutSine(me['pcomplete'] / self.maxsize) * self.maxsize)
				me['pcomplete'] = me['pcomplete'] + 1
				me['poly'].y = round(me['poly'].radius)-1
				if me['poly'].radius >= self.maxsize:
					self.removeCircle(i)
				i = i + 1

		if self.freeze == 1:
			if not locals()['keys'][0]:
				self.freeze = 0

		if self.device.menu_group.hidden and sum(locals()['keys']):
			if locals()['keys'][0]:
				self.freeze = 1
				