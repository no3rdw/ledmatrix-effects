import gc
from device import Device
device = Device()
from matrixclock import MatrixClock

##### App variables
effects = ['MatrixTest']
device.changeEffect('MatrixTest')

while True:
	gc.collect()

	device.effect.play(device)

	# if device.neokey[0]:
	# 	device.neokey.pixels[0] = (255, 200, 40)
	# 	device.keypixelStatus[0] = True
	# else:
	# 	device.resetKeypixel(0)
	# if device.neokey[1]:
	# 	device.neokey.pixels[1] = (255, 200, 40)
	# 	device.keypixelStatus[1] = True
	# else:
	# 	device.resetKeypixel(1)
	# if device.neokey[2]:
	# 	device.neokey.pixels[2] = (255, 200, 40)
	# 	device.keypixelStatus[2] = True
	# else:
	# 	device.resetKeypixel(2)
	# if device.neokey[3]:
	# 	device.neokey.pixels[3] = (255, 200, 40)
	# 	device.keypixelStatus[3] = True
	# else:
	# 	device.resetKeypixel(3)