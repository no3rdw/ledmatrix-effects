import time, json
from effect import Effect
import adafruit_display_text.label

class Effect(Effect):
	def __init__(self, device:Device):
		self.name = 'Weather'
		super().__init__(device, self.name)
		
		self.device = locals()['device']

		device.clearDisplayGroup(device.effect_group)

		self.label = adafruit_display_text.label.Label(
			device.font, color=0xFFFFFF, background_color=None, text='', line_spacing=1,
			label_direction='LTR',anchor_point=[0,1],anchored_position=[1,10], base_alignment=True, background_tight=True)
		self.label.text = ""

		device.effect_group.append(self.label)



		self.menu = [
			#{
			#	'label': 'Setting',
			#	'set': self.setFunction,
			#	'get': self.getFunction
			#}
		]
	
	def play(self):
		pass

	def handleMessage(self, message:str):
		try:
			struct = json.loads(message)
			temp = struct['current']['temperature_2m']
			self.label.text = str(temp) + 'F'
		except Exception as e:
			print('EXCEPTION', e)
		pass
	
	def handleRemote(self, key:str):
		print(key)
		if key == 'Enter' and len(self.device.sendMessage) == 0:
			self.label.text = "WAIT"
			self.device.sendMessage = self.device.prepMessage('GETWEATHER')