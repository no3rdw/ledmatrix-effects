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

		# The Feather M4 cannot read IR signals and output to the RGBMatrix at the same time
		# Instead, we'll use a Circuit Playground Express (because I have one on hand)
		# to read the IR signals from a remote and pass them to the Feather via a serial connection.
		# If not using a serial connection, replace the following line with the line below.
		self.uart = busio.UART(board.TX, board.RX, baudrate=9600, timeout=0)
		self.uart.reset_input_buffer()
		# self.uart = None

		self.i2c = board.I2C()

		################### Hardware Config ##################

		# If no NeoKey module, replace the following line with the line below
		self.neokey = NeoKey1x4(self.i2c)
		#self.neokey = None

		# If no RTC module, replace the following line with the line below
		self.rtc = pcf8523.PCF8523(self.i2c)
		#self.rtc = None

		self.i2c.unlock()

		if hasattr(self.neokey, "pixels"):
			self.neokey.pixels.brightness = 1
		else:
			locals()['keys'] = [0,0,0,0]

		self.effect = None
		self.settings = self.loadData('settings.json')
		if not self.settings: # set defaults
			self.settings = {"brightness":0.8,"startupEffect":"Static","displayClock":False,"displaySeconds":False,"startupWifi":False}

		##### LED Matrix setup
		self.matrix = rgbmatrix.RGBMatrix(
			width=32, height=32, bit_depth=6,
			rgb_pins=[board.D6, board.D5, board.D9, board.D11, board.D10, board.D12],
			addr_pins=[board.D25, board.D24, board.A3, board.A2],
			clock_pin=board.D13, latch_pin=board.A0, output_enable_pin=board.A1)
			
		self.display = framebufferio.FramebufferDisplay(self.matrix, auto_refresh=True)
		self.display.root_group = displayio.Group()
		# FramebufferDisplay.brightness is non-functional with RGBMatrix 
		# so we will implement our own brightness setting by modifying the level of all the HSL values
		# and for imported .bmps, pass them through alphaPalette to modify all indexed colors

		#background
		self.effect_group = displayio.Group()
		self.display.root_group.append(self.effect_group)

		self.clock_group = displayio.Group()
		self.display.root_group.append(self.clock_group)

		self.menu_group = displayio.Group()
		self.display.root_group.append(self.menu_group)

		#foreground
		self.overlay_group = displayio.Group()
		self.display.root_group.append(self.overlay_group)

		self.font = bitmap_font.load_font("fonts/04B_03__6pt.bdf")
		self.font.load_glyphs('1234567890QWERTYUIOPLKJHGFDSAZXCVBNMmnbvcxzasdfghjklpoiuytrewq&:<>')

		self.overlayDelayDefault = .7
		self.overlayDelay = self.overlayDelayDefault

		self.lastOverlayUpdate = 0
		self.clockcolor = 0x000000
		self.message_read_started = False
		self.message_read = []
		self.messageToSend = []
		self.wifi = False

		self.lastButtonTick = 0
		self.buttonPause = .05
		self.longPress = .3
		self.keyDownTime = [0,0,0,0]
		self.keyLongPress = [0,0,0,0]
		self.keyColors = [(255,255,0),
						(255,0,255),
						(0,255,0),
						(255,0,0)]

		#if self.settings['startupWifi'] == 'True':
		#	self.sendShortMessage('C2WF')

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
		self.settings['brightness'] = self.cycleOption([.1,.2,.3,.4,.5,.6,.7,.8,.9,1], self.settings['brightness'], direction)
		self.reloadEffect()

	def changeEffect(self, e:str):
		if not hasattr(self.effect, 'name') or e != self.effect.name:
			try:
				self.effect = locals()[e](self)
			except: #on error, or specified effect is not in effect list, load first in list
				self.effect = locals()[locals()['effects'][0]](self)
			locals()['menu'].getEffectMenu()
			self.gc(1)

	def reloadEffect(self):
		self.effect = locals()[self.effect.name](self)
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
		
	#def setLastButtonTick(self):
	#	self.lastButtonTick = time.monotonic()

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
		x = colorsys.hls_to_rgb(h,b*l, s)
		y = (math.floor(x[0]*255), math.floor(x[1]*255), math.floor(x[2]*255))
		#print ("COLOR", h, l, s, b, y)
		return y

	
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
		
	def receiveOverSerial(self):		
		#try:
			byte_read = self.uart.read(1)
			if byte_read is not None:
				
				byte_read = byte_read.decode('utf-8')
				if byte_read == '^':
					self.message_read_started = True
				if self.message_read_started:
					self.message_read.append(byte_read)
				if byte_read == '~':
					self.message_read = "".join(self.message_read[1:-1]) # remove first (^) and last (~), then join all characters into a string
					print('Rcvd:', self.message_read)

					if len(self.message_read) == 8:
						self.processRemoteKeypress(self.message_read)
					else:
						if self.message_read == 'WAIT':
							locals()['menu'].showOverlay('Wait...', 10)
						elif self.message_read == 'C2WF':
							self.wifi = False
							locals()['menu'].showOverlay('WifiWait', 30)
						elif self.message_read == 'WIFI':
							self.wifi = True
							locals()['menu'].showOverlay('Wifi!')
						elif self.message_read == 'NOWI':
							self.wifi = False
							locals()['menu'].showOverlay('No Wifi')
						elif self.message_read == 'ERRR':
							locals()['menu'].showOverlay('Error')
						else:
							self.overlayDelay = self.overlayDelayDefault
						
						if "handleMessage" in dir(self.effect):
							self.effect.handleMessage(self.message_read)


					self.message_read = []
					self.message_read_started = False
					self.uart.reset_input_buffer()

		#except:
		#	pass

	def processKey(self, n, keyDown, shortCode, longCode):
		if keyDown:
			self.neokey.pixels[n] = self.keyColors[n]
			if self.keyDownTime[n] == 0:
				self.keyDownTime[n] = time.monotonic()
			elif time.monotonic() - self.keyDownTime[n] > self.longPress and not self.keyLongPress[n]:
				self.keyLongPress[n] = 1
				print('key', n, 'longpress')
				self.processRemoteKeypress(longCode)
		elif self.keyDownTime[n]:
			if not self.keyLongPress[n]:
				print('key', n, 'shortpress')
				self.processRemoteKeypress(shortCode)
			self.neokey.pixels[n] = (0,0,0)
			self.keyDownTime[n] = 0
			self.keyLongPress[n] = 0
		
	def processRemoteKeypress(self, code:str):
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
				("00FD58A7", "9"),
				("00000003", "Effect"),
				("00000002", "Clock"),
				("00000001", "Settings"),
				("00000000", "Clear"))
		# the last four values are the 'longPress' versions of the four keys
		
		foundAt = [index for index, value in enumerate(table) if value[0] == code]
		if len(foundAt):
			key = table[foundAt[0]][1]
			if not self.menu_group.hidden:
				locals()['menu'].handleRemote(key)
			else:
				if key == 'Effect' or key == 'Clock' or key  == 'Settings':
					locals()['menu'].showMenu(key)
				elif key == 'PlayPause':
					self.cycleEffect(1)
				else:
					self.effect.handleRemote(key)

	def loadData(self, filename:str):
		try:
			self.writeMode = not storage.getmount("/").readonly
			f = open(filename,'r')
			var = json.loads(f.read())
			f.close()
		except:
			var = {}
		return var

	def writeData(self, var, filename:str):
		if self.writeMode == True:
			f = open(filename,'w') # 'w' is truncate write
			f.write(json.dumps(var))
			f.close()
		else:
			print(filename)
			print(json.dumps(var))

	def copyData(self, srcfilename:str, destfilename:str):
	
		src = open(srcfilename, 'r')
		dest = open(destfilename, 'x')
		dest.write(src.read())
		dest.close()
		src.close()

	def str2bool(self, v):
		return v.lower() in ("yes", "true", "t", "1")
	
	def prepMessage(self, m):
			return '^'+m+'~'
	
	def sendMessage(self, m):
		self.messageToSend = self.prepMessage(m)
		print("Sent:", self.messageToSend)
		return self.messageToSend

	def sendShortMessage(self, m):
		m = self.prepMessage(m)
		self.uart.write(m)
		print("Sent:", m)
		return m

	def sendMessageChar(self):
		
		self.uart.write(self.messageToSend[0]) #send the first character of the message string
		self.messageToSend = self.messageToSend[1:] #remove the first character from the message string