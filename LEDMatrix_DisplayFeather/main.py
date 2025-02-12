import supervisor
supervisor.runtime.autoreload = False

from device import Device
device = Device()


# working: 'Paint','Bounce','Midiviz, 'Grow','Worms','Sky','Static','ITYSL'
effects = ['Grow','Weather','Static','Paint','Bounce','Worms','Sky','ITYSL']
for e in effects:
	locals()[e] = __import__(str.lower(e)).Effect
	device.gc()

menu = __import__('menu').Effect(device)
clock = __import__('clock').Effect(device)
device.changeEffect(device.settings['startupEffect'])
menu.setDisplayClock(0)

device.sendShortMessage('WIFI') # check to see if we already are connected on reboot


while True:

	device.receiveOverSerial()

	if not device.menu_group.hidden: # only play the menu loop if menu is open
		menu.play()

	if not device.clock_group.hidden: # only play the clock loop if clock is displayed
		clock.play()

	device.effect.play()

	if device.overlay_group.hidden == False and device.limitStep(device.overlayDelay, device.lastOverlayUpdate):
		device.overlay_group.hidden = True

	if len(device.messageToSend):
		device.sendMessageChar()