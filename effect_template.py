import time

class Effect:
	def __init__(self, device:Device):
		self.name = type(self).__name__
		self.displayname = 'Effect'
		self.device = locals()['device']

		device.clearDisplayGroup(device.effect_group)

		self.menu = [
			#{
			#	'label': 'Setting',
			#	'set': self.setFunction,
			#	'get': self.getFunction
			#}
        ]
		self.lastFrame = 0

	def play(self):
		if (self.device.limitStep(.1, self.lastFrame)):
			# do stuff
			
			self.lastFrame = time.monotonic()