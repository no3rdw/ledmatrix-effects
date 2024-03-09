import time, displayio, random
import adafruit_display_text.label

class Sky:
			
	def initPhrase(self):
		return self.device.getTime()
		#phrases = ["This", 'That', 'The Other Thing']
		#return phrases[random.randrange(0,len(phrases))]

	def initBlimp(self):
		me = {}
		me['group'] = displayio.Group()

		banner = adafruit_display_text.label.Label(
			self.device.font, color=self.device.hls(0,0,0), 
			text=self.initPhrase(), x=20, y=10, background_tight=True)
		
		blimp_f = displayio.OnDiskBitmap('images/blimp-front.bmp')
		blimp_m = displayio.OnDiskBitmap('images/blimp-mid.bmp')
		blimp_r = displayio.OnDiskBitmap('images/blimp-rear.bmp')
		alphashader = self.device.alphaPalette(blimp_f.pixel_shader)
		alphashader.make_transparent(0)
		t = displayio.TileGrid(bitmap=blimp_f, pixel_shader=alphashader, x=0, y=0)
		t1 = displayio.TileGrid(bitmap=blimp_m, pixel_shader=alphashader, x=28, y=0, tile_width=1, width=banner.width-6)
		t2 = displayio.TileGrid(bitmap=blimp_r, pixel_shader=alphashader, x=t1.x+t1.width, y=0)
		
		me['group'].append(t)
		me['group'].append(t1)
		me['group'].append(t2)
		me['group'].x = self.device.display.width
		me['group'].y = round((self.device.display.height-24)/2)
		me['width'] = t2.x + t2.width
		me['group'].append(banner)
		me['type'] = 'blimp'
		me['delay'] = random.randrange(40,60)
		me['done'] = False
		print('init blimp complete')
		self.device.gc(1)
		return me

	def initPlane(self):
		me = {}
		me['group'] = displayio.Group()

		plane_b = displayio.OnDiskBitmap('images/plane.bmp')
		plane_b.pixel_shader.make_transparent(6)
		
		t = displayio.TileGrid(bitmap=plane_b, 
						pixel_shader=self.device.alphaPalette(plane_b.pixel_shader),
						x=0, y=round((self.device.display.height-24)/2))
		me['group'].append(t)
		me['group'].x = self.device.display.width
		banner = adafruit_display_text.label.Label(
			self.device.font, color=self.device.hls(.01,.2,1), 
			background_color=self.device.hls(0,1,0), 
			text=' '+self.initPhrase()+' ', x=49, y=11)
		me['group'].append(banner)
		me['width'] = 49 + banner.width
		me['type'] = 'plane'
		me['delay'] = random.randrange(10,30)
		me['done'] = False
		print('init plane complete')
		self.device.gc(1)
		return me

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

		self.planegroup = self.initPlane()

		self.cloud_b = displayio.OnDiskBitmap('images/cloud2.bmp')
		self.cloudshader = self.device.alphaPalette(self.cloud_b.pixel_shader, True)
		self.cloudshader.make_transparent(2)
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
		me['group'].y = self.setCloudY(scale)
		me['group'].x = random.randrange(-self.device.display.width, self.device.display.width)
		me['delay'] = random.randrange(10,30)
		c = displayio.TileGrid(bitmap=self.cloud_b,
						 pixel_shader=self.cloudshader,
						 x=0, y=0)
		me['group'].append(c)
		return me
	
	def setCloudY(self, scale):
		if scale == 1:
			return random.randrange(-4,4)
		elif scale == 2:
			return random.randrange(5,15)
		else:
			return random.randrange(15,32)
	
	def moveCloud(self, me):
		me['group'].x = me['group'].x + me['scale']	
		if me['group'].x > self.device.display.width+(me['delay']*me['scale']):
			# re-init params after cloud goes offscreen
			me['group'].x = 0 - round(13 * me['scale'])
			me['group'].y = self.setCloudY(me['scale'])
			me['delay'] = random.randrange(10,30)

	def movePlane(self, me):
		if random.randrange(0,8) == 1:
			pass
			me['group'].y = me['group'].y + random.randrange(-1,2)
		me['group'].x -= 1
		if me['group'].x < -me['width']-me['delay']:
			me['done'] = True

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

			if self.planegroup['type'] == 'blimp' and self.planegroup['done']:
				self.planegroup = self.initPlane()
				self.device.effect_group[3] = self.planegroup['group']
			elif self.planegroup['type'] == 'plane' and self.planegroup['done']:
				self.planegroup = self.initBlimp()
				self.device.effect_group[3] = self.planegroup['group']


