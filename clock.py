import time, random
import adafruit_display_text.label

class Effect:
	def __init__(self, device:Device):
		self.device = locals()['device']

		self.settings = self.device.settings
		self.lastFrame = 0
		self.lastMove = time.monotonic()
		
		self.clockPositions = [		
			{'anchor_point':[0,0],'anchored_position':[1,1]},	 		
			{'anchor_point':[0,1],'anchored_position':[1,self.device.display.height-1]},
			{'anchor_point':[1,0],'anchored_position':[self.device.display.width,1]},
			{'anchor_point':[1,1],'anchored_position':[self.device.display.width,self.device.display.height-1]}
		]
		self.selectedClockPosition = 1
	
		self.clocklabel = adafruit_display_text.label.Label(
			device.font, color=self.device.clockcolor, background_color=None, text='', line_spacing=1,
			label_direction='LTR',anchor_point=[0,1],anchored_position=[1,self.device.display.height-1], base_alignment=True, background_tight=True)

		device.clearDisplayGroup(device.clock_group)
		device.clock_group.append(self.clocklabel)

	def updateClock(self):
		self.clocklabel.color = self.device.clockcolor
		self.clocklabel.text = self.device.getTime(self.device.str2bool(self.device.settings['displaySeconds']))
		if(self.device.getTime('seconds')[-2:] == '00' and self.device.limitStep(2, self.lastMove)):
			self.selectedClockPosition = self.device.cycleOption([0,1,2,3], self.selectedClockPosition, 1)
			self.lastMove = time.monotonic()

		if self.device.clockposition == None: 
			# when device.clockposition is null, we auto-cycle through the four positions above
			self.clocklabel.anchor_point = self.clockPositions[self.selectedClockPosition]['anchor_point']
			self.clocklabel.anchored_position = self.clockPositions[self.selectedClockPosition]['anchored_position']
		else:
			# but when the selected effect defines clockposition, we use that
			self.clocklabel.anchor_point = self.device.clockposition['anchor_point']
			self.clocklabel.anchored_position = self.device.clockposition['anchored_position']

	def play(self):
		if (self.device.limitStep(.3, self.lastFrame)):
			self.updateClock()
			self.lastFrame = time.monotonic()
