from adafruit_bitmap_font import bitmap_font
import adafruit_display_text.label
import displayio, time

class Clock:

	def fixHour(self, hour):
		if hour == 0 or hour == 12:
			return 12
		else:
			return hour % 12

	def __init__(self, device):
		self.name = 'Clock'

		# Associate the RGB matrix with a Display so that we can use displayio features		

		fontFile = "lib/fonts/04B_03__6pt.bdf"
		fontToUse = bitmap_font.load_font(fontFile)

		#longtext = adafruit_display_text.wrap_text_to_pixels("This is a test",32,fontToUse)
		#longtext = "\n".join(longtext)

		t = device.rtc.datetime
		startclock = "%d:%02d:%02d" % (self.fixHour(t.tm_hour), t.tm_min, t.tm_sec)

		self.line1 = adafruit_display_text.label.Label(
			fontToUse, color=0xffff00, text=startclock, line_spacing=1,label_direction='LTR',anchor_point=[.5,.5],anchored_position=[16,15])
		#self.line1.x = 0
		#self.line1.y = 15

		g = displayio.Group()
		g.append(self.line1)
		device.display.root_group = g
		self.lastScroll = 0

	def scroll(self, device):
		t = device.rtc.datetime
		self.line1.text="%d:%02d:%02d" % (self.fixHour(t.tm_hour), t.tm_min, t.tm_sec)

		#self.line1.x = self.line1.x - 1
		line_width = self.line1.bounding_box[2]
		if self.line1.x < -line_width:
			self.line1.x = device.display.width

	def play(self, device):

		if (device.limitStep(.2, self.lastScroll)):
			self.scroll(device)
			self.lastScroll = time.monotonic()
		
		if device.keypixelStatus[0]:
			if (device.limitStep(.15, device.lastButtonTick)):
				device.setLastButtonTick()
				self.addMinute(device)

		if device.keypixelStatus[1]:
			if (device.limitStep(.15, device.lastButtonTick)):
				device.setLastButtonTick()
				self.addHour(device)


	def addMinute(self, device):
		t = device.rtc.datetime
		newmin = 0 if t.tm_min == 59 else t.tm_min + 1
		newt = time.struct_time((2024, 1, 1, t.tm_hour, newmin, 0, 0, -1, -1))
		device.rtc.datetime = newt

	def addHour(self, device):
		t = device.rtc.datetime
		newhr = 0 if t.tm_hour == 23 else t.tm_hour + 1
		newt = time.struct_time((2024, 1, 1, newhr, t.tm_min, t.tm_sec, 0, -1, -1))
		device.rtc.datetime = newt