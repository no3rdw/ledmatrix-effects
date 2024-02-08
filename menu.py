import adafruit_display_text.label
import adafruit_display_shapes.rect
import time

class Menu:

	def __init__(self, device:Device):
		self.name = 'Menu'
		self.menu = []
		self.effectmenu = []
		self.carat = 0
		self.device = device

		self.menucolor = 0xffff00
		self.selectedcolor = 0x660000
		self.optioncolor = 0x006666

		self.lastOptionLabelRefresh = 0

		#longtext = adafruit_display_text.wrap_text_to_pixels("MENU TEST",device.matrix.width,device.font)
		#longtext = "\n".join(longtext)

		#self.menubg = adafruit_display_shapes.rect.Rect(x=1,y=1, width=25, height=23, fill=0x000000)

		self.menu.append(adafruit_display_text.label.Label(
			device.font, color=self.selectedcolor, background_color=0x000000, text='Effect', line_spacing=1,
			label_direction='LTR',anchor_point=[0,0],anchored_position=[1,1], background_tight=True))
		
		self.menu.append(adafruit_display_text.label.Label(
			device.font, color=self.menucolor, background_color=0x000000, text='', line_spacing=1,
			label_direction='LTR',anchor_point=[0,0],anchored_position=[1,7], background_tight=True))
		
		self.menu.append(adafruit_display_text.label.Label(
			device.font, color=self.menucolor, background_color=0x000000, text='', line_spacing=1,
			label_direction='LTR',anchor_point=[0,0],anchored_position=[1,13], background_tight=True))
		
		self.menu.append(adafruit_display_text.label.Label(
			device.font, color=self.menucolor, background_color=0x000000, text='', line_spacing=1,
			label_direction='LTR',anchor_point=[0,0],anchored_position=[1,19], background_tight=True))

		self.optionlabel = adafruit_display_text.label.Label(
			device.font, color=self.optioncolor, background_color=0x000000, text='OPTION', line_spacing=1,
			label_direction='LTR',anchor_point=[0,1],anchored_position=[1,31], background_tight=True)

		device.clearDisplayGroup(device.menu_group)
		#device.menu_group.append(self.menubg)
		device.menu_group.append(self.menu[0])
		device.menu_group.append(self.menu[1])
		device.menu_group.append(self.menu[2])
		device.menu_group.append(self.menu[3])
		device.menu_group.append(self.optionlabel)

		device.menu_group.hidden = 1
		
	def showMenu(self):
		# call showMenu AFTER initial effect is loaded
		self.refreshOptionLabel()
		self.device.menu_group.hidden = 0 # show menu

	def hideMenu(self):
		self.device.menu_group.hidden = 1
		self.device.resetKeypixel(0)
		self.device.resetKeypixel(1)
		self.device.resetKeypixel(2)
		self.device.resetKeypixel(3)

	def highlightCarat(self):
		i=0
		while i < len(self.menu):
			self.menu[i].color = self.menucolor if self.carat != i else self.selectedcolor
			i += 1

	def refreshOptionLabel(self):
		if self.carat == 0:
			self.optionlabel.text = self.device.effect.name
		elif self.carat == 1 and hasattr(self.device.effect, 'optionlabel1'):
			self.optionlabel.text = self.device.effect.optionlabel1()
		elif self.carat == 2 and hasattr(self.device.effect, 'optionlabel2'):
			self.optionlabel.text = self.device.effect.optionlabel2()
		elif self.carat == 3 and hasattr(self.device.effect, 'optionlabel3'):
			self.optionlabel.text = self.device.effect.optionlabel3()

	def changeOption(self, direction:int):
		if self.carat == 0:
			self.device.cycleEffect(direction)
		elif self.carat == 1 and hasattr(self.device.effect, 'setoption1'):
			self.device.effect.setoption1(direction)
		elif self.carat == 2 and hasattr(self.device.effect, 'setoption2'):
			self.device.effect.setoption2(direction)
		elif self.carat == 3 and hasattr(self.device.effect, 'setoption3'):
			self.device.effect.setoption3(direction)

	def moveCarat(self, direction:int):
		if direction > 0:
			# moving down
			self.carat = self.carat + 1 if self.carat < len(self.effectmenu) else 0
		else:
			#moving up
			self.carat = self.carat - 1 if self.carat > 0 else len(self.effectmenu)
		self.highlightCarat()
		self.refreshOptionLabel()

	def getEffectMenu(self):
		self.effectmenu = []
		if hasattr(self.device.effect, 'menu'):
			self.effectmenu = self.device.effect.menu
			self.menu[1].text = ''
			self.menu[2].text = ''
			self.menu[3].text = ''
			i=0
			while i < len(self.effectmenu):
				self.menu[i+1].text = self.effectmenu[i]
				i += 1

	def play(self):	
		if sum(locals()['keys']): # only enter this loop if a button is down
			if locals()['keys'][3]:
				if (self.device.limitStep(.15, self.device.lastButtonTick)):
					self.device.setLastButtonTick()
					self.hideMenu()
					#self.device.neokey.pixels[3] = (255, 200, 40)
					#if self.carat == 0:
					#	self.hideMenu()
					#else:
					#	self.moveCarat(-1)
			else:
				self.device.resetKeypixel(3)

			if locals()['keys'][2]:
				if (self.device.limitStep(.15, self.device.lastButtonTick)):
					self.device.setLastButtonTick()
					self.device.neokey.pixels[2] = (255, 200, 40)
					self.moveCarat(1)
			else:
				self.device.resetKeypixel(2)

			if locals()['keys'][1]:
				if (self.device.limitStep(.15, self.device.lastButtonTick)):
					self.device.setLastButtonTick()
					self.device.neokey.pixels[1] = (255, 200, 40)
					self.changeOption(-1)
			else:
				self.device.resetKeypixel(1)

			if locals()['keys'][0]:
				if (self.device.limitStep(.15, self.device.lastButtonTick)):
					self.device.setLastButtonTick()
					self.device.neokey.pixels[0] = (255, 200, 40)
					self.changeOption(1)
			else:
				self.device.resetKeypixel(0)

		if (self.device.limitStep(.15, self.lastOptionLabelRefresh)):
			self.lastOptionLabelRefresh = time.monotonic()
			self.refreshOptionLabel()
