import time, vectorio, displayio
from effect import Effect

class Effect(Effect):
	def __init__(self, device:Device):
		self.name = 'Colorbars'
		super().__init__(device, self.name)
		self.device = locals()['device']

		#if not self.settings: #set defaults
		#	self.settings = {'setting':'default'}

		device.clearDisplayGroup(device.effect_group)

		self.menu = [
			#{
			#	'label': 'Label',
			#	'set': self.saveSetting,
			#	'get': lambda: '<Press>'
			#}
		]

		self.device.clockcolor = 0xFFFFFF
		self.device.clockposition = {'anchor_point':[1,1],'anchored_position':[31,30]}
		
		self.p = displayio.Palette(11)
		self.p[0] = device.hls(0, 0, 0) # black
		self.p[1] = device.hls(1, .5, 0) # gray
		self.p[2] = device.hls(.2, .5, .7) # yellow
		self.p[3] = device.hls(.5, .4, .7) # cyan
		self.p[4] = device.hls(.3, .25, .8) # green
		self.p[5] = device.hls(.8, .2, .8) # magenta
		self.p[6] = device.hls(0, .35, .85) # red
		self.p[7] = device.hls(.65, .1, 1) # blue
		self.p[8] = device.hls(.65, .04, .9) # navy
		self.p[9] = device.hls(1, .7, 0) # white
		self.p[10] = device.hls(.75, .04, .8) # purple

		bars = [
					vectorio.Rectangle(pixel_shader=self.p, color_index=1, width=4, height=20, x=2, y=2),
					vectorio.Rectangle(pixel_shader=self.p, color_index=2, width=4, height=20, x=6, y=2),
					vectorio.Rectangle(pixel_shader=self.p, color_index=3, width=4, height=20, x=10, y=2),
					vectorio.Rectangle(pixel_shader=self.p, color_index=4, width=4, height=20, x=14, y=2),
					vectorio.Rectangle(pixel_shader=self.p, color_index=5, width=4, height=20, x=18, y=2),
					vectorio.Rectangle(pixel_shader=self.p, color_index=6, width=4, height=20, x=22, y=2),
					vectorio.Rectangle(pixel_shader=self.p, color_index=7, width=4, height=20, x=26, y=2),
					vectorio.Rectangle(pixel_shader=self.p, color_index=7, width=4, height=3, x=2, y=22),
					vectorio.Rectangle(pixel_shader=self.p, color_index=0, width=4, height=3, x=6, y=22),
					vectorio.Rectangle(pixel_shader=self.p, color_index=5, width=4, height=3, x=10, y=22),
					vectorio.Rectangle(pixel_shader=self.p, color_index=0, width=4, height=3, x=14, y=22),
					vectorio.Rectangle(pixel_shader=self.p, color_index=3, width=4, height=3, x=18, y=22),
					vectorio.Rectangle(pixel_shader=self.p, color_index=0, width=4, height=3, x=22, y=22),
					vectorio.Rectangle(pixel_shader=self.p, color_index=1, width=4, height=3, x=26, y=22),
					vectorio.Rectangle(pixel_shader=self.p, color_index=8, width=4, height=5, x=2, y=25),
					vectorio.Rectangle(pixel_shader=self.p, color_index=9, width=4, height=5, x=6, y=25),
					vectorio.Rectangle(pixel_shader=self.p, color_index=10, width=4, height=5, x=10, y=25),
					]
		
		for bar in bars:
			device.effect_group.append(bar)

		self.menu.extend(self.effectmenu)
		
		self.lastFrame = 0

	def play(self):
		if (self.device.limitStep(.1, self.lastFrame)):
			# do stuff
			
			self.lastFrame = time.monotonic()

	def handleRemote(self, key:str):
		if key == 'Enter':
			pass