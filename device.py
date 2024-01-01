import neopixel, board, time
from micropython import const
from digitalio import DigitalInOut, Pull
from adafruit_neokey.neokey1x4 import NeoKey1x4

class Device:
	def __init__(self):
		self.effect = None
		###### NeoPixel Strip Setup
		self.pixelcount = const(60)
		self.pixelpin = board.D6 # IDE PIN NUMBERS FOUND HERE https://learn.adafruit.com/assets/47156
		# board.D8 is onboard neopixels, board.D6 is strip connected to A1 hole
		self.pixels = neopixel.NeoPixel(pin=self.pixelpin, n=self.pixelcount, bpp=4, brightness=.5, auto_write=True)
		self.pixels.fill(0)
		self.keypixelStatus = [False, False, False, False]

		##### NeoKey Setup
		i2c_bus = board.I2C()
		# Create a NeoKey object
		self.neokey = NeoKey1x4(i2c_bus, addr=0x30) # address found with I2C Scanner py script
		self.neokey.pixels.brightness = .2 # KEYS, not strip

	"""
		##### Onboard Button Setup 
		#self.buttona = self.init_button(board.D4)
		#self.buttonb = self.init_button(board.D5)
		#self.buttonstates = [self.buttona.value, self.buttonb.value]

	def init_button(self, pin):
		button = DigitalInOut(pin)
		button.switch_to_input()
		button.pull = Pull.DOWN
		return button
	"""

	def init_pixelStatus(self):
		self.pixelStatus = []
		for x in range(0,self.pixelcount):
			self.pixelStatus.append(False)
	
	def changeEffect(self, e:str):
		if not hasattr(self.effect, 'type') or e != self.effect.type:
			self.pixels.fill(0)
			self.effect = locals()[e](self)
	
	def resetKeypixel(self, n:int):
		if self.keypixelStatus[n] == True:
			self.neokey.pixels[n] = 0x0
			self.keypixelStatus[n] = False

	def limitStep(self, limit:float, pastTick:float):
		nowTick = time.monotonic()
		if (nowTick - pastTick >= limit):
			return True
		else:
			return False