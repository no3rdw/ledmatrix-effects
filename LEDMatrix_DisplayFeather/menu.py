import adafruit_display_text.label
import time
from effect import Effect

class Effect(Effect):
	def __init__(self, device:Device):
		self.device = device
		
		self.name = "Settings"
		self.menu = {}
		self.menu['labels'] = [] # actual display objects, limited to 4 lines
		self.menu['options'] = [] # all possible options, 0 = effect switch, all others are appended from effect
		self.caret = 0
		self.offset = 0
		
		self.selectedMenu = None
		self.setColors()

		self.lastMenuRefresh = 0

		#longtext = adafruit_display_text.wrap_text_to_pixels("MENU TEST",device.matrix.width,device.font)
		#longtext = "\n".join(longtext) 

		self.menu['labels'].append(adafruit_display_text.label.Label(
			device.font, color=self.selectedcolor, background_color=0x000000, text='', line_spacing=1,
			label_direction='LTR',anchor_point=[0,0],anchored_position=[1,1], background_tight=True))
		
		self.menu['labels'].append(adafruit_display_text.label.Label(
			device.font, color=self.menucolor, background_color=0x000000, text='', line_spacing=1,
			label_direction='LTR',anchor_point=[0,0],anchored_position=[1,7], background_tight=True))
		
		self.menu['labels'].append(adafruit_display_text.label.Label(
			device.font, color=self.menucolor, background_color=0x000000, text='', line_spacing=1,
			label_direction='LTR',anchor_point=[0,0],anchored_position=[1,13], background_tight=True))
		
		self.menu['labels'].append(adafruit_display_text.label.Label(
			device.font, color=self.menucolor, background_color=0x000000, text='', line_spacing=1,
			label_direction='LTR',anchor_point=[0,0],anchored_position=[1,19], background_tight=True))

		self.optionlabel = adafruit_display_text.label.Label(
			device.font, color=self.optioncolor, background_color=0x000000, text='OPTION', line_spacing=1,
			label_direction='LTR',anchor_point=[0,1],anchored_position=[1,31], background_tight=True)

		device.clearDisplayGroup(device.menu_group)
		device.menu_group.append(self.menu['labels'][0])
		device.menu_group.append(self.menu['labels'][1])
		device.menu_group.append(self.menu['labels'][2])
		device.menu_group.append(self.menu['labels'][3])
		device.menu_group.append(self.optionlabel)
		# start hidden
		device.menu_group.hidden = 1

		self.overlay = adafruit_display_text.label.Label(
			device.font, color=self.menucolor, background_color=0x000000, text='Overlay', line_spacing=1,
			label_direction='LTR',anchor_point=[0,1],anchored_position=[1,31], background_tight=True)
		
		device.overlay_group.append(self.overlay)
		device.overlay_group.hidden = True
		
	def showMenu(self, menuType='Effect'):
		print(self.selectedMenu, menuType)
		if self.selectedMenu == menuType:
			self.hideMenu()
		else:
			self.selectedMenu = menuType
			self.moveCaret(0, 0)
			if menuType == 'Settings':
				self.getSettingsMenu()
			elif menuType == 'Clock':
				self.getClockMenu()
			else:
				self.getEffectMenu()
			self.device.menu_group.hidden = 0 # show menu

	def hideMenu(self):
		self.selectedMenu = None
		self.device.menu_group.hidden = 1

	def setColors(self):
		self.menucolor = self.device.hls(.18, .5, 1)
		if self.selectedMenu == 'Settings':
			self.selectedcolor = self.device.hls(.9, .3, 1)
		elif self.selectedMenu == 'Clock':
			self.selectedcolor = self.device.hls(.3, .2, 1)
		else: 
			self.selectedcolor = self.device.hls(.01, .2, 1)
		self.optioncolor = self.device.hls(.6, .4, 1)

	def refreshMenu(self):
		self.setColors()
		i=0
		# refresh all displayed options
		while i < 4:
			if i < len(self.menu['options']):
				self.menu['labels'][i].text = self.menu['options'][i+self.offset]['label']
			else:
				self.menu['labels'][i].text = ''
			self.menu['labels'][i].color = self.menucolor if self.caret != i+self.offset else self.selectedcolor
			i += 1
		# refresh the selected option label
		self.optionlabel.text = self.menu['options'][self.caret]['get']()
		self.optionlabel.color = self.optioncolor
		
	def changeOption(self, direction:int):
		self.menu['options'][self.caret]['set'](direction)

	def moveCaret(self, direction:int, n:int=None):
		if direction == 1:
			self.caret = self.caret + 1 if self.caret < len(self.menu['options'])-1 else 0
		elif direction == -1:
			self.caret = self.caret - 1 if self.caret > 0 else len(self.menu['options'])-1
		elif direction == 0 and n != None:
			self.caret = n
		self.offset = self.caret-3 if self.caret-3 > 0 else 0

	def getEffectMenu(self):
		#reset effect menu
		self.menu['options'] = [{'label':'Effect', 'set':self.device.cycleEffect, 'get':self.device.getEffectName}]
		if hasattr(self.device.effect, 'menu'):
			i=0
			# add the effect options to the menu
			while i<len(self.device.effect.menu):
				self.menu['options'].append(self.device.effect.menu[i])
				i += 1

	def play(self):	
		self.refreshMenu()

	def handleRemote(self, key:str):
		#if key == 'Setup':
			#self.hideMenu()
		#el
		if key == 'Up':
			self.moveCaret(-1)
		elif key == 'Down':
			self.moveCaret(1)
		elif key == 'Left':
			self.changeOption(-1)
		elif key == 'Right' or key == 'Enter':
			self.changeOption(1)
		elif key == 'Effect':
			self.showMenu('Effect')
		elif key == 'Clock':
			self.showMenu('Clock')
		elif key == 'Settings':
			self.showMenu('Settings')
		elif key == 'Clear':
			self.hideMenu()
		elif key == 'Setup':
			self.hideMenu()

	def showOverlay(self, message:str, length:float=.7):
		self.device.lastOverlayUpdate = time.monotonic()
		self.device.overlayDelay = length
		self.overlay.text = message
		self.device.overlay_group.hidden = False

	def saveSettings(self, direction:int=0):
		self.device.writeData(self.device.settings, 'settings.json')

#	--------------------- SETTINGS MENU FUNCTIONS ---------------------------
	def getSettingsMenu(self):
		#reset settings menu
		self.menu['options'] = [
			{
				'label': 'Settings',
				'set': lambda d: self.hideMenu(),
				'get': lambda: 'Menu'
			},
			{	'label': 'Bright',
				'set': self.setBrightness,
				'get': lambda: str(self.device.settings['brightness'])
			},
			{
				'label': 'Startup',
				'set': self.setStartupEffect,
				'get': lambda: self.device.settings['startupEffect']
			},
			{
				'label': 'WifiStart',
				'set': self.setStartupWifi,
				'get': lambda: str(self.device.settings['startupWifi'])
			},
			{
				'label': 'Save',
				'set': self.saveSettings,
				'get': lambda: '<Press>'
			}]
		
	def setStartupEffect(self, direction:int):
		try:
			self.device.settings['startupEffect'] = self.device.cycleOption(locals()['effects'], self.device.settings['startupEffect'], direction)
		except: #when specified effect is not in effect list, load first in list
			self.device.settings['startupEffect'] = locals()['effects'][0]

	def setStartupWifi(self, direction:int):
		self.device.settings['startupWifi'] = self.device.cycleOption(['False','True'], self.device.settings['startupWifi'], direction)

	def setBrightness(self, direction:int):
		self.device.cycleBrightness(direction)
		#self.__init__(self.device)
		locals()['menu'].refreshMenu()

# 	--------------------- CLOCK MENU FUNCTIONS ----------------------------

	def getClockMenu(self):
		#reset clock menu
		self.menu['options'] = [
			{
				'label': 'Clock',
				'set': lambda: self.hideMenu(),
				'get': lambda: 'Menu'
			},
			{
				'label': 'Display',
				'set': self.setDisplayClock,
				'get': lambda: str(self.device.settings['displayClock'])
			},
			{
				'label': 'Seconds',
				'set': self.setDisplaySeconds,
				'get': lambda: str(self.device.settings['displaySeconds'])
			},
			{
				'label': 'Set Hr',
				'set': self.setHour,
				'get': self.getHour
			},
			{
				'label': 'Set Min',
				'set': self.setMinute,
				'get': self.getMinute
			},
			{
				'label': 'Save',
				'set': self.saveSettings,
				'get': lambda: '<Press>'
			}]

	def setDisplayClock(self, direction:int):
		self.device.settings['displayClock'] = self.device.cycleOption(['False','True'], self.device.settings['displayClock'], direction)
		if self.device.settings['displayClock'] == 'True':
			self.device.clock_group.hidden = False
		else:
			self.device.clock_group.hidden = True

	def setDisplaySeconds(self, direction:int):
		self.device.settings['displaySeconds'] = self.device.cycleOption(['False','True'], self.device.settings['displaySeconds'], direction)

	def fixHour(self:int, hour:int):
		return 12 if hour == 0 or hour == 12 else hour % 12

	def getHour(self):
		if hasattr(self.device.rtc, 'datetime'):
			t = self.device.rtc.datetime
			return '%d' % self.fixHour(t.tm_hour)
		else:
			return '0'

	def getMinute(self):
		if hasattr(self.device.rtc, 'datetime'):
			t = self.device.rtc.datetime
			return '%02d' % t.tm_min
		else:
			return '0'
	
	def updateClock(self):
		if hasattr(self.device.rtc, 'datetime'):
			t = self.device.rtc.datetime
			self.clockline1.hidden = 0
			self.clockline1.text="%d:%02d:%02d" % (self.fixHour(t.tm_hour), t.tm_min, t.tm_sec)

			line_width = self.clockline1.bounding_box[2]
			if self.clockline1.x < -line_width:
				self.clockline1.x = self.device.display.width
		else:
			self.clockline1.hidden = 1

	def setMinute(self, direction:int):
		if hasattr(self.device.rtc, 'datetime'):
			t = self.device.rtc.datetime
			newmin = 0 if t.tm_min == 59 or (direction == -1 and t.tm_min == 0) else t.tm_min + (1*direction)
			newt = time.struct_time((2024, 1, 1, t.tm_hour, newmin, 0, 0, -1, -1))
			self.device.rtc.datetime = newt

	def setHour(self, direction:int):
		if hasattr(self.device.rtc, 'datetime'):
			t = self.device.rtc.datetime
			if direction == -1 and t.tm_hour == 0:
				newhr = 23
			elif t.tm_hour == 23 and direction == 1:
				newhr = 0
			else: newhr = t.tm_hour + (1*direction)
			newt = time.struct_time((2024, 1, 1, newhr, t.tm_min, t.tm_sec, 0, -1, -1))
			self.device.rtc.datetime = newt



	