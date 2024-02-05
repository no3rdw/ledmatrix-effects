import adafruit_display_text.label
import displayio, time

class Clock:

	def fixHour(self:int, hour:int):
		if hour == 0 or hour == 12:
			return 12
		else:
			return hour % 12

	def __init__(self, device:Device):
		self.name = 'Clock'

		self.clockline1 = adafruit_display_text.label.Label(
			device.font, color=0xffff00, text='', line_spacing=1,label_direction='LTR',anchor_point=[.5,.5],anchored_position=[16,15])

		device.clearDisplayGroup(device.effect_group)
		device.effect_group.append(self.clockline1)

		self.lastScroll = 0

		self.menu = ['Set Hr', 'Set Min']

	def setoption1(self, device):
		self.addHour(device)

	def setoption2(self, device):
		self.addMinute(device)

	def optionlabel1(self, device):
		t = device.rtc.datetime
		return '%d' % self.fixHour(t.tm_hour)

	def optionlabel2(self, device):
		t = device.rtc.datetime
		return '%02d' % t.tm_min
	
	def updateClock(self, device:Device):
		t = device.rtc.datetime
		self.clockline1.hidden = 0
		self.clockline1.text="%d:%02d:%02d" % (self.fixHour(t.tm_hour), t.tm_min, t.tm_sec)

		line_width = self.clockline1.bounding_box[2]
		if self.clockline1.x < -line_width:
			self.clockline1.x = device.display.width

	def play(self, device:Device):
		if (device.limitStep(.1, self.lastScroll)):
			if device.menu_group.hidden:
				self.updateClock(device)
				self.lastScroll = time.monotonic()
			else:
				self.clockline1.hidden = 1

	def addMinute(self, device:Device):
		t = device.rtc.datetime
		newmin = 0 if t.tm_min == 59 else t.tm_min + 1
		newt = time.struct_time((2024, 1, 1, t.tm_hour, newmin, 0, 0, -1, -1))
		device.rtc.datetime = newt

	def addHour(self, device:Device):
		t = device.rtc.datetime
		newhr = 0 if t.tm_hour == 23 else t.tm_hour + 1
		newt = time.struct_time((2024, 1, 1, newhr, t.tm_min, t.tm_sec, 0, -1, -1))
		device.rtc.datetime = newt