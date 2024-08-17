import adafruit_display_text.label
import time, json, storage

class Settings:
	def __init__(self, device:Device):
		self.name = type(self).__name__
		self.displayname = 'Settings'
		self.device = locals()['device']

		self.clockline1 = adafruit_display_text.label.Label(
			device.font, color=device.hls(.18, .5, 1), text='', line_spacing=1,
			label_direction='LTR',anchor_point=[.5,.5],anchored_position=[16,15])
		
		device.clearDisplayGroup(device.effect_group)
		device.effect_group.append(self.clockline1)

		self.effectList = locals()['effects'][:] # makes a copy of the effects var to remove 'Settings', we don't want it as a startup option
		self.effectList.remove('Settings')

		self.lastScroll = 0

		self.menu = [
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
				'label': 'Save',
				'set': lamda: self.device.writeData(self.device.settings, 'settings.json'),
				'get': lambda: '<Press>'
			}
		]

	def setStartupEffect(self, direction:int):
		self.device.settings['startupEffect'] = self.device.cycleOption(self.effectList, self.device.settings['startupEffect'], direction)

	def setBrightness(self, direction:int):
		self.device.cycleBrightness(direction)
		self.__init__(self.device)
		locals()['menu'].setColors()
		locals()['menu'].refreshMenu()

	def fixHour(self:int, hour:int):
		if hour == 0 or hour == 12:
			return 12
		else:
			return hour % 12

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

	def play(self):
		if (self.device.limitStep(.1, self.lastScroll)):
			if self.device.menu_group.hidden:
				self.updateClock()
				self.lastScroll = time.monotonic()
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
			newhr = 0 if t.tm_hour == 23 or (direction == -1 and t.tm_hour == 0) else t.tm_hour + (1*direction)
			newt = time.struct_time((2024, 1, 1, newhr, t.tm_min, t.tm_sec, 0, -1, -1))
			self.device.rtc.datetime = newt

	def handleRemote(self, key:str):
		print(key)