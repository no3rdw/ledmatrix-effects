import gc
from device import Device
##### Can't enable all at once on the CPX because of memory
#from sparkle import Sparkle
#from clock import Clock
from worms import Worms
device = Device()

##### App variables
effects = ['Clock', 'Sparkle', 'Worms']
device.changeEffect('Worms') # set startup/default effect here

while True:
	gc.collect()
	print(str(gc.mem_free()))
	if device.neokey[0]:
		device.neokey.pixels[0] = (255, 200, 40)
		device.pixels.brightness = .1 if device.pixels.brightness - .01 < .1 else device.pixels.brightness - .1
		device.keypixelStatus[0] = True
	else:
		device.resetKeypixel(0)
	if device.neokey[1]:
		device.neokey.pixels[1] = (255, 200, 40)
		device.pixels.brightness = 1 if device.pixels.brightness + .1 > 1 else device.pixels.brightness + .1
		device.keypixelStatus[1] = True
	else:
		device.resetKeypixel(1)
	if device.neokey[2]:
		device.neokey.pixels[2] = (255, 200, 40)
		device.changeEffect('Clock')
		device.keypixelStatus[2] = True
	else:
		device.resetKeypixel(2)
	if device.neokey[3]:
		device.neokey.pixels[3] = (255, 200, 40)
		device.changeEffect('Worms')
		device.keypixelStatus[3] = True
	else:
		device.resetKeypixel(3)
	
	device.effect.play(device)