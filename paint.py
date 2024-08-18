import time, displayio, vectorio, os, random
from effect import Effect

class Effect(Effect):
	def __init__(self, device:Device):
		self.name = 'Paint'
		self.device = device

		device.clearDisplayGroup(device.effect_group)
		self.fillbg = 0

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
				'set': lambda d: (self.loadFile(self.safeCycleFilenames(d))),
				'get': lambda: str(self.currentSaveFilename)
			},{
				'label': 'Save',
				'set': self.saveCurrentToDisk,
				'get': lambda: '<Press>'
			},{
				'label': 'PlaySpd',
				'set': self.setPlayspeed,
				'get': self.getPlayspeed
			}	
		]
	

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
		

		# Create a bitmap with the number of colors in the selected palette
		self.bitmap = displayio.Bitmap(device.display.width, device.display.height, 9)
		self.nextframe = displayio.Bitmap(device.display.width, device.display.height, 9)
		self.undo = displayio.Bitmap(device.display.width, device.display.height, 9)
		self.bitmapgrid = displayio.TileGrid(self.bitmap, pixel_shader=self.p)

		self.caret = vectorio.Polygon(pixel_shader=self.p, points=[(0,0),(0,4),(4,0)], x=0, y=0, color_index=1)
		self.marker = vectorio.Polygon(pixel_shader=self.p, points=[(0,0),(4,0),(4,4),(0,4)], x=0, y=0, color_index=9)
		self.caretGroup = displayio.Group()
		self.caretGroup.hidden = True
		self.caretGroup.append(self.caret)
		self.caretGroup.append(self.marker)
		
		self.setScale(4)
		self.painting = False
		self.playspeed = 0

		# Create a TileGrid using the Bitmap and Palette
	
		self.paintGroup = displayio.Group()

		device.clearDisplayGroup(device.effect_group)
		self.paintGroup.append(self.bitmapgrid)
		self.paintGroup.append(self.caretGroup)
		device.effect_group.append(self.paintGroup)

		self.lastblink = 0
		self.lastload = 0
		self.blinkstate = False

		self.allSaveFilenames = self.getAllFilenames()
		self.loadFile(self.allSaveFilenames[0])
		
	def getAllFilenames(self):
		filenames = [filename.split('.')[0] for filename in os.listdir('/paintsaves/')]
		return sorted(filenames)

	def play(self):
		if (self.device.limitStep(.25, self.lastblink)):
			if self.blinkstate == False:
				self.caret.color_index = self.selectedColor
				self.marker.color_index = self.selectedColor
				self.blinkstate = True
			else:
				if self.selectedColor == 9:
					self.caret.color_index = 0
					self.marker.color_index = 0
				else:
					self.caret.color_index = 9
					self.marker.color_index = 9
				self.blinkstate = False
			self.lastblink = time.monotonic()

		if (self.playspeed != 0 and self.device.limitStep(self.playspeed, self.lastload)):
			self.loadFile(self.safeCycleFilenames(1))
			
			self.lastload = time.monotonic()
		elif self.playspeed == 0:
			self.lastload = time.monotonic()

	def safeCycleFilenames(self, direction:int=1):
		# wrapper for cycleOption to account for unsaved new image
		# if we are on an unsaved new image and are abandoning it, skip to either the last or first saved image
		if self.currentSaveFilename == 'Unnamed' and direction == -1:
			self.currentSaveFilename = self.allSaveFilenames[len(self.allSaveFilenames)-1]
		elif self.currentSaveFilename == 'Unnamed' and direction == 1:
			self.currentSaveFilename = self.allSaveFilenames[0]
		else:
			self.currentSaveFilename = self.device.cycleOption(self.allSaveFilenames, self.currentSaveFilename, direction)
		return self.currentSaveFilename

	def handleRemote(self, key:str):
		if key == 'PlayPause':
			pass
		elif key == 'VolDown':
			self.loadFile(self.safeCycleFilenames(-1))
			locals()['menu'].showOverlay(self.currentSaveFilename)
		elif key == 'VolUp':
			self.loadFile(self.safeCycleFilenames(1))
			locals()['menu'].showOverlay(self.currentSaveFilename)
		else:
			self.caretGroup.hidden = False # show cursor on all other button presses
			if key == 'Left':
				self.caretPos[0] = [lambda: self.device.display.width-self.scale, lambda: self.caretPos[0] - self.scale][self.caretPos[0] > 0]()
				self.paint()
			elif key == 'Right':
				self.caretPos[0] = [lambda: 0, lambda: self.caretPos[0] + self.scale][self.caretPos[0] + self.scale < self.device.display.width]()
				self.paint()
			elif key == 'Up':
				self.caretPos[1] = [lambda: self.device.display.height-self.scale, lambda: self.caretPos[1] - self.scale][self.caretPos[1] > 0]()
				self.paint()
			elif key == 'Down':
				self.caretPos[1] = [lambda: 0, lambda: self.caretPos[1] + self.scale][self.caretPos[1] + self.scale < self.device.display.height]()
				self.paint()
			elif key == 'Back':
				self.switchPainting(False)
				self.bitmap.blit(0,0,self.undo)
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
				self.setScale(self.device.cycleOption([4,2,1], self.scale, 1))
			
	def paint(self):
		self.caretGroup.x = self.caretPos[0]
		self.caretGroup.y = self.caretPos[1]
		if self.painting:
			self.undo.blit(0,0,self.bitmap)
			y=0
			while y<self.scale:
				x=0
				while x<self.scale:
					self.bitmap[(self.caretPos[0]+x,self.caretPos[1]+y)] = self.selectedColor
					x += 1
				y+=1
			
	def switchPainting(self, b):
		if b:
			self.painting = True
			self.marker.hidden = False
			self.caret.hidden = True
		else:
			self.painting = False
			self.marker.hidden = True
			self.caret.hidden = False

	def setScale(self, scale):
		self.scale = scale
		self.caretPos[0] = self.caretPos[0] - (self.caretPos[0] % scale)
		self.caretPos[1] = self.caretPos[1] - (self.caretPos[1] % scale)
		if self.caretPos[0] > self.device.display.width-1:
			self.caretPos[0] = 0
		if self.caretPos[1] > self.device.display.height-1:
			self.caretPos[1] = 0
		self.caretGroup.x = self.caretPos[0]
		self.caretGroup.y = self.caretPos[1]
		self.caret.points = [(0,0),(0,scale),(scale,0)]
		self.marker.points = [(0,0),(scale,0),(scale,scale),(0,scale)]

	def loadFile(self, filename):
		self.currentSaveFilename = filename
		saveContents = self.device.loadData('/paintsaves/'+self.currentSaveFilename+'.json')
		self.loadSaveContents(saveContents)

	def loadSaveContents(self, save):
		self.switchPainting(False)
		n = 0
		for y in range(0, self.device.display.height):
			for x in range(0, self.device.display.width):
				self.nextframe[x,y] = int(save['data'][n])
				n += 1
			
		self.bitmap.blit(0,0,self.nextframe)
		self.undo.blit(0,0,self.nextframe)
		self.caretGroup.hidden = True
		self.lastload = time.monotonic()
		self.device.gc(1)

	def saveCurrentToDisk(self, direction:int=0):
		output = ""
		for y in range(0, self.device.display.height):
			for x in range(0, self.device.display.width):
				output = output + str(self.bitmap[x,y])
		newData = {"data": output}

		if self.currentSaveFilename == 'Unnamed':
			new = True
			self.currentSaveFilename = str(int(self.allSaveFilenames[len(self.allSaveFilenames)-1])+1)
		else:
			new = False
		print(self.currentSaveFilename)
		self.device.writeData(newData, '/paintsaves/'+self.currentSaveFilename+'.json')

		if new:
			self.allSaveFilenames = self.getAllFilenames()
			print(self.allSaveFilenames)

		locals()['menu'].hideMenu()
	
	def setNew(self, direction:int=0):
		locals()['menu'].hideMenu()
		self.currentSaveFilename = "Unnamed"
		newSave = {"data":'0'*(self.device.display.height*self.device.display.width)}
		self.loadSaveContents(newSave)

	def getFillBackground(self):
		return str(self.fillbg)

	def setFillBackground(self, direction:int):
		self.fillbg = self.device.cycleOption([0,1,2,3,4,5,6,7,8,9], self.fillbg, direction)
		self.bitmap.fill(self.fillbg)

	def setPlayspeed(self, direction:int):
		self.playspeed = self.device.cycleOption([0,.5,1,5,10,30,60], self.playspeed, direction)

	def getPlayspeed(self):
		return str(self.playspeed) + 'sec'
	