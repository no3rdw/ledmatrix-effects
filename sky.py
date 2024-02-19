import time, displayio, random
import adafruit_display_text.label

class Sky:
	def __init__(self, device:Device):
		self.name = type(self).__name__
		self.displayname = 'Sky'
		self.device = locals()['device']

		p = displayio.Palette(3)
		p[0] = device.hls(.55, .6, .75) # blue sky
		colorcount = len(p)
		bg = displayio.Bitmap(device.display.width, device.display.height, colorcount)
		bggrid = displayio.TileGrid(bg, pixel_shader=p)

		device.clearDisplayGroup(device.effect_group)

		self.planegroup = {}
		self.planegroup['group'] = displayio.Group()

		plane_b = displayio.OnDiskBitmap('images/plane.bmp')
		plane_b.pixel_shader.make_transparent(7)
		t = displayio.TileGrid(bitmap=plane_b, pixel_shader=plane_b.pixel_shader, x=0, y=round((self.device.display.height-24)/2))
		self.planegroup['group'].append(t)
		self.planegroup['group'].x = self.device.display.width
		self.planewidth = 49

		self.banner = adafruit_display_text.label.Label(
			device.font, color=device.hls(.01,.2,1), 
			background_color=device.hls(.1,1,1), 
			text=' Go to bed! ', x=self.planewidth, y=11)
		self.planegroup['group'].append(self.banner)
	
		self.cloud_b = displayio.OnDiskBitmap('images/cloud2.bmp')
		self.cloud_b.pixel_shader.make_transparent(2)
		self.cloudbg = self.initCloud(1)
		self.cloudnbg = self.initCloud(2)
		self.cloudfg = self.initCloud(3)

		#t.flip_x=True

		device.effect_group.append(bggrid)
		device.effect_group.append(self.cloudbg['group'])
		device.effect_group.append(self.cloudnbg['group'])
		device.effect_group.append(self.planegroup['group'])
		device.effect_group.append(self.cloudfg['group'])

		self.menu = [
			#{
			#	'label': 'Setting',
			#	'set': self.setFunction,
			#	'get': self.getFunction
			#}
        ]
		self.lastCloudFrame = 0
		self.lastPlaneFrame = 0

	def initCloud(self, scale):
		me = {}
		me['scale'] = scale
		me['group'] = displayio.Group(scale=me['scale'])

		c = displayio.TileGrid(bitmap=self.cloud_b, pixel_shader=self.cloud_b.pixel_shader, x=0, y=self.setCloudY(scale))
		me['group'].append(c)
		return me
	
	def setCloudY(self, scale):
		if scale == 1:
			return random.randrange(0,15)
		elif scale == 2:
			return random.randrange(-10,10)
		else:
			return random.randrange(3,10)
	
	def moveCloud(self, me):
		me['group'].x = me['group'].x + me['scale']
		if me['group'].x > self.device.display.width:
			me['group'].x = 0 - round(13 * me['scale'])
			me['group'].y = self.setCloudY(me['scale'])

	def movePlane(self, me):
		if random.randrange(0,4) == 1:
			me['group'].y = me['group'].y + random.randrange(-1,2)
		me['group'].x -= 1
		print(me['group'].x)
		if me['group'].x < -self.planewidth-self.banner.width-5:
			me['group'].x = self.device.display.width
			me['group'].y = round((self.device.display.height-24)/2)

	def play(self):
		if (self.device.limitStep(.03, self.lastCloudFrame)):
			# do stuff
			self.moveCloud(self.cloudfg)
			self.moveCloud(self.cloudbg)
			self.moveCloud(self.cloudnbg)
			self.lastCloudFrame = time.monotonic()

		if (self.device.limitStep(.1, self.lastPlaneFrame)):
			self.movePlane(self.planegroup)
			self.lastPlaneFrame = time.monotonic()


