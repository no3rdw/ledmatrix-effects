import time, vectorio, displayio, random
import adafruit_display_text.label

class Cards:
	def __init__(self, device:Device):
		self.name = type(self).__name__
		self.displayname = 'Cards'
		self.device = locals()['device']

		device.clearDisplayGroup(device.effect_group)

		self.gravity = .4

		self.p = displayio.Palette(4)
		self.p[0] = device.hls(.35, .2, .8) # green bg
		self.p[1] = device.hls(1, 1, 0) # white
		self.p[2] = device.hls(0, .35, 1) # red
		self.p[3] = device.hls(1, .0, 0) # black
		self.cardcolors = [2, 3]
		self.lastcolor = self.cardcolors[0]

		self.cardlabels = ['A','2','3','4','5','6','7','8','9','10','J','Q','K']
		self.lastcardlabel = self.cardlabels[random.randint(0, 12)]
			
		# Create a bitmap with the number of colors in the selected palette
		self.bitmap = displayio.Bitmap(device.display.width, device.display.height, 4)
		tile_grid = displayio.TileGrid(self.bitmap, pixel_shader=self.p)
		device.effect_group.append(tile_grid)

		self.bgcards = displayio.Group()
		device.effect_group.append(self.bgcards)

		self.cardgroup = displayio.Group()
		device.effect_group.append(self.cardgroup)

		self.cards = []

		self.menu = [
			#{
			#	'label': 'Setting',
			#	'set': self.setFunction,
			#	'get': self.getFunction
			#}
		]
		self.lastFrame = 0
		self.lastCardDrop = 0

	def buildCard(self):
		newcard = {}
		self.lastcolor = self.device.cycleOption(self.cardcolors, self.lastcolor, 1)
		newcard['color'] = self.lastcolor
		self.lastcardlabel = self.device.cycleOption(self.cardlabels, self.lastcardlabel, 1)
		newcard['label'] = self.lastcardlabel
		newcard['poly'] = displayio.Group()
		border = vectorio.Rectangle(pixel_shader=self.p, color_index=newcard['color'], width=8, height=10, x=0, y=0)
		bg = vectorio.Rectangle(pixel_shader=self.p, color_index=1, width=6, height=8, x=1, y=1)
		label = adafruit_display_text.label.Label(
			self.device.font, color=self.p[newcard['color']], text=newcard['label'], line_spacing=1,
			anchor_point=[.5,0], anchored_position=[4,2])
		
		newcard['poly'].append(border)
		newcard['poly'].append(bg)
		newcard['poly'].append(label)
		newcard['poly'].x = random.randint(round(self.device.display.width/2)+8, self.device.display.width)
		newcard['dx'] = -.6
		newcard['dy'] = 1 + (random.random() * 3)
		newcard['done'] = False
		self.cardgroup.append(newcard['poly'])

		self.device.gc(1)
		return newcard
	
	def moveCard(self, card):
		self.bgcards.append(vectorio.Rectangle(pixel_shader=self.p, color_index=card['color'], width=8, height=10, x=card['poly'].x, y=card['poly'].y))
		self.bgcards.append(vectorio.Rectangle(pixel_shader=self.p, color_index=1, width=6, height=8, x=card['poly'].x+1, y=card['poly'].y+1))

		# bounce off left side
		#if card['done'] == False and (card['poly'].x + card['dx'] < 0):
		#	card['dx'] = -card['dx']
		card['poly'].x = round(card['poly'].x + card['dx'])

		if card['poly'].y + card['dy'] >= self.device.display.height - 10:
			# force a frame with the card at the bottom of the screen at the moment of the bounce
			card['poly'].y = self.device.display.height - 10
			card['dy'] = -card['dy'] * .75 # lower the bounce height (closer to 1 = lighter)
		else:
			if card['dy'] == 0 and card['poly'].y == self.device.display.height - 10:
				# stopped 
				card['done'] = True
			else:
				card['dy'] += self.gravity	
			card['poly'].y = round(card['poly'].y + card['dy'])
		

	def removeCard(self, i:int=0):
		self.cardgroup.pop(i)
		self.cards.pop(i)

	def play(self):

		while len(self.bgcards) > 200:
			self.bgcards.pop(0) # remove border
			self.bgcards.pop(0) # remove card bg

		if (self.device.limitStep(2, self.lastCardDrop)):
			self.cards.append(self.buildCard())
			self.lastCardDrop = time.monotonic()

		if (self.device.limitStep(.03, self.lastFrame)):
			c = 0
			while c < len(self.cards):
				self.moveCard(self.cards[c])
				if self.cards[c]['poly'].x > self.device.display.width or self.cards[c]['poly'].x < -10:
					self.removeCard(c)
				c = c + 1			
			self.lastFrame = time.monotonic()