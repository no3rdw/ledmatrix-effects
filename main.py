
from device import Device
device = Device()
from clock import Clock
from static import Static
from menu import Menu
from itysl import ITYSL
import random

##### App variables test 
effects = ['ITYSL','Static','Clock']

# https://learn.adafruit.com/circuitpython-display-support-using-displayio/library-overview

menu = Menu(device)
device.changeEffectByIndex(0)
#device.changeEffectByIndex(random.randrange(0,len(effects)))
device.gc()

while True:
	keys = device.neokey.get_keys() # using this is MUCH faster than referencing device.neokey[x] over and over 
	if device.menu_group.hidden and sum(keys): # only enter this loop if a button is down
		if keys[0]:
			device.neokey.pixels[0] = (255, 200, 40)
		else:
			device.resetKeypixel(0)
		if keys[1]:
			device.neokey.pixels[1] = (255, 200, 40)
		else:
			device.resetKeypixel(1)
		if keys[2]:
			device.neokey.pixels[2] = (255, 200, 40)
		else:
			device.resetKeypixel(2)
		if keys[3]:
			if (device.limitStep(.15, device.lastButtonTick)):
					device.setLastButtonTick()
					device.neokey.pixels[3] = (255, 200, 40)
					menu.showMenu()
		else:
			device.resetKeypixel(3)

	if not device.menu_group.hidden: # only play the menu loop if menu is open
		menu.play()

	device.effect.play()