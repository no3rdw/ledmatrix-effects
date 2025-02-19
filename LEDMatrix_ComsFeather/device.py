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

		self.settings = {}
	
	def setupIR(self):
		# IR receiver setup needs to happen after connected to wifi
		self.ir_receiver = pulseio.PulseIn(board.A1, maxlen=1200, idle_state=True)
		#self.decoder = adafruit_irremote.NonblockingGenericDecode(self.ir_receiver) # unreliable
		self.decoder = adafruit_irremote.GenericDecode(self.ir_receiver)
		self.lastSentCode = ''

	def readPulses(self):
		pulses = self.decoder.read_pulses(input_pulses=self.ir_receiver, blocking=False, pulse_window=.04)
		if pulses is not None:
			try:
				code = self.decoder.decode_bits(pulses)
				hex_code = ''.join(["%02X" % x for x in code])
				self.sendCode(hex_code)
			except adafruit_irremote.IRNECRepeatException:  # unusual short code!
				#pass
				self.sendCode(self.lastSentCode)
			except adafruit_irremote.IRDecodeException as e:     # failed to decode
				pass
				#print("Failed to decode: ", e.args)

		# nonblocking decoder is unreliable!!
		# for remoteMessage in device.decoder.read():
		# 	if hasattr(remoteMessage, 'reason'):
		# 		print('IR Error: ' + remoteMessage.reason)
		# 	elif hasattr(remoteMessage, 'code'):
		# 		hex_code = ''.join(["%02X" % x for x in remoteMessage.code])
		# 		device.sendCode(hex_code)
		# 	else:
		# 		pass
		
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
		#try:
			byte_read = self.uart.read(1)
			if byte_read is not None:
				byte_read = byte_read.decode('utf-8')
				if byte_read == '^':
					self.message_started = True
				if self.message_started:
					self.message_read.append(byte_read)
				if byte_read == '~':
					self.message_read = "".join(self.message_read[1:-1]) # remove first (^) and last (~), then join all characters into a string
					print('Rcvd:', self.message_read)

					if len(self.message_read) > 4:

						try:
							self.settings = json.loads(self.message_read)
							if("req" in self.settings and self.settings['req'] == 'WTHR'):
								# we now pass in settings json with lat/lng to use in weather lookup
								self.getWeather()
						except Exception as e:	
							print('EXCEPTION', e)

					elif(self.message_read == 'WIFI'):
						if self.esp.is_connected:
							self.sendShortMessage('WIFI') 	
						else:
							self.sendShortMessage('NOWI')
					elif(self.message_read == 'C2WF'):
						self.wifiConnect()

					self.message_read = []
					self.message_started = False
					self.uart.reset_input_buffer()
		#except:
		#	pass

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
		if self.esp.is_connected:
			if("lat" in self.settings and "lng" in self.settings):
				JSON_URL = f"http://api.open-meteo.com/v1/forecast?latitude={self.settings['lat']}&longitude={self.settings['lng']}&current=temperature_2m,weather_code&hourly=temperature_2m&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max&temperature_unit=fahrenheit&wind_speed_unit=mph&precipitation_unit=inch&timezone=America%2FNew_York&forecast_days=5"

				with self.requests.get(JSON_URL) as response:
					myresp = response.json()
					#print(myresp)
					filtered = {}
					filtered['temp'] = myresp['hourly']['temperature_2m']
					filtered['code'] = myresp['daily']['weather_code']
					filtered['hi'] = myresp['daily']['temperature_2m_max']
					filtered['lo'] = myresp['daily']['temperature_2m_min']
					filtered['time'] = myresp['daily']['time']
					filtered['precip'] = myresp['daily']['precipitation_probability_max']
					filtered['current_temp'] = myresp['current']['temperature_2m']
					filtered['current_code'] = myresp['current']['weather_code']
					print("JSON Response: ", filtered)
					self.sendMessage(json.dumps(filtered))
			else:
				self.sendShortMessage('ERRR')
		else:
			self.sendShortMessage('NOWI')

# {'time': ['2025-02-13', '2025-02-14', '2025-02-15'], 'precip': [47, 3, 92], 'code': [71, 3, 73], 'temp': [25.0, 25.2, 25.5, 26.5, 28.2, 30.1, 30.3, 32.0, 32.3, 33.1, 34.0, 34.2, 34.7, 35.4, 37.9, 38.3, 37.8, 38.2, 36.3, 32.4, 30.1, 29.4, 28.7, 28.6, 28.4, 27.5, 26.8, 24.8, 22.4, 21.9, 20.2, 18.9, 20.2, 21.8, 23.0, 24.4, 25.9, 26.3, 26.1, 27.3, 26.5, 24.8, 22.5, 21.1, 20.7, 19.4, 18.3, 17.7, 17.7, 17.8, 17.2, 16.6, 15.2, 14.5, 14.1, 14.0, 16.5, 19.5, 21.8, 24.3, 26.4, 29.0, 30.8, 30.9, 30.4, 29.3, 28.2, 27.2, 24.1, 24.9, 25.7, 26.9], 'hi': [38.3, 28.4, 30.9], 'current_code': 0, 'lo': [25.0, 17.7, 14.0], 'current_temp': 29.0}