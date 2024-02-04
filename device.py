import board, time
from digitalio import DigitalInOut, Pull
from adafruit_neokey.neokey1x4 import NeoKey1x4
import pcf8523
import rgbmatrix
import displayio
import framebufferio
import gc

class Device:
	def __init__(self):
		displayio.release_displays()

		self.effect = None

		self.keypixelStatus = [False, False, False, False]

		##### NeoKey Setup
		self.i2c = board.I2C()
		# Create a NeoKey object
		self.neokey = NeoKey1x4(self.i2c) # address found with I2C Scanner py script
		self.neokey.pixels.brightness = .2 # neopixels on KEYS

		self.rtc = pcf8523.PCF8523(self.i2c)

		##### LED Matrix setup		
		self.matrix = rgbmatrix.RGBMatrix(
			width=32, height=32, bit_depth=6,
			rgb_pins=[board.D6, board.D5, board.D9, board.D11, board.D10, board.D12],
			addr_pins=[board.A5, board.A4, board.A3, board.A2],
			clock_pin=board.D13, latch_pin=board.D0, output_enable_pin=board.D1)
		
		self.display = framebufferio.FramebufferDisplay(self.matrix, auto_refresh=True)
		self.lastButtonTick = 0

	def init_button(self, pin):
		button = DigitalInOut(pin)
		button.switch_to_input()
		button.pull = Pull.DOWN
		return button
	
	def cycleEffect(self):
		currentIndex = locals()['effects'].index(self.effect.name)
		newIndex = currentIndex + 1
		if newIndex > len(locals()['effects'])-1:
			newIndex = 0
		self.changeEffectByIndex(newIndex)

	def changeEffect(self, e:str):
		gc.collect()
		if not hasattr(self.effect, 'name') or e != self.effect.name:
			self.effect = locals()[e](self)
			print(str(gc.mem_free()))

	def changeEffectByIndex(self, e:int):
		self.changeEffect(locals()['effects'][e])
	
	def resetKeypixel(self, n:int):
		if self.keypixelStatus[n] == True:
			self.neokey.pixels[n] = 0
			self.keypixelStatus[n] = False

	def limitStep(self, limit:float, pastTick:float):
		nowTick = time.monotonic()
		if (nowTick - pastTick >= limit):
			return True
		else:
			return False
		
	def setLastButtonTick(self):
		self.lastButtonTick = time.monotonic()