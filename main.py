import gc
from device import Device
device = Device()
from clock import Clock
from static import Static

##### App variables 
effects = ['Clock','Static']
device.changeEffectByIndex(1)
gc.collect()

# https://learn.adafruit.com/circuitpython-display-support-using-displayio/library-overview

while True:
	if device.neokey[0]:
		device.neokey.pixels[0] = (255, 200, 40)
		device.keypixelStatus[0] = True
	else:
		device.resetKeypixel(0)
	if device.neokey[1]:
		device.neokey.pixels[1] = (255, 200, 40)
		device.keypixelStatus[1] = True
	else:
		device.resetKeypixel(1)
	if device.neokey[2]:
		device.neokey.pixels[2] = (255, 200, 40)
		device.keypixelStatus[2] = True
	else:
		device.resetKeypixel(2)
	if device.neokey[3]:
		if (device.limitStep(.5, device.lastButtonTick)):
				device.setLastButtonTick()
				device.neokey.pixels[3] = (255, 200, 40)
				device.keypixelStatus[3] = True
				device.cycleEffect()
	else:
		device.resetKeypixel(3)

	device.effect.play(device)