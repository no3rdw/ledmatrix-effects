import time, random
import adafruit_display_text.label
# This is a class template applied to all other defined Effects (including the Menu)

class Effect:
	def __init__(self, device:Device):
		self.device = locals()['device']

		self.settings = self.device.settings
		self.lastFrame = time.monotonic()
		self.lastMove = time.monotonic()
		
		self.clockPositions = [		
			{'anchor_point':[0,0],'anchored_position':[1,1]},	 		
			{'anchor_point':[0,1],'anchored_position':[1,31]},
			{'anchor_point':[1,0],'anchored_position':[32,1]},
			{'anchor_point':[1,1],'anchored_position':[32,31]}
		]
		self.selectedClockPosition = 1
	
		self.clocklabel = adafruit_display_text.label.Label(
			device.font, color=self.device.clockcolor, background_color=None, text='', line_spacing=1,
			label_direction='LTR',anchor_point=[0,1],anchored_position=[1,31], base_alignment=True, background_tight=True)

		device.clearDisplayGroup(device.clock_group)
		device.clock_group.append(self.clocklabel)

	def play(self):
		if (self.device.limitStep(.4, self.lastFrame)):
			self.clocklabel.color = self.device.clockcolor
			self.clocklabel.text = self.device.getTime(self.device.str2bool(self.device.settings['displaySeconds']))
			if(self.device.getTime(True)[-2:] == '00' and self.device.limitStep(30, self.lastMove)):
				if self.device.settings['displaySeconds'] == 'True':
					self.selectedClockPosition = 1
				else: 
					self.selectedClockPosition =  self.device.cycleOption([0,1,2,3], self.selectedClockPosition, 1)
				self.lastMove = time.monotonic()

			self.lastFrame = time.monotonic()
			self.clocklabel.anchor_point = self.clockPositions[self.selectedClockPosition]['anchor_point']
			self.clocklabel.anchored_position = self.clockPositions[self.selectedClockPosition]['anchored_position']

		