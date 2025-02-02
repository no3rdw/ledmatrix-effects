import time, json

from device import Device
device = Device()

if device.wifiConnect():
	pass
	#device.sendMessage = getWeather()

while True:
	device.receiveOverSerial()

	for remoteMessage in device.decoder.read():
		if hasattr(remoteMessage, 'reason'):
			pass
			#print('IR Error: ' + remoteMessage.reason)
		elif hasattr(remoteMessage, 'code'):
			hex_code = ''.join(["%02X" % x for x in remoteMessage.code])
			device.sendCode(hex_code)
		else:
			#print('IR Repeat')
			pass
	
	if device.limitStep(.1, device.buttonTick):
		keys = device.neokey.get_keys()
		if keys[0]:
			device.sendCode('00FD20DF')
		if keys[1]:
			device.sendCode('00FDA05F')
		if keys[2]:
			device.sendCode('00FDB04F')
		if keys[3]:
			device.sendCode('00FD906F')
		device.buttonTick = time.monotonic()
		
	#if device.limitStep(3, device.messageTick):
	#	device.sendMessage = prepMessage(generate_random_string(30))
	#	device.messageTick = time.monotonic()
	
	if len(device.sendMessage):
		device.buttonPause = True # don't interrupt messages with button codes
		device.uart.write(device.sendMessage[0]) #send the first character of the message string
		device.sendMessage = device.sendMessage[1:] #remove the first character from the message string
		device.neokey.pixels[0] = (0,255,0)
		device.neokey.pixels[1] = (0,255,0)
		device.neokey.pixels[2] = (0,255,0)
		device.neokey.pixels[3] = (0,255,0)
	else:
		device.buttonPause = False
		device.neokey.pixels[0] = (0,0,0)
		device.neokey.pixels[1] = (0,0,0)
		device.neokey.pixels[2] = (0,0,0)
		device.neokey.pixels[3] = (0,0,0)