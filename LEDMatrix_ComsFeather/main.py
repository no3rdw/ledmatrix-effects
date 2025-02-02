import time, json

from device import Device
device = Device()

device.wifiConnect()
device.setupIR()

while True:
	device.receiveOverSerial()
	
	
	for remoteMessage in device.decoder.read():
		if hasattr(remoteMessage, 'reason'):
			print('IR Error: ' + remoteMessage.reason)
		elif hasattr(remoteMessage, 'code'):
			hex_code = ''.join(["%02X" % x for x in remoteMessage.code])
			device.sendCode(hex_code)
		else:
			pass
	
	
	#if device.limitStep(.1, device.buttonTick):
	#	keys = device.neokey.get_keys()
	#	if keys[0]:
	#		device.sendCode('00FD20DF')
	#	if keys[1]:
	#		device.sendCode('00FDA05F')
	#	if keys[2]:
	#		device.sendCode('00FDB04F')
	#	if keys[3]:
	#		device.sendCode('00FD906F')
	#	device.buttonTick = time.monotonic()
		
	if len(device.messageToSend):
		device.sendMessageChar()
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