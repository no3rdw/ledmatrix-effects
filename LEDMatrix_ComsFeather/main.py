
import board
import pulseio
import adafruit_irremote
import busio, time
from adafruit_neokey.neokey1x4 import NeoKey1x4

buttonTick = 0
lastCodeSent = ''

# IR receiver setup 
ir_receiver = pulseio.PulseIn(board.A0, maxlen=120, idle_state=True)
decoder = adafruit_irremote.NonblockingGenericDecode(ir_receiver)
uart = busio.UART(board.TX, board.RX, baudrate=38400)
neokey = NeoKey1x4(board.I2C())


def limitStep(limit:float, pastTick:float):
	nowTick = time.monotonic()
	if (nowTick - pastTick >= limit):
		return True
	else:
		return False

def sendCode(code):
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
		lastCodeSent = code
		uart.write(lastCodeSent)
		print("Sent:", lastCodeSent)	

while True:

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

		for message in decoder.read():
			try:
				# Attempt to decode the received pulses
				sendCode(''.join(["%02X" % x for x in message.code]))
			except AttributeError:  # message did not have 'code' attribute but does have reason, must be an error
				try:
					print("ERROR", message.reason)
					ir_receiver.clear()
					pass
				except AttributeError: # message did not have 'code' or 'reason', must be a repeat
					sendCode(lastCodeSent)
					pass

		buttonTick = time.monotonic()