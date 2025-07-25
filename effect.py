import time
# This is a class template applied to all other defined Effects (including the Menu)

class Effect:
	def __init__(self, device:Device, realname):
		#super().__init__(device)
		self.device = locals()['device']

		self.settings = self.device.loadData(realname.lower() + '.json')
		#if not self.settings: #set defaults
		#	self.settings = {'setting':'default'}

		#device.clearDisplayGroup(device.effect_group)

		self.effectmenu = [
			{
				'label': 'Save',
				'set': self.saveSettings,
				'get': lambda: '<Press>'
			}
        ]
		#self.menu.extend(self.effectmenu)
		self.device.clockcolor = 0x000000
		self.device.clockposition = None
		#self.device.clockposition = {'anchor_point':[0,0],'anchored_position':[1,1]}
		
		self.lastFrame = 0

	def play(self):
		if (self.device.limitStep(.1, self.lastFrame)):
			# do stuff
			
			self.lastFrame = time.monotonic()

	def handleRemote(self, key:str):
		if key == 'Enter':
			pass

	def saveSettings(self, direction:int=0):
		self.device.writeData(self.settings, self.name.lower() + '.json')