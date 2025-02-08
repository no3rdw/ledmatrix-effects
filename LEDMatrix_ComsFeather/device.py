import board, random
import pulseio
import adafruit_irremote
import busio, time, json
from adafruit_neokey.neokey1x4 import NeoKey1x4

from os import getenv
from digitalio import DigitalInOut
import adafruit_connection_manager
import adafruit_requests
from adafruit_esp32spi import adafruit_esp32spi
from secrets import secrets

class Device:
	def __init__(self):
	
		#related to sending messages
		self.buttonTick = 0
		self.buttonPause = False
		self.messageTick = 0
		self.messageToSend = []

		# related to receiving messages
		self.message_started = False
		self.message_read = []

		# serial setup
		self.uart = busio.UART(board.TX, board.RX, baudrate=9600, timeout=0)
		self.uart.reset_input_buffer()

		# neokey setup
		self.neokey = NeoKey1x4(board.I2C())
		self.neokey.pixels.brightness = 1
		self.neokey.pixels[0] = (0,0,0)
		self.neokey.pixels[1] = (0,0,0)
		self.neokey.pixels[2] = (0,0,0)
		self.neokey.pixels[3] = (0,0,0)

		esp32_cs = DigitalInOut(board.D10)
		esp32_ready = DigitalInOut(board.D9)
		esp32_reset = DigitalInOut(board.D6)
		spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
		self.esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)

		pool = adafruit_connection_manager.get_radio_socketpool(self.esp)
		ssl_context = adafruit_connection_manager.get_radio_ssl_context(self.esp)
		self.requests = adafruit_requests.Session(pool, ssl_context)
		#print("Firmware vers.", esp.firmware_version)
		#print("MAC addr:", ":".join("%02X" % byte for byte in esp.MAC_address))
	
	def setupIR(self):
		# IR receiver setup needs to happen after connected to wifi
		self.ir_receiver = pulseio.PulseIn(board.A1, maxlen=1200, idle_state=True)
		self.decoder = adafruit_irremote.NonblockingGenericDecode(self.ir_receiver)
		self.lastSentCode = ''

	def wifiConnect(self):
		try:
			self.sendShortMessage('C2WF')
			print("Connecting to Wifi")
			while not self.esp.is_connected:
				try:
					self.neokey.pixels[0] = (0,0,255)
					self.esp.connect_AP(secrets["ssid"], secrets["password"])
				except OSError as e:
					self.neokey.pixels[1] = (0,0,255)
					print("could not connect to Wifi, retrying: ", e)
					continue
			self.neokey.pixels[1] = (0,0,255)
			self.neokey.pixels[2] = (0,0,255)
			print("Connected to", self.esp.ap_info.ssid, "\tRSSI:", self.esp.ap_info.rssi)
			self.sendShortMessage('WIFI')
			print("My IP address is", self.esp.ipv4_address)
			return True
		except Exception as e:
			self.sendShortMessage('ERRR')
			print('EXCEPTION', e)
			return False

	def receiveOverSerial(self):		
		try:
			byte_read = self.uart.read(1)
			if byte_read is not None:
				byte_read = byte_read.decode('utf-8')
				if byte_read == '^':
					self.message_started = True
				if self.message_started:
					self.message_read.append(byte_read)
				if byte_read == '~':
					self.message_read = "".join(self.message_read[1:-1]) # remove first (^) and last (~), then join all characters into a string
					print(self.message_read)
					print('MESSAGE RECEIVED')

					if(self.message_read == 'WTHR'):
						self.sendMessage(self.getWeather())

					self.message_read = []
					self.message_started = False
					self.uart.reset_input_buffer()
		except:
			pass

	def limitStep(self, limit:float, pastTick:float):
		nowTick = time.monotonic()
		if (nowTick - pastTick >= limit):
			return True
		else:
			return False

	def sendCode(self, code):
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
			self.lastSentCode = code
			self.sendShortMessage(code)
			self.neokey.pixels[0] = (255,0,0)
			self.neokey.pixels[1] = (255,0,0)
			self.neokey.pixels[2] = (255,0,0)
			self.neokey.pixels[3] = (255,0,0)

	def prepMessage(self, m):
			return '^'+m+'~'
	
	def sendMessage(self, m):
		self.messageToSend = self.prepMessage(m)
		print("Sent:", self.messageToSend)
		return self.messageToSend

	def sendShortMessage(self, m):
		# NO BUTTON PAUSE
		#self.buttonPause = True # don't interrupt messages with button codes
		m = self.prepMessage(m)
		self.uart.write(m)
		print("Sent:", m)
		return m

	def sendMessageChar(self):
		self.buttonPause = True # don't interrupt messages with button codes
		self.uart.write(self.messageToSend[0]) #send the first character of the message string
		self.messageToSend = self.messageToSend[1:] #remove the first character from the message string

	def getWeather(self):
		#self.sendShortMessage('WAIT')
		JSON_URL = "http://api.open-meteo.com/v1/forecast?latitude=42.6576&longitude=-73.8018&current=temperature_2m,weather_code&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max&temperature_unit=fahrenheit&wind_speed_unit=mph&precipitation_unit=inch&timezone=America%2FNew_York&temporal_resolution=hourly_6&forecast_days=5&forecast_hours=24"
		with self.requests.get(JSON_URL) as response:
			myresp = response.json()
			filtered = myresp['daily']
			filtered['current_temp'] = myresp['current']['temperature_2m']
			filtered['current_code'] = myresp['current']['weather_code']
			print("JSON Response: ", filtered)
			return json.dumps(filtered)