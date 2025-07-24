import supervisor, time
supervisor.runtime.autoreload = False

from device import Device
device = Device()

effects = ['Colorbars','Grow','Static','Bounce','Worms','Sky','ITYSL','Dotman']
for e in effects:
	locals()[e] = __import__(str.lower(e)).Effect
	device.gc()

menu = __import__('menu').Effect(device)
clock = __import__('clock').Effect(device)
device.changeEffect(device.settings['startupEffect'])
menu.setDisplayClock(0)

#device.sendShortMessage('WIFI') # check to see if we already are connected on reboot 

while True:

	#device.receiveOverSerial()
	
	#if hasattr(device.neokey, "pixels"):
	if device.limitStep(device.buttonPause, device.lastButtonTick):
		keys = device.neokey.get_keys() # using this is MUCH faster than referencing device.neokey[x] over and over 
		device.processKey(3, keys[3], '00FDA05F', '00000003')
		device.processKey(2, keys[2], '00FDB04F', '00000002')
		device.processKey(1, keys[1], '00FD10EF', '00000001')
		device.processKey(0, keys[0], '00FD50AF', '00000000')
		device.lastButtonTick = time.monotonic()

		if device.menu_group.hidden and device.settings['autoAdvanceSpeed'] != 0 and device.limitStep(device.settings['autoAdvanceSpeed'], device.autoAdvanceTick):
			device.cycleEffect(1)

	if not device.menu_group.hidden: # only play the menu loop if menu is open
		menu.play()

	if not device.clock_group.hidden: # only play the clock loop if clock is displayed
		clock.play()

	device.effect.play()

	if device.overlay_group.hidden == False and device.limitStep(device.overlayDelay, device.lastOverlayUpdate):
		device.overlay_group.hidden = True

	if len(device.messageToSend):
		device.sendMessageChar()