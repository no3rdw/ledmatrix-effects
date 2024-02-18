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
		
		self.menucolor = device.hls(.18, .5, 1)
		self.selectedcolor = device.hls(.01, .2, 1)
		self.optioncolor = device.hls(.6, .4, 1)

		self.lastOptionLabelRefresh = 0

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
		
	def showMenu(self):
		# call showMenu AFTER initial effect is loaded
		self.moveCaret(0, 0)
		self.refreshMenu()
		self.device.menu_group.hidden = 0 # show menu

	def hideMenu(self):
		self.device.menu_group.hidden = 1
		self.device.resetKeypixel(0)
		self.device.resetKeypixel(1)
		self.device.resetKeypixel(2)
		self.device.resetKeypixel(3)

	def refreshMenu(self):
		i=0
		# refresh all displayed options
		while i < len(self.menu['options']) and i < 4:
			self.menu['labels'][i].text = self.menu['options'][i+self.offset]['label']
			self.menu['labels'][i].color = self.menucolor if self.caret != i+self.offset else self.selectedcolor
			i += 1
		# refresh the selected option label
		self.optionlabel.text = self.menu['options'][self.caret]['get']()
		
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
		if sum(locals()['keys']): # only enter this loop if a button is down
			if locals()['keys'][0]:
				if (self.device.limitStep(.15, self.device.lastButtonTick)):
					self.device.setLastButtonTick()
					self.hideMenu()
			else:
				self.device.resetKeypixel(0)

			if locals()['keys'][1]:
				if (self.device.limitStep(.15, self.device.lastButtonTick)):
					self.device.setLastButtonTick()
					self.device.neokey.pixels[1] = (255, 200, 40)
					self.moveCaret(1)
			else:
				self.device.resetKeypixel(1)

			if locals()['keys'][2]:
				if (self.device.limitStep(.15, self.device.lastButtonTick)):
					self.device.setLastButtonTick()
					self.device.neokey.pixels[2] = (255, 200, 40)
					self.changeOption(-1)
			else:
				self.device.resetKeypixel(2)

			if locals()['keys'][3]:
				if (self.device.limitStep(.15, self.device.lastButtonTick)):
					self.device.setLastButtonTick()
					self.device.neokey.pixels[3] = (255, 200, 40)
					self.changeOption(1)
			else:
				self.device.resetKeypixel(3)

			if (not self.device.menu_group.hidden and self.device.limitStep(.15, self.lastOptionLabelRefresh)):
				self.lastOptionLabelRefresh = time.monotonic()
				self.refreshMenu()
