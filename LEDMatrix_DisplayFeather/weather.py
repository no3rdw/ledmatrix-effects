import time, json, displayio
from effect import Effect
import adafruit_display_text.label
from adafruit_bitmap_font import bitmap_font


class Effect(Effect):
	def __init__(self, device:Device):
		self.name = 'Weather'
		super().__init__(device, self.name)
		
		self.device = locals()['device']

		self.device.clockcolor = 0xFF0000
		device.clearDisplayGroup(device.effect_group)
		self.lastWeatherGet = 0
		self.lastWeatherTry = 0
		self.lastPageTurn = 0
		self.currentPage = 0
		self.currentDay = 0

		self.p = displayio.Palette(4)
		self.p[0] = device.hls(0, 1, 0) # white
		self.p[1] = device.hls(.5, .5, .8)  # light blue
		self.p[2] = device.hls(.01, .5, .8) # red
		self.p[3] = device.hls(.65, .2, 1)  # dk blue

		self.datelabel = adafruit_display_text.label.Label(
			device.font, color=self.p[0], background_color=None, text='Waiting', line_spacing=1,
			label_direction='LTR',anchor_point=[.5,0],anchored_position=[self.device.display.width/2,0], base_alignment=True, background_tight=True)

		self.label1 = adafruit_display_text.label.Label(
			device.font, color=self.p[0], background_color=None, text='For Wifi', line_spacing=1,
			label_direction='LTR',anchor_point=[.5,1],anchored_position=[self.device.display.width/2,self.device.display.height-6], base_alignment=True, background_tight=True)

		self.label2 = adafruit_display_text.label.Label(
			device.font, color=self.p[0], background_color=None, text='', line_spacing=1,
			label_direction='LTR',anchor_point=[.5,1],anchored_position=[self.device.display.width/2,self.device.display.height-1], base_alignment=True, background_tight=True)

		self.icons = bitmap_font.load_font("fonts/weather.bdf")
		self.icons.load_glyphs('ABCDEFGHI')

		self.iconlabel = adafruit_display_text.label.Label(
			self.icons, color=self.p[0], background_color=None, text='', line_spacing=1,
			label_direction='LTR',anchor_point=[.5,0],anchored_position=[self.device.display.width/2-1,6], base_alignment=True, background_tight=True)

		device.effect_group.append(self.iconlabel)
		device.effect_group.append(self.label1)
		device.effect_group.append(self.label2)
		device.effect_group.append(self.datelabel)

		self.days = []
		self.data = '{"time": ["2025-02-07", "2025-02-08", "2025-02-09"], "precipitation_probability_max": [7, 84, 97], "temperature_2m_max": [35.2, 32.5, 31.4], "weather_code": [71, 73, 75], "temperature_2m_min": [20.8, 18.0, 10.4], "current_code": 3, "current_temp": 23.7}'
		self.retryState = False

		self.menu = [
			{
				'label': 'Refresh',
				'set': self.requestWeather,
				'get': lambda: '<Press>'
			}
		]

		if self.device.wifi == True:
			self.resetPage() # reset message when switching effects and already on wifi
	
	def play(self):
		if self.device.wifi == True:
			if self.device.limitStep(self.lastWeatherGet, 300): # refresh every 30 minutes
				if self.device.limitStep(self.lastWeatherTry, 5): #try every X seconds
					self.requestWeather(0,False) # used when live
					#self.handleMessage(self.data) # used when testing
					self.lastWeatherTry = time.monotonic()

			if self.device.limitStep(self.lastPageTurn, 3):
				self.currentPage = self.device.cycleOption([0,1,2,3], self.currentPage, 1)
				self.showPage()

	def resetPage(self):
		self.label1.text = 'Getting'
		self.label2.text = 'Weathr'
		self.iconlabel.text = ''
		self.datelabel.text = ''
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
					self.label1.color = self.p[3]
					self.label2.color = self.p[3]
					self.label2.text = str(self.days[self.currentDay]['precip']) + '%'
				elif self.currentPage == 2:
					self.label1.text = 'Lo Temp'
					self.label1.color = self.p[1]
					self.label2.color = self.p[1]
					self.label2.text = str(round(self.days[self.currentDay]['lo'])) + 'F'
				else:
					self.label1.text = 'Hi Temp'
					self.label1.color = self.p[2]
					self.label2.color = self.p[2]
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
			elif c == 71 or c == 73:
				icon = "H"
			elif c == 75:
				icon = "HH"
			elif c == 95 or c == 96 or c == 99:
				icon = "GF"
			else:
				icon = ""

			self.iconlabel.text = icon

		else:
			pass


	def handleMessage(self, message:str):
		try:
			# ^{
			# 	"time": ["2025-02-07", "2025-02-08", "2025-02-09"], 
			# 	"temperature_2m_min": [19.5, 17.9, 10.4],
			#	"precipitation_probability_max": [7, 84, 97],
			#	"temperature_2m_max": [35.2, 32.5, 31.4], 
			#	"weather_code": [71, 73, 75]
			# }~
			struct = json.loads(message)
			self.days = []
			if 'weather_code' in struct.keys():
				i = 0
				while i < len(struct['weather_code']):
					x = {}
					x['date'] = struct['time'][i][5:7] + '/' + struct['time'][i][8:10]
					x['lo'] = struct['temperature_2m_min'][i]
					x['hi'] = struct['temperature_2m_max'][i]
					x['precip'] = struct['precipitation_probability_max'][i]
					x['code'] = struct['weather_code'][i]
					if i == 0:
						x['current_code'] = struct['current_code']
						x['current_temp'] = struct['current_temp']	
					self.days.append(x)
					i = i + 1
				self.lastWeatherGet = time.monotonic()

				self.currentDay = 0
				self.currentPage = 0
				self.showPage()
			else:
				print('WRONG JSON')
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
		self.device.sendShortMessage('WTHR')
	
	def handleRemote(self, key:str):
		if key == 'Enter':
			if (self.retryState == True):
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
			self.requestWeather(0,True)