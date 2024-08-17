import time, displayio, vectorio
# add menu items: 
# fillbg (scroll for colors)
# save 
# delete
# play (speed)


class Paint:
	def __init__(self, device:Device):
		self.name = type(self).__name__
		self.displayname = 'Paint'
		self.device = locals()['device']

		device.clearDisplayGroup(device.effect_group)
		self.fillbg = 0

		self.paintData = self.device.loadData('paint.json')

		self.menu = [
			{
				'label': 'Fill BG',
				'set': self.setFillBackground,
				'get': self.getFillBackground
			},{
				'label': 'New',
				'set': self.setNew,
				'get': lambda: '<Press>'
			},{
				'label': 'Load',
				'set': lambda d: (self.load(self.device.cycleOption(self.saveslots, self.saveslot, d))),
				'get': lambda: 'Save' + str(self.saveslot)
			},{
				'label': 'SaveAll',
				'set': self.saveAllToDisk,
				'get': lambda: '<Press>'
			},{
				'label': 'PlaySpd',
				'set': self.setPlayspeed,
				'get': self.getPlayspeed
			}
			
		]
		self.lastFrame = 0

		self.p = displayio.Palette(10)
		self.p[0] = device.hls(0, 0, 0) # black
		self.p[1] = device.hls(.99, .3, .85) # red
		self.p[2] = device.hls(.05, .35, .85) # orange
		self.p[3] = device.hls(.12, .35, .85) # yellow
		self.p[4] = device.hls(.25, .3, .85) # grass green
		self.p[5] = device.hls(.4, .3, .85) # teal
		self.p[6] = device.hls(.6, .3, .85) # blue
		self.p[7] = device.hls(.7, .3, .85) # purple
		self.p[8] = device.hls(.8, .3, .85) # violet
		self.p[9] = device.hls(0, 1, 0) #white

		self.caretPos = [0,0]
		self.selectedColor = 1
		self.scale = 4

		self.undo = []

		# Create a bitmap with the number of colors in the selected palette
		self.bitmap = displayio.Bitmap(round(device.display.width/self.scale), round(device.display.height/self.scale), 9)
		self.bitmapgrid = displayio.TileGrid(self.bitmap, pixel_shader=self.p)

		self.caret = vectorio.Polygon(pixel_shader=self.p, points=[(0,0),(0,self.scale),(self.scale,self.scale),(self.scale,0)], x=0, y=0, color_index=1)
		self.window = vectorio.Polygon(pixel_shader=self.p, points=[(1,1),(3,1),(3,3),(1,3)], x=0, y=0, color_index=0)
		self.window.hidden = True

		self.caretGroup = displayio.Group()
		self.caretGroup.hidden = True
		self.caretGroup.append(self.caret)
		self.caretGroup.append(self.window)
		
		self.painting = False
		self.playspeed = 0

		# Create a TileGrid using the Bitmap and Palette
	
		self.paintGroup = displayio.Group()
		self.paintGroup.scale = 4

		device.clearDisplayGroup(device.effect_group)
		self.paintGroup.append(self.bitmapgrid)
		self.paintGroup.append(self.caretGroup)
		device.effect_group.append(self.paintGroup)

		self.lastblink = 0
		self.lastload = 0
		self.saveslot = 0
		self.blinkstate = False

		self.load(self.saveslot)

	def play(self):
		if (self.device.limitStep(.25, self.lastblink)):
			if self.blinkstate == False:
				self.caret.color_index = self.selectedColor
				self.blinkstate = True
			else:
				self.caret.color_index = 9
				self.blinkstate = False
			self.lastblink = time.monotonic()

		if (self.device.limitStep(.1, self.lastFrame)):
			self.caretGroup.x = self.caretPos[0]
			self.caretGroup.y = self.caretPos[1]
			self.lastFrame = time.monotonic()

		if (self.playspeed != 0 and self.device.limitStep(self.playspeed, self.lastload)):
			self.load(self.device.cycleOption(self.saveslots, self.saveslot, 1))
			
			self.lastload = time.monotonic()
		elif self.playspeed == 0:
			self.lastload = time.monotonic()

	def handleRemote(self, key:str):
		#print(key)
		if key == 'PlayPause':
			pass
		elif key == 'VolDown':
			self.saveCurrentToMem()
			self.load(self.device.cycleOption(self.saveslots, self.saveslot, -1))
			locals()['menu'].showOverlay('Save' + str(self.saveslot))
		elif key == 'VolUp':
			self.saveCurrentToMem()
			self.load(self.device.cycleOption(self.saveslots, self.saveslot, 1))
			locals()['menu'].showOverlay('Save' + str(self.saveslot))
		elif key == 'Left':
			self.caretPos[0] = [lambda: 7, lambda: self.caretPos[0] - 1][self.caretPos[0] > 0]()
			self.paint()
		elif key == 'Right':
			self.caretPos[0] = [lambda: 0, lambda: self.caretPos[0] + 1][self.caretPos[0] < 7]()
			self.paint()
		elif key == 'Up':
			self.caretPos[1] = [lambda: 7, lambda: self.caretPos[1] - 1][self.caretPos[1] > 0]()
			self.paint()
		elif key == 'Down':
			self.caretPos[1] = [lambda: 0, lambda: self.caretPos[1] + 1][self.caretPos[1] < 7]()
			self.paint()
		elif key == 'Back':
			if len(self.undo) > 0:
				self.switchPainting(False)
				self.bitmap[self.undo[0][0]] = self.undo[0][1]
				self.undo.pop(0)
		elif self.caretGroup.hidden == True:
			self.switchCaretVisible(False)
			if len(key) == 1:
				self.selectedColor = int(key)
				self.caret.color_index = int(key)
		elif len(key) == 1:
			self.selectedColor = int(key)
			self.caret.color_index = int(key)
			self.paint()
		elif key == 'Enter' and self.painting == True:
			self.switchPainting(False)
		elif key == 'Enter' and self.painting == False:
			self.switchPainting(True)
			self.paint()
		elif key == 'StopMode':
			self.switchCaretVisible(True)
		
	def paint(self):
		if self.painting:
			self.undo.insert(0, [self.caretPos[:], self.bitmap[self.caretPos]])
			self.bitmap[self.caretPos] = self.selectedColor

	def switchPainting(self, b):
		if b:
			self.painting = True
			self.window.hidden = False
		else:
			self.painting = False
			self.window.hidden = True

	def switchCaretVisible(self, b):
		if b:
			self.caretGroup.hidden = True
			self.switchPainting(False)
		else:
			self.caretGroup.hidden = False

	def load(self, saveslot:str):
		self.device.gc(1)
		self.switchPainting(False)
		self.getSaveSlots()
		n = 0
		for y in range(0, 8):
			for x in range(0, 8):
				self.bitmap[x,y] = int(self.paintData['paintSaves'][saveslot][n])
				n += 1
		self.saveslot = saveslot
		self.undo = []

	def saveCurrentToMem(self):
		output = ""
		for y in range(0, 8):
			for x in range(0, 8):
				output = output + str(self.bitmap[x,y])
		self.paintData['paintSaves'][self.saveslot] = output
		
	def saveAllToDisk(self, direction:int=0):
		self.saveCurrentToMem()
		self.device.writeData(self.paintData, 'paint.json')
	
	def setNew(self, direction:int=0):
		newID = len(self.paintData['paintSaves'])
		self.paintData['paintSaves'].append('0'*64)
		self.load(newID)
		locals()['menu'].hideMenu()

	def getFillBackground(self):
		return str(self.fillbg)

	def setFillBackground(self, direction:int):
		self.fillbg = self.device.cycleOption([0,1,2,3,4,5,6,7,8,9], self.fillbg, direction)
		self.bitmap.fill(self.fillbg)

	def setPlayspeed(self, direction:int):
		self.playspeed = self.device.cycleOption([0,.25,.5,1,5,10,30,60], self.playspeed, direction)

	def getPlayspeed(self):
		return str(self.playspeed) + 'sec'
	
	def getSaveSlots(self):
		self.saveslots = list(range(len(self.paintData['paintSaves'])))