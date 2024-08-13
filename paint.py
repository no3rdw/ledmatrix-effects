import time, displayio
# add menu items: 
# fillbg (scroll for colors)
# save 
# delete
# play (speed)
# make 'empty caret' for moving without painting

class Paint:
	def __init__(self, device:Device):
		self.name = type(self).__name__
		self.displayname = 'Paint'
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

		self.p = displayio.Palette(10)
		self.p[0] = device.hls(0, 0, 0) # black

		self.p[1] = device.hls(.1, .3, .8) 
		self.p[2] = device.hls(.2, .3, .8)
		self.p[3] = device.hls(.3, .3, .8)
		self.p[4] = device.hls(.4, .3, .8)
		self.p[5] = device.hls(.5, .3, .8)
		self.p[6] = device.hls(.6, .3, .8)
		self.p[7] = device.hls(.7, .3, .8)
		self.p[8] = device.hls(.8, .3, .8)
		self.p[9] = device.hls(.9, .3, .8)

		self.caretPos = [0,0]
		self.selectedColor = 1

		# Create a bitmap with the number of colors in the selected palette
		self.bitmap = displayio.Bitmap(round(device.display.width/4), round(device.display.height/4), 10)
		self.bitmapgrid = displayio.TileGrid(self.bitmap, pixel_shader=self.p)

		self.caret = displayio.Bitmap(1, 1, 10)
		self.caretgrid = displayio.TileGrid(self.caret, pixel_shader=self.p)
		self.caret[0,0] = 1
		self.painting = False

		# Create a TileGrid using the Bitmap and Palette
	
		self.paintGroup = displayio.Group()
		self.paintGroup.scale = 4

		device.clearDisplayGroup(device.effect_group)
		self.paintGroup.append(self.bitmapgrid)
		self.paintGroup.append(self.caretgrid)
		device.effect_group.append(self.paintGroup)

		self.lastblink = 0

	def play(self):
			
		if (self.device.limitStep(.25, self.lastblink)):
			if self.caret[0,0] == 0:
				self.caret[0,0] = self.selectedColor
			else:
				self.caret[0,0] = 0
			self.lastblink = time.monotonic()

		self.caretgrid.x = self.caretPos[0]
		self.caretgrid.y = self.caretPos[1]

		self.lastFrame = time.monotonic()

	def handleRemote(self, key:str):
		if key == 'Left':
			self.caretPos[0] = [lambda: 7, lambda: self.caretPos[0] - 1][self.caretPos[0] > 0]()
		elif key == 'Right':
			self.caretPos[0] = [lambda: 0, lambda: self.caretPos[0] + 1][self.caretPos[0] < 7]()
		elif key == 'Up':
			self.caretPos[1] = [lambda: 7, lambda: self.caretPos[1] - 1][self.caretPos[1] > 0]()
		elif key == 'Down':
			self.caretPos[1] = [lambda: 0, lambda: self.caretPos[1] + 1][self.caretPos[1] < 7]()
		elif len(key) == 1:
			self.selectedColor = int(key)
		elif key == 'Enter' and self.painting == True:
			self.painting = False
		elif key == 'Enter' and self.painting == False:
			self.painting = True
		elif key == 'Back' and self.caretgrid.hidden == True:
			self.caretgrid.hidden = False
		elif key == 'Back' and self.caretgrid.hidden == False:
			self.caretgrid.hidden = True

		if self.painting:
			self.bitmap[self.caretPos] = self.selectedColor