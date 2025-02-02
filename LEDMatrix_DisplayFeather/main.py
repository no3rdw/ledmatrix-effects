import supervisor
supervisor.runtime.autoreload = False

from device import Device
device = Device()


# working: 'Paint','Bounce','Midiviz, 'Grow','Worms','Sky','Static','ITYSL'
effects = ['Weather','Static','Paint','Bounce','Grow','Worms','Sky','ITYSL']
for e in effects:
	locals()[e] = __import__(str.lower(e)).Effect
	device.gc()

menu = __import__('menu').Effect(device)
clock = __import__('clock').Effect(device)
device.changeEffect(device.settings['startupEffect'])
menu.setDisplayClock(0)


while True:

	#if (device.limitStep(.1, device.lastRead)):
	device.receiveOverSerial()

	#if hasattr(device.neokey, "pixels"):
	#	keys = device.neokey.get_keys() # using this is MUCH faster than referencing device.neokey[x] over and over 
	
	#if device.menu_group.hidden and keys[0] and device.limitStep(device.buttonPause, device.lastButtonTick): # only enter this loop if menu button is down
	#	device.setLastButtonTick()
	#	menu.showMenu()

	if not device.menu_group.hidden: # only play the menu loop if menu is open
		menu.play()

	if not device.clock_group.hidden: # only play the clock loop if clock is displayed
		clock.play()

	device.effect.play()

	#if device.limitStep(device.buttonPause, device.lastButtonTick):
	#	if hasattr(device.neokey, "pixels"):
	#		device.neokey.pixels.brightness = 0

	if device.overlay_group.hidden == False and device.limitStep(device.overlayDelay, device.lastOverlayUpdate):
		device.overlay_group.hidden = True

	if len(device.sendMessage):
		device.uart.write(device.sendMessage[0]) #send the first character of the message string
		device.sendMessage = device.sendMessage[1:] #remove the first character from the message string