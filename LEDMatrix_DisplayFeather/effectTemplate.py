import time
from effect import Effect

class Effect(Effect):
	def __init__(self, device:Device):
		self.name = 'Template'
		super().__init__(device, self.name)
		self.device = locals()['device']

		if not self.settings: #set defaults
			self.settings = {'setting':'default'}

		self.device.clockcolor = 0x000000
		self.device.clockposition = None
		#self.device.clockposition = {'anchor_point':[0,0],'anchored_position':[1,1]}

		device.clearDisplayGroup(device.effect_group)

		self.menu = [
			#{
			#	'label': 'Label',
			#	'set': self.saveSetting,
			#	'get': lambda: '<Press>'
			#}
        ]
		self.menu.extend(self.effectmenu)
		
		self.lastFrame = 0

	def play(self):
		if (self.device.limitStep(.1, self.lastFrame)):
			# do stuff
			
			self.lastFrame = time.monotonic()

	def handleRemote(self, key:str):
		if key == 'Enter':
			pass