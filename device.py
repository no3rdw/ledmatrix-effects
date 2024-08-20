import board, time, json, math
from adafruit_neokey.neokey1x4 import NeoKey1x4
import pcf8523
import rgbmatrix
import displayio
import framebufferio
import gc
import displayio
import colorsys
import storage
import busio
from adafruit_bitmap_font import bitmap_font


class Device:
	def __init__(self):
		displayio.release_displays()
		self.i2c = board.I2C()

		################### Hardware Config ##################

		# If no NeoKey module, replace the following line with the line below
		#self.neokey = NeoKey1x4(self.i2c)
		self.neokey = None

		# If no RTC module, replace the following line with the line below
		self.rtc = pcf8523.PCF8523(self.i2c)
		# self.rtc = None

		# The Feather M4 cannot read IR signals and output to the RGBMatrix at the same time
		# Instead, we'll use a Circuit Playground Express (because I have one on hand)
		# to read the IR signals from a remote and pass them to the Feather via a serial connection.
		# If not using a serial connection, replace the following line with the line below.
		self.uart = busio.UART(None, board.RX, baudrate=38400, timeout=.05)
		# self.uart = None

		if hasattr(self.neokey, "pixels"):
			self.neokey.pixels.brightness = 0
			self.neokey.pixels[0] = (255,0,0)
			self.neokey.pixels[1] = (255,0,0)
			self.neokey.pixels[2] = (255,0,0)
			self.neokey.pixels[3] = (255,0,0)
		else:
			locals()['keys'] = [0,0,0,0]

		self.effect = None
		self.settings = self.loadData('settings.json')

		##### LED Matrix setup
		self.matrix = rgbmatrix.RGBMatrix(
			width=32, height=32, bit_depth=6,
			rgb_pins=[board.D6, board.D5, board.D9, board.D11, board.D10, board.D12],
			addr_pins=[board.A5, board.A4, board.A3, board.A2],
			clock_pin=board.D13, latch_pin=board.D4, output_enable_pin=board.D1)
			
		self.display = framebufferio.FramebufferDisplay(self.matrix, auto_refresh=True)
		self.display.root_group = displayio.Group()
		# FramebufferDisplay.brightness is non-functional with RGBMatrix 
		# so we will implement our own brightness setting by modifying the level of all the HSL values
		# and for imported .bmps, pass them through alphaPalette to modify all indexed colors

		
		
		self.effect_group = displayio.Group()
		self.display.root_group.append(self.effect_group)
		self.menu_group = displayio.Group()
		self.display.root_group.append(self.menu_group)
		self.overlay_group = displayio.Group()
		self.display.root_group.append(self.overlay_group)

		self.font = bitmap_font.load_font("lib/fonts/04B_03__6pt.bdf")
		self.font.load_glyphs('1234567890QWERTYUIOPLKJHGFDSAZXCVBNMmnbvcxzasdfghjklpoiuytrewq&:<>')
		self.lastButtonTick = 0
		self.buttonPause = .20

		self.overlayDelay = .7
		self.lastOverlayUpdate = 0

		self.lastRead = 0

	def cycleOption(self, optionList, selectedOption, direction):
		currentIndex = optionList.index(selectedOption)
		newIndex = currentIndex + direction
		if newIndex > len(optionList)-1:
			newIndex = 0
		elif newIndex < 0:
			newIndex = len(optionList)-1
		return optionList[newIndex]
	
	def cycleEffect(self, direction:int):
		locals()['menu'].moveCaret(0, 0)
		self.changeEffect(self.cycleOption(locals()['effects'], self.effect.name, direction))

	def cycleBrightness(self, direction:int):
		self.settings['brightness'] = self.cycleOption([.2,.4,.6,.8,1], self.settings['brightness'], direction)

	def changeEffect(self, e:str):
		if not hasattr(self.effect, 'name') or e != self.effect.name:
			self.effect = locals()[e](self)
			locals()['menu'].getEffectMenu()
			self.gc(1)

	def getTime(self, seconds:bool=True):
		if hasattr(self.rtc, 'datetime'):
			t = self.rtc.datetime
			if t.tm_hour == 0 or t.tm_hour == 12:
				hour = 12
			else:
				hour = t.tm_hour % 12
			if seconds:
				return "%d:%02d:%02d" % (hour, t.tm_min, t.tm_sec)
			else:
				return "%d:%02d" % (hour, t.tm_min)
		else:
			return "00:00:00"

	def getEffectName(self):
		return self.effect.name

	def resetKeypixel(self, n:int):
		if hasattr(self.neokey, "pixels"):
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

	def hls(self, h:float, l:float, s:float, b:float=None):
		if not b:
			b = self.settings['brightness']
		if h == 0: h = .0001
		elif h > 1: h = 1
		if l == 0: l = .0001
		elif l > 1: l = 1
		if s == 0: s = .0001
		elif s > 1: s = 1
		return colorsys.hls_to_rgb(h,b*l, s)
	
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
	
	def alphaPalette(self, p:Palette, pr:bool=False, b:float=None):
		i=0
		while i < len(p):
			h,l,s = self.int_to_hls(p[i])
			p[i] = self.hls(h,l,s,b)
			i += 1
		return p

	# Easing functions courtesy https://easings.net/
	def easeOutSine(self, x:float):
		return math.sin((x * math.pi) / 2)
	
	def easeInOutSine(self, x:int):
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
		
	def receiveIROverSerial(self):		
		if hasattr(self.uart, "baudrate"):
			byte_read = self.uart.read(8)  # Read eight bytes over serial connection
			
			if byte_read:
				self.processRemoteKeypress(byte_read.decode('utf-8'))
				self.uart.reset_input_buffer()
			
		self.lastRead = time.monotonic()

	def processRemoteKeypress(self, code:str):
		if hasattr(self.neokey, "pixels"):
			self.neokey.pixels.brightness = .5
		table = (("00FD00FF", "VolDown"),
		   		("00FD807F", "PlayPause"),
				("00FD40BF", "VolUp"),
				("00FD20DF", "Setup"),
				("00FDA05F", "Up"),
				("00FD609F", "StopMode"),
				("00FD10EF", "Left"),
				("00FD906F", "Enter"),
				("00FD50AF", "Right"),
				("00FD30CF", "0"),
				("00FDB04F", "Down"),
				("00FD708F", "Back"),
				("00FD08F7", "1"),
				("00FD8877", "2"),
				("00FD48B7", "3"),
				("00FD28D7", "4"),
				("00FDA857", "5"),
				("00FD6897", "6"),
				("00FD18E7", "7"),
				("00FD9867", "8"),
				("00FD58A7", "9"))
		
		foundAt = [index for index, value in enumerate(table) if value[0] == code]
		if len(foundAt):
			key = table[foundAt[0]][1]
			if not self.menu_group.hidden:
				locals()['menu'].handleRemote(key)
			else:
				if key == 'Setup':
					locals()['menu'].showMenu()
				elif key == 'PlayPause':
					self.cycleEffect(1)
				else:
					self.effect.handleRemote(key)
			self.setLastButtonTick()

	def loadData(self, filename:str):
		try:
			self.writeMode = not storage.getmount("/").readonly
			f = open(filename,'r')
			var = json.loads(f.read())
			f.close()
		except:
			if(filename == 'settings.json'):
				# load defaults so device doesn't error if settings.json is not present
				var = json.loads('{"brightness":0.8,"startupEffect":"Static","displayClock":"False","clockPosition":"Bottom","clockColor":"Black"}')
			else:
				var = {}
		return var

	def writeData(self, var, filename:str):
		if self.writeMode == True:
			f = open(filename,'w') # 'w' is truncate write
			f.write(json.dumps(var))
			f.close()
		else:
			print(json.dumps(var))