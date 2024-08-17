import adafruit_display_text.label
import time

class Menu:

	def __init__(self, device:Device):
		self.name = 'Menu'
		self.device = device

		self.menu = {}
		self.menu['labels'] = [] # actual display objects, limited to 4 lines
		self.menu['options'] = [{'label':'Effect', 'set':device.cycleEffect, 'get':device.getEffectName}] # all possible options, 0 = effect switch, all others are appended from effect
		self.caret = 0
		self.offset = 0
		
		self.setColors()

		self.lastMenuRefresh = 0

		#longtext = adafruit_display_text.wrap_text_to_pixels("MENU TEST",device.matrix.width,device.font)
		#longtext = "\n".join(longtext) 

		self.menu['labels'].append(adafruit_display_text.label.Label(
			device.font, color=self.selectedcolor, background_color=0x000000, text='', line_spacing=1,
			label_direction='LTR',anchor_point=[0,0],anchored_position=[1,1], background_tight=True))
		
		self.menu['labels'].append(adafruit_display_text.label.Label(
			device.font, color=self.menucolor, background_color=0x000000, text='', line_spacing=1,
			label_direction='LTR',anchor_point=[0,0],anchored_position=[1,7], background_tight=True))
		
		self.menu['labels'].append(adafruit_display_text.label.Label(
			device.font, color=self.menucolor, background_color=0x000000, text='', line_spacing=1,
			label_direction='LTR',anchor_point=[0,0],anchored_position=[1,13], background_tight=True))
		
		self.menu['labels'].append(adafruit_display_text.label.Label(
			device.font, color=self.menucolor, background_color=0x000000, text='', line_spacing=1,
			label_direction='LTR',anchor_point=[0,0],anchored_position=[1,19], background_tight=True))

		self.optionlabel = adafruit_display_text.label.Label(
			device.font, color=self.optioncolor, background_color=0x000000, text='OPTION', line_spacing=1,
			label_direction='LTR',anchor_point=[0,1],anchored_position=[1,31], background_tight=True)

		device.clearDisplayGroup(device.menu_group)
		device.menu_group.append(self.menu['labels'][0])
		device.menu_group.append(self.menu['labels'][1])
		device.menu_group.append(self.menu['labels'][2])
		device.menu_group.append(self.menu['labels'][3])
		device.menu_group.append(self.optionlabel)
		# start hidden
		device.menu_group.hidden = 1

		self.overlay = adafruit_display_text.label.Label(
			device.font, color=self.menucolor, background_color=0x000000, text='Overlay', line_spacing=1,
			label_direction='LTR',anchor_point=[0,1],anchored_position=[1,31], background_tight=True)
		
		device.overlay_group.append(self.overlay)
		device.overlay_group.hidden = True
		
	def showMenu(self):
		# call showMenu AFTER initial effect is loaded
		#self.moveCaret(0, 0)
		self.refreshMenu()
		self.device.menu_group.hidden = 0 # show menu

	def hideMenu(self):
		self.device.menu_group.hidden = 1

	def setColors(self):
		self.menucolor = self.device.hls(.18, .5, 1)
		self.selectedcolor = self.device.hls(.01, .2, 1)
		self.optioncolor = self.device.hls(.6, .4, 1)

	def refreshMenu(self):
		i=0
		# refresh all displayed options
		while i < len(self.menu['options']) and i < 4:
			self.menu['labels'][i].text = self.menu['options'][i+self.offset]['label']
			self.menu['labels'][i].color = self.menucolor if self.caret != i+self.offset else self.selectedcolor
			i += 1
		# refresh the selected option label
		self.optionlabel.text = self.menu['options'][self.caret]['get']()
		self.optionlabel.color = self.optioncolor
		
	def changeOption(self, direction:int):
		self.menu['options'][self.caret]['set'](direction)

	def moveCaret(self, direction:int, n:int=None):
		if direction == 1:
			self.caret = self.caret + 1 if self.caret < len(self.menu['options'])-1 else 0
		elif direction == -1:
			self.caret = self.caret - 1 if self.caret > 0 else len(self.menu['options'])-1
		elif direction == 0 and n != None:
			self.caret = n
		self.offset = self.caret-3 if self.caret-3 > 0 else 0

	def getEffectMenu(self):
		#clear menu except option 0 / Effect switch
		i=len(self.menu['options'])-1
		while i>0:
			self.menu['options'].pop(i)
			i -= 1
		if hasattr(self.device.effect, 'menu'):
			i=0
			# add the effect options to the menu
			while i<len(self.device.effect.menu):
				self.menu['options'].append(self.device.effect.menu[i])
				i += 1
		# clear the previous labels, set them from the current menu options
		self.menu['labels'][0].text = ''
		self.menu['labels'][1].text = ''
		self.menu['labels'][2].text = ''
		self.menu['labels'][3].text = ''

	def play(self):	
		if sum(locals()['keys']) and self.device.limitStep(self.device.buttonPause, self.device.lastButtonTick): 
			# only enter this loop if a button is down and it hasn't been too soon since last press
			if locals()['keys'][0]:
				self.device.setLastButtonTick()
				self.hideMenu()

			if locals()['keys'][1]:
				self.device.setLastButtonTick()
				self.moveCaret(1)

			if locals()['keys'][2]:
				self.device.setLastButtonTick()
				self.changeOption(-1)

			if locals()['keys'][3]:
				self.device.setLastButtonTick()
				self.changeOption(1)
		else:
			if (self.device.limitStep(self.device.buttonPause, self.lastMenuRefresh)):
				self.lastMenuRefresh = time.monotonic()
				self.refreshMenu()

	def handleRemote(self, key:str):
		if key == 'Setup':
			self.hideMenu()
		elif key == 'Up':
			self.moveCaret(-1)
		elif key == 'Down':
			self.moveCaret(1)
		elif key == 'Left':
			self.changeOption(-1)
		elif key == 'Right' or key == 'Enter':
			self.changeOption(1)

	def showOverlay(self, message:str):
		self.device.lastOverlayUpdate = time.monotonic()
		self.overlay.text = message
		self.device.overlay_group.hidden = False