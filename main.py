from device import Device
device = Device()
from menu import Menu
from static import Static
from itysl import ITYSL
from sky import Sky
from bounce import Bounce
from grow import Grow
effects = ['Grow','Bounce','Sky','ITYSL','Static']

if device.writeMode == True:
	from settings import Settings
	effects.append('Settings')

# https://learn.adafruit.com/circuitpython-display-support-using-displayio/library-overview

menu = Menu(device)
device.changeEffect(device.saveData['startupEffect'])

device.gc()

while True:
	if hasattr(device.neokey, "pixels"):
		keys = device.neokey.get_keys() # using this is MUCH faster than referencing device.neokey[x] over and over 
	
	if device.menu_group.hidden and keys[0] and device.limitStep(device.buttonPause, device.lastButtonTick): # only enter this loop if menu button is down
		device.setLastButtonTick()
		menu.showMenu()

	if not device.menu_group.hidden: # only play the menu loop if menu is open
		menu.play()

	device.effect.play()