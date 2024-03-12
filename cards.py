import time, vectorio, displayio, random
import adafruit_display_text.label
import bitmaptools

class Cards:
	def __init__(self, device:Device, style:str='Cards'):
		self.name = type(self).__name__
		self.displayname = 'Bounce'
		self.device = locals()['device']

		device.clearDisplayGroup(device.effect_group)

		self.selectedStyle = style
		self.styles = {
			'Cards': {
				'cardcolors': [2,3],
				'displaylabels': True,
				'shape': 'rect',
				'sizex': lambda : 8,
				'sizey': lambda : 10,
				'border': True,
				'bgindex': 0,
				'cardinterval': lambda : 1,
				'gravity': lambda : random.randint(30,70)/100,
				'dx': lambda : -1, # varying the x travel distance does not work well when the border/labels are enabled
				'trail': True
			},
			'90s': {
				'cardcolors': [3,1,4,5,6,7],
				'displaylabels': False,
				'shape': 'square',
				'sizex': lambda : random.randint(1,5),
				'border': False,
				'bgindex': 3,
				'cardinterval': lambda : random.randint(40,200)/100,
				'gravity': lambda : random.randint(10,60)/100,
				'dx': lambda : random.randint(60, 100)/-100,
				'trail': True
			},
			'B-Balls': {
				'cardcolors': [8,9,10],
				'displaylabels': False,
				'shape': 'circle',
				'sizex': lambda : 8,
				'border': False,
				'bgindex': 1,
				'cardinterval': lambda : .9,
				'gravity': lambda : .2,
				'dx': lambda : random.randint(10, 100)/-100,
				'trail': False
			}
		}

		self.p = displayio.Palette(11)
		self.p[0] = device.hls(.35, .2, 1) # green bg
		self.p[1] = device.hls(1, 1, 0) # white
		self.p[2] = device.hls(0, .35, 1) # red
		self.p[3] = device.hls(1, .0, 0) # black
		self.p[4] = device.hls(.25, .5, 1) # 
		self.p[5] = device.hls(.45, .5, 1) # 
		self.p[6] = device.hls(.65, .5, 1) # 
		self.p[7] = device.hls(.85, .5, 1) #
		self.p[8] = device.hls(.05, .45, 1) #
		self.p[9] = device.hls(.02, .5, .95) #
		self.p[10] = device.hls(.08, .3, 1) #

		self.cardcolors = self.styles[self.selectedStyle]['cardcolors']
		self.lastcolor = self.cardcolors[0]

		self.displaylabels = self.styles[self.selectedStyle]['displaylabels']
		self.cardlabels = ['A','2','3','4','5','6','7','8','9','10','J','Q','K']
		self.lastcardlabel = self.cardlabels[random.randint(0, 12)]
			
		# Create a bitmap with the number of colors in the selected palette
		self.bitmap = displayio.Bitmap(device.display.width, device.display.height, len(self.p))
		tile_grid = displayio.TileGrid(self.bitmap, pixel_shader=self.p)
		bitmaptools.fill_region(dest_bitmap=self.bitmap, x1=0, y1=0, x2=device.display.width, y2=device.display.height, value=self.styles[self.selectedStyle]['bgindex'])

		device.effect_group.append(tile_grid)

		self.cardgroup = displayio.Group()
		device.effect_group.append(self.cardgroup)

		self.cards = []

		self.menu = [
			{
				'label': 'Style',
				'set': self.setStyle,
				'get': self.getStyle
			}
		]
		self.lastFrame = 0
		self.lastCardDrop = 0

	def setStyle(self, direction:int):
		self.selectedStyle = self.device.cycleOption(list(self.styles), self.selectedStyle, direction)
		self.__init__(device=self.device, style=self.selectedStyle)

	def getStyle(self):
		return self.selectedStyle

	def buildCard(self):
		newcard = {}
		newcard['gravity'] = self.styles[self.selectedStyle]['gravity']()
		self.lastcolor = self.device.cycleOption(self.cardcolors, self.lastcolor, 1)
		newcard['color'] = self.lastcolor
		self.lastcardlabel = self.device.cycleOption(self.cardlabels, self.lastcardlabel, 1)
		newcard['label'] = self.lastcardlabel
		newcard['poly'] = displayio.Group()
		newcard['sizex'] = self.styles[self.selectedStyle]['sizex']()
		if self.styles[self.selectedStyle]['shape'] == 'rect':
			newcard['sizey'] = self.styles[self.selectedStyle]['sizey']()
		else:
			newcard['sizey'] = newcard['sizex']
		if self.styles[self.selectedStyle]['shape'] == 'circle':
			border = vectorio.Circle(pixel_shader=self.p, color_index=newcard['color'], radius=newcard['sizex'], x=0, y=0)
		else:
			border = vectorio.Rectangle(pixel_shader=self.p, color_index=newcard['color'], width=newcard['sizex'], height=newcard['sizey'], x=0, y=0)
		newcard['poly'].append(border)

		if self.styles[self.selectedStyle]['border']:
			if self.styles[self.selectedStyle]['shape'] != 'circle':
				bg = vectorio.Rectangle(pixel_shader=self.p, color_index=1, width=newcard['sizex']-2, height=newcard['sizey']-2, x=1, y=1)
				newcard['poly'].append(bg)

		if self.displaylabels:
			label = adafruit_display_text.label.Label(
				self.device.font, color=self.p[newcard['color']], text=newcard['label'], line_spacing=1,
				anchor_point=[.5,0], anchored_position=[4,2])
			newcard['poly'].append(label)
		newcard['poly'].x = random.randint(round(self.device.display.width/2) + newcard['sizey'], self.device.display.width)
		newcard['poly'].y = -newcard['sizey'] - random.randint(0, 5)
		newcard['dx'] = self.styles[self.selectedStyle]['dx']()
		newcard['realx'] = newcard['poly'].x
		newcard['dy'] = 1 + (random.random() * 3)
		self.cardgroup.append(newcard['poly'])

		self.device.gc(1)
		return newcard
	
	def moveCard(self, card):
		if  self.styles[self.selectedStyle]['trail']:
			bitmaptools.fill_region(dest_bitmap=self.bitmap, x1=card['poly'].x, y1=card['poly'].y, x2=card['poly'].x+card['sizex'], y2=card['poly'].y+card['sizey'], value=card['color'])
			if self.styles[self.selectedStyle]['border']:
				bitmaptools.fill_region(dest_bitmap=self.bitmap, x1=card['poly'].x+1, y1=card['poly'].y+1, x2=card['poly'].x+card['sizex']-1, y2=card['poly'].y+card['sizey']-1, value=1)

		card['realx'] = card['realx'] + card['dx']
		card['poly'].x = round(card['realx'])

		if card['poly'].y + card['dy'] >= self.device.display.height - card['sizey']:
			# force a frame with the card at the bottom of the screen at the moment of the bounce
			card['poly'].y = self.device.display.height - card['sizey']
			card['dy'] = -card['dy'] * .75 # lower the bounce height (closer to 1 = lighter)
		else:
			card['dy'] += card['gravity']
			card['poly'].y = round(card['poly'].y + card['dy'])

	def removeCard(self, i:int=0):
		self.cardgroup.pop(i)
		self.cards.pop(i)

	def play(self):
		if (self.device.limitStep(self.styles[self.selectedStyle]['cardinterval'](), self.lastCardDrop)):
			self.cards.append(self.buildCard())
			self.lastCardDrop = time.monotonic()

		if (self.device.limitStep(.03, self.lastFrame)):
			c = 0
			while c < len(self.cards):
				self.moveCard(self.cards[c])
				if self.cards[c]['poly'].x > self.device.display.width or self.cards[c]['poly'].x < -self.cards[c]['sizex']-1:
					self.removeCard(c)
				c = c + 1			
			self.lastFrame = time.monotonic()

		if self.device.menu_group.hidden and sum(locals()['keys']):
			if locals()['keys'][3]:
				if (self.device.limitStep(self.device.buttonPause, self.device.lastButtonTick)):
					self.device.lastButtonTick = time.monotonic()
					self.__init__(device=self.device, style=self.selectedStyle)
					