
import board, random
import pulseio
import adafruit_irremote
import busio, time
from adafruit_neokey.neokey1x4 import NeoKey1x4

buttonTick = 0
buttonPause = False
messageTick = 0
lastCodeSent = ''
uartMessage = ''

# IR receiver setup 
ir_receiver = pulseio.PulseIn(board.A1, maxlen=120, idle_state=True)
decoder = adafruit_irremote.NonblockingGenericDecode(ir_receiver)
uart = busio.UART(board.TX, board.RX, baudrate=9600)

neokey = NeoKey1x4(board.I2C())
neokey.pixels.brightness = 1

def generate_random_string(length):
    characters = 'QWERTYUIOPASDFGHJKL:ZXCVBNM<>":{}!@#$%^&*()_+'
    return ''.join(random.choice(characters) for _ in range(length))


def limitStep(limit:float, pastTick:float):
	nowTick = time.monotonic()
	if (nowTick - pastTick >= limit):
		return True
	else:
		return False

def sendCode(code):
	if not buttonPause:
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
			lastCodeSent = prep(code)
			uart.write(lastCodeSent)
			neokey.pixels[0] = (255,0,0)
			neokey.pixels[1] = (255,0,0)
			neokey.pixels[2] = (255,0,0)
			neokey.pixels[3] = (255,0,0)
			decoder._unparsed_pulses.clear()
			decoder.pulses.clear()
			print("Sent:", lastCodeSent)	
	else:
		print('Buttons Paused')

def prep(m):
	return '^'+m+'~'

while True:

	for remoteMessage in decoder.read():
		if hasattr(remoteMessage, 'reason'):
			pass
			#print('IR Error: ' + remoteMessage.reason)
		elif hasattr(remoteMessage, 'code'):
			hex_code = ''.join(["%02X" % x for x in remoteMessage.code])
			sendCode(hex_code)
		else:
			#print('IR Repeat')
			pass
	
	if limitStep(.1, buttonTick):
		keys = neokey.get_keys()
		if keys[0]:
			sendCode('00FD20DF')
		if keys[1]:
			sendCode('00FDA05F')
		if keys[2]:
			sendCode('00FDB04F')
		if keys[3]:
			sendCode('00FD906F')
		buttonTick = time.monotonic()
		
	#if limitStep(3, messageTick):
	#	uartMessage = prep(generate_random_string(30))
	#	messageTick = time.monotonic()
	
	if len(uartMessage):
		buttonPause = True # don't interrupt messages with button codes
		uart.write(uartMessage[0]) #send the first character of the message string
		uartMessage = uartMessage[1:] #remove the first character from the message string
		neokey.pixels[0] = (0,255,0)
		neokey.pixels[1] = (0,255,0)
		neokey.pixels[2] = (0,255,0)
		neokey.pixels[3] = (0,255,0)
	else:
		buttonPause = False
		neokey.pixels[0] = (0,0,0)
		neokey.pixels[1] = (0,0,0)
		neokey.pixels[2] = (0,0,0)
		neokey.pixels[3] = (0,0,0)