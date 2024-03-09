import board, time, json
from digitalio import DigitalInOut, Pull
from adafruit_neokey.neokey1x4 import NeoKey1x4
import pcf8523
import rgbmatrix
import displayio
import framebufferio
import gc
import displayio
import colorsys
import storage
from adafruit_bitmap_font import bitmap_font

class Device:
	def __init__(self):
		displayio.release_displays()

		self.effect = None

		##### NeoKey Setup
		self.i2c = board.I2C()
		# Create a NeoKey object
		self.neokey = NeoKey1x4(self.i2c)
		self.neokey.pixels.brightness = 0

		self.rtc = pcf8523.PCF8523(self.i2c)

		self.writeMode = not storage.getmount("/").readonly
		f = open('data.json','r') #'a' is appending, 'w' is truncate write
		self.saveData = json.loads(f.read())
		self.brightness = float(self.saveData['brightness'])
		f.close()

		##### LED Matrix setup		
		self.matrix = rgbmatrix.RGBMatrix(
			width=32, height=32, bit_depth=6,
			rgb_pins=[board.D6, board.D5, board.D9, board.D11, board.D10, board.D12],
			addr_pins=[board.A5, board.A4, board.A3, board.A2],
			clock_pin=board.D13, latch_pin=board.D0, output_enable_pin=board.D1)
			
		self.display = framebufferio.FramebufferDisplay(self.matrix, auto_refresh=True)
		self.display.root_group = displayio.Group()
		# FramebufferDisplay.brightness is non-functional with RGBMatrix 
		# so we will implement our own brightness setting by modifying the level of all the HSL values
		# and for imported .bmps, pass them through alphaPalette to modify all indexed colors
		
		self.effect_group = displayio.Group()
		self.display.root_group.append(self.effect_group)
		self.menu_group = displayio.Group()
		self.display.root_group.append(self.menu_group)

		self.font = bitmap_font.load_font("lib/fonts/04B_03__6pt.bdf")
		self.font.load_glyphs('1234567890QWERTYUIOPLKJHGFDSAZXCVBNMmnbvcxzasdfghjklpoiuytrewq&:')
		self.lastButtonTick = 0
		self.buttonPause = .15
	
	def cycleOption(self, optionList, selectedOption, direction):
		currentIndex = optionList.index(selectedOption)
		newIndex = currentIndex + direction
		if newIndex > len(optionList)-1:
			newIndex = 0
		elif newIndex < 0:
			newIndex = len(optionList)-1
		return optionList[newIndex]
	
	def cycleEffect(self, direction:int):
		self.changeEffect(self.cycleOption(locals()['effects'], self.effect.name, direction))

	def cycleBrightness(self, direction:int):
		self.brightness = self.cycleOption([.2,.4,.6,.8,1], self.brightness, direction)
		if self.writeMode:
			f = open('data.txt','w') # 'w' is truncate write
			f.write(str(self.brightness))
			f.close()

	def changeEffect(self, e:str):
		if not hasattr(self.effect, 'name') or e != self.effect.name:
			self.effect = locals()[e](self)
			locals()['menu'].getEffectMenu()
			self.gc(1)

	def getTime(self, seconds:bool=True):
		t = self.rtc.datetime
		if t.tm_hour == 0 or t.tm_hour == 12:
			hour = 12
		else:
			hour = t.tm_hour % 12
		if seconds:
			return "%d:%02d:%02d" % (hour, t.tm_min, t.tm_sec)
		else:
			return "%d:%02d" % (hour, t.tm_min)

	def getEffectName(self):
		return self.effect.displayname

	def resetKeypixel(self, n:int):
		self.neokey.pixels[n] = 0

	def limitStep(self, limit:float, pastTick:float):
		nowTick = time.monotonic()
		if (nowTick - pastTick >= limit):
			return True
		else:
			return False
		
	def setLastButtonTick(self):
		self.lastButtonTick = time.monotonic()

	def clearDisplayGroup(self, group:displayio.Group):
		while len(group) > 0:
			group.pop(0)

	def gc(self, output:int=0):
		gc.collect()
		if output: print(str(gc.mem_free()))

	def hls(self, h:float, l:float, s:float):
		if h == 0: h = .0001
		elif h > 1: h = 1
		if l == 0: l = .0001
		elif l > 1: l = 1
		if s == 0: s = .0001
		elif s > 1: s = 1
		return colorsys.hls_to_rgb(h,self.brightness*l, s)
	
	def int_to_hls(self, color:int):
		# from https://gist.github.com/mathebox/e0805f72e7db3269ec22
		r = (color >> 16) & 0xFF
		g = (color >> 8) & 0xFF
		b = color & 0xFF
		high = max(r, g, b)
		low = min(r, g, b)
		h, s, l = ((high + low) / 2,)*3
		if high == low:
			h = 0.0
			s = 0.0
		else:
			d = high - low
			s = d / (2 - high - low) if l > 0.5 else d / (high + low)
			h = {
				r: (g - b) / d + (6 if g < b else 0),
				g: (b - r) / d + 2,
				b: (r - g) / d + 4,
			}[high]
			h /= 6
		l = l / 255
		s = abs(s)
		return h, l, s
	
	def alphaPalette(self, p:Palette, pr:bool=False):
		i=0
		while i < len(p):
			h,l,s = self.int_to_hls(p[i])
			p[i] = self.hls(h,l,s)
			i += 1
		return p

	# https://easings.net/
	'''def easeInOutSine(self, x:int):
		return -(math.cos(math.pi * x) - 1) / 2

	def easeInOutQuad(self, x:int):
		if x < .5:
			return 2 * x * x
		else:
			return 1 - math.pow(-2 * x + 2, 2) / 2
		
	def easeInOutQuart(self, x:int):
		if x < 0.5:
			return  8 * x * x * x * x 
		else:
			return 1 - math.pow(-2 * x + 2, 4) / 2
	'''
	#self.x = self.easeInOutQuart(self.i / self.maxchanged) * self.maxchanged
	