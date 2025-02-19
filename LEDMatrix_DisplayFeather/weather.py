import time, json, displayio
from effect import Effect
import adafruit_display_text.label
from adafruit_bitmap_font import bitmap_font


class Effect(Effect):
	def __init__(self, device:Device):
		self.name = 'Weather'
		super().__init__(device, self.name)
		
		self.device = locals()['device']
		if not self.settings: #set defaults 
			self.settings = {"lat":42.6526,"lng":-73.7562}

		self.device.clockcolor = 0xFF0000
		device.clearDisplayGroup(device.effect_group)
		self.lastWeatherGet = time.monotonic()
		self.lastPageTurn = 0
		self.currentPage = 0
		self.currentDay = 0

		self.p = displayio.Palette(2)
		self.p[0] = device.hls(0, 1, 0) # white
		self.p[1] = device.hls(0, 0, 0)  # black

		#nonlinear gradient from dark blue to red (values in p above), provided by chatGPT!
		self.g = displayio.Palette(50)
		self.g[0] =  (0, 8, 106)
		self.g[1] =  (0, 8, 105)
		self.g[2] =  (0, 9, 104)
		self.g[3] =  (0, 9, 103)
		self.g[4] =  (0, 10, 102)
		self.g[5] =  (0, 10, 101)
		self.g[6] =  (0, 10, 101)
		self.g[7] =  (2, 10, 101)
		self.g[8] =  (3, 10, 100)
		self.g[9] =  (5, 10, 100)
		self.g[10] = (8, 10, 99)
		self.g[11] = (11, 11, 98)
		self.g[12] = (14, 11, 97)
		self.g[13] = (18, 12, 95)
		self.g[14] = (22, 12, 94)
		self.g[15] = (27, 13, 92)
		self.g[16] = (32, 13, 91)
		self.g[17] = (37, 14, 89)
		self.g[18] = (43, 15, 87)
		self.g[19] = (48, 15, 85)
		self.g[20] = (55, 16, 83)
		self.g[21] = (61, 17, 81)
		self.g[22] = (68, 18, 79)
		self.g[23] = (74, 18, 76)
		self.g[24] = (81, 19, 74)
		self.g[25] = (89, 20, 72)
		self.g[26] = (96, 21, 69)
		self.g[27] = (103, 22, 67)
		self.g[28] = (110, 23, 64)
		self.g[29] = (118, 23, 62)
		self.g[30] = (125, 24, 59)
		self.g[31] = (132, 25, 57)
		self.g[32] = (139, 26, 54)
		self.g[33] = (147, 27, 52)
		self.g[34] = (154, 28, 50)
		self.g[35] = (160, 28, 47)
		self.g[36] = (167, 29, 45)
		self.g[37] = (173, 30, 43)
		self.g[38] = (180, 31, 41)
		self.g[39] = (185, 31, 39)
		self.g[40] = (191, 32, 37)
		self.g[41] = (196, 33, 35)
		self.g[42] = (201, 33, 34)
		self.g[43] = (206, 34, 32)
		self.g[44] = (210, 34, 31)
		self.g[45] = (214, 35, 29)
		self.g[46] = (217, 35, 28)
		self.g[47] = (220, 36, 27)
		self.g[48] = (223, 36, 26)
		self.g[49] = (225, 36, 26)

		self.bitmap = displayio.Bitmap(self.device.display.width, self.device.display.height, len(self.g))
		self.tile_grid = displayio.TileGrid(self.bitmap, pixel_shader=self.g)
		device.effect_group.append(self.tile_grid)

		self.datelabel = adafruit_display_text.label.Label(
			device.font, color=self.p[0], background_color=None, text='Connect', line_spacing=1,
			label_direction='LTR',anchor_point=[.5,0],anchored_position=[self.device.display.width/2+1,1], base_alignment=True, background_tight=True)

		self.label1 = adafruit_display_text.label.Label(
			device.font, color=self.p[0], background_color=None, text='to Wifi?', line_spacing=1,
			label_direction='LTR',anchor_point=[.5,1],anchored_position=[self.device.display.width/2+1,self.device.display.height-6], base_alignment=True, background_tight=True)

		self.label2 = adafruit_display_text.label.Label(
			device.font, color=self.p[0], background_color=None, text='Enter', line_spacing=1,
			label_direction='LTR',anchor_point=[.5,1],anchored_position=[self.device.display.width/2+1,self.device.display.height-1], base_alignment=True, background_tight=True)

		self.icons = bitmap_font.load_font("fonts/weather.bdf")
		self.icons.load_glyphs('ABCDEFGHI')

		self.iconlabel = adafruit_display_text.label.Label(
			self.icons, color=self.p[0], background_color=None, text='', line_spacing=1,
			label_direction='LTR',anchor_point=[.5,0],anchored_position=[self.device.display.width/2,7], base_alignment=True, background_tight=True)

		device.effect_group.append(self.iconlabel)
		device.effect_group.append(self.label1)
		device.effect_group.append(self.label2)
		device.effect_group.append(self.datelabel)

		self.days = []
		self.testdata = '{"current_temp":30.5,"current_code":2,"temp":[24.1,24.6,25.1,26.8,28.6,29.9,31.0,31.6,32.1,32.3,33.3,33.9,34.3,34.8,37.1,37.3,37.4,37.9,33.2,30.5,29.3,28.8,28.5,28.3,76.4,77.6,78.2,79.9,80.2,81.0,82.7,18.5,19.8,21.1,22.2,23.5,25.5,26.7,27.6,28.4,27.2,25.8,23.6,22.5,21.2,20.2,19.0,18.9,18.6,19.4,18.1,16.9,15.7,15.0,14.6,14.2,16.1,19.6,23.1,26.4,30.0,28.7,19.0,19.9,19.9,19.9,19.8,20.1,20.7,21.8,23.5,25.6,26.6,27.2,28.0,28.4,28.9,29.4,30.3,31.7,32.3,33.5,34.8,35.0,34.8,34.5,34.1,34.3,34.5,34.3,35.9,32.8,28.4,25.4,23.0,24.3,23.3,22.3,21.3,19.7,18.5,18.5,17.9,17.1,17.8,19.7,21.9,23.6,23.9,24.8,25.1,23.7,22.1,20.1,18.6,17.3,16.1,15.1,14.2,13.6],"precip":[9,6,14,17,22,28,43,48,37,32,27,49,45,30,11,3,8,17,6,1,0,0,0,0,1,1,2,1,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,1,1,1,2,2,2,0,0,15,15,15,15,15,15,85,85,85,85,85,85,92,92,92,92,92,92,94,94,94,94,94,94,99,99,99,99,99,99,96,96,96,96,96,96,53,53,53,53,53,53,7,7,7,7,7,7,4,4,4,4,4,4,5,5,5,5,5,5,4,4,4,4],"time":["2025-02-13","2025-02-14","2025-02-15","2025-02-16","2025-02-17"],"code":[73,71,73,75,85],"hi":[38.3,28.6,30.3,37.3,25.3],"lo":[25.0,18.2,14.0,22.2,14.2]}'
		self.retryState = False

		self.menu = [
			{
				'label': 'LAT',
				'set': self.setLat,
				'get': lambda: str(self.settings['lat'])
			},
			{
				'label': 'LNG',
				'set': self.setLng,
				'get': lambda: str(self.settings['lng'])
			},
			{
				'label': 'Refresh',
				'set': self.requestWeather,
				'get': lambda: '<Press>'
			},
		]

		self.testing = False

		if self.device.wifi == True or self.testing == True:
			self.resetPage() # reset message when switching effects and already on wifi
	

	def setLat(self, direction):
		pass

	def setLng(self, direction):
		pass

	def play(self):
		if self.device.wifi == True or self.testing == True:
			if self.device.limitStep(self.lastWeatherGet, 300): # refresh every 30 minutes
				self.requestWeather(0,False) # used when live

			if self.device.limitStep(self.lastPageTurn, 3):
				self.currentPage = self.device.cycleOption([0,1,2,3], self.currentPage, 1)
				self.showPage()

	def resetPage(self):
		if self.device.wifi == True:
			self.datelabel.text = ''
			self.label1.text = 'Getting'
			self.label2.text = 'Weathr'
		else:
			self.datelabel.text = 'Connect'
			self.label1.text = 'to Wifi?'
			self.label2.text = 'Enter'
		self.iconlabel.text = ''
		self.label1.color = self.p[0]
		self.label2.color = self.p[0]

	def showPage(self):
		self.lastPageTurn = time.monotonic()
		if len(self.days):
			if self.currentPage == 0 and self.currentDay == 0:
				self.datelabel.text = 'Current'
				self.label1.text = 'Temp'
				self.label1.color = self.p[0]
				self.label2.color = self.p[0]
				self.label2.text = str(self.days[self.currentDay]['current_temp']) + 'F'
				c = self.days[self.currentDay]['current_code']
			else:
				if (self.currentPage == 0 and self.currentDay != 0):
					self.currentPage =+ 1 #only 'today' has current temp, on other days advance past this page
				c = self.days[self.currentDay]['code']
				if self.currentDay == 0:
					self.datelabel.text = 'Today'
				elif self.currentDay == 1:
					self.datelabel.text = 'Tmrrw'
				else:
					self.datelabel.text = str(self.days[self.currentDay]['date'])

				if self.currentPage == 3:
					self.label1.text = 'Precip'
					#self.label1.color = self.p[3]
					#self.label2.color = self.p[3]
					self.label2.text = str(self.days[self.currentDay]['precip']) + '%'
				elif self.currentPage == 2:
					self.label1.text = 'Lo Temp'
					#self.label1.color = self.p[1]
					#self.label2.color = self.p[1]
					self.label2.text = str(round(self.days[self.currentDay]['lo'])) + 'F'
				else:
					self.label1.text = 'Hi Temp'
					#self.label1.color = self.p[2]
					#self.label2.color = self.p[2]
					self.label2.text = str(round(self.days[self.currentDay]['hi'])) + 'F'

			
			if c == 0:
				icon = 'A'
			elif c == 1:
				icon = 'B'
			elif c == 2:
				icon = 'C'
			elif c == 3:
				icon = 'D'
			elif c == 45 or c == 48:
				icon = "I"
			elif c == 51 or c == 53 or c == 61:
				icon = 'E'
			elif c == 55:
				icon = "EE"
			elif c == 56 or c == 57 or c == 66 or c == 67:
				icon = "EH"
			elif c == 63:
				icon = "F"
			elif c == 65:
				icon = "FF"
			elif c == 71 or c == 73 or c == 85:
				icon = "H"
			elif c == 75 or c == 85:
				icon = "HH"
			elif c == 95 or c == 96 or c == 99:
				icon = "GF"
			else:
				icon = ""

			self.iconlabel.text = icon
			self.drawBG(self.days[self.currentDay]['hours'])
			if self.days[0]['current_temp'] > 70:
				self.datelabel.color = 0x00000
				self.label1.color = 0x00000
				self.label2.color = 0x00000
				self.iconlabel.color = 0x00000
				
		else:
			pass

	def drawBG(self, hours):
		h = 0
		x = 0
		while h < 24:
			y = 0
			doubled = 0
			while y < self.device.display.height:
				g = round(hours[h][0]/2)
				if g > 49: g = 49
				if g < 0: g = 0
				self.bitmap[(x,y)] = g
				y = y + 1
				if doubled == 0 and y == self.device.display.height and h >= 9 and h <= 16:
					# double the width of hours 9am-4pm so 24 hours fills the 32px-wide screen
					x = x + 1; y = 0; doubled = 1
			x = x + 1
			h = h + 1

	def handleMessage(self, message:str):
		try:
			if(len(message) > 4):
				struct = json.loads(message)
				self.days = []
				if 'code' in struct.keys():
					i = 0
					while i < len(struct['code']):
						x = {}
						x['date'] = struct['time'][i][5:7] + '/' + struct['time'][i][8:10]
						x['lo'] = struct['lo'][i]
						x['hi'] = struct['hi'][i]
						x['precip'] = struct['precip'][i]
						x['code'] = struct['code'][i]
						x['hours'] = []
						h = 0
						while h < 24:
							x['hours'].append([struct['temp'].pop(0)])
							h = h + 1
						if i == 0:
							x['current_code'] = struct['current_code']
							x['current_temp'] = struct['current_temp']	
						self.days.append(x)
						i = i + 1
					self.lastWeatherGet = time.monotonic()

					self.currentDay = 0
					self.currentPage = 0
					self.showPage()
			elif message == 'WIFI':
				self.requestWeather(0,True)
			elif message == 'NOWI':
				self.resetPage()
			else:
				pass
		except Exception as e:
			locals()['menu'].showOverlay('Error', 1)
			print('EXCEPTION', e)
			self.label1.text = 'Enter'
			self.label2.text = 'RetrY'
			self.retryState = True
		pass

	def requestWeather(self, direction:int=0, closeMenu:bool=True):
		if closeMenu: # unless we're doing an autorefresh after a long time, clear days array and close menu
			self.resetPage()
			self.days = []
			locals()['menu'].hideMenu()
		if self.testing == True:
			self.handleMessage(self.testdata) 
		else: self.device.sendMessage(json.dumps(self.settings))
	
	def handleRemote(self, key:str):
		if key == 'Enter':
			if (not self.device.wifi):
				self.device.sendShortMessage('C2WF')
			elif(self.retryState == True):
				self.retryState = False
				self.requestWeather(0,True)
			else:
				self.currentPage = self.device.cycleOption([0,1,2,3], self.currentPage, 1)
				self.showPage()
		elif key == 'Right' or key == 'Down':
			self.currentDay = self.device.cycleOption([0,1,2,3,4], self.currentDay, 1)
			self.showPage()
		elif key == 'Left' or key == 'Up':
			self.currentDay = self.device.cycleOption([0,1,2,3,4], self.currentDay, -1)
			self.showPage()
		elif key == 'StopMode':
			if (not self.device.wifi):
				self.device.sendShortMessage('C2WF')
			else:
				self.retryState = False
				self.requestWeather(0,True)