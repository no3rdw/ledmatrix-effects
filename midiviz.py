import time, random, vectorio, displayio, math
import usb_midi
import adafruit_midi
from effect import Effect

from adafruit_midi.note_off import NoteOff
from adafruit_midi.note_on import NoteOn
from adafruit_midi.start import Start
from adafruit_midi.stop import Stop

class MidiViz(Effect):
	def __init__(self, device:Device):
		self.name = type(self).__name__
		self.displayname = 'MidiViz'
		self.device = locals()['device']

		self.channelcount = 6
		self.baseoctave = 2
		self.octavecount = 2
		self.noteradius = 5

		device.clearDisplayGroup(device.effect_group)

		self.menu = [
			#{
			#	'label': 'Setting',
			#	'set': self.setFunction,
			#	'get': self.getFunction
			#}
        ]
		self.lastFrame = 0
		self.lastCleanup = 0
		self.usbmidi = adafruit_midi.MIDI(midi_in=usb_midi.ports[0], midi_out=usb_midi.ports[1], in_buf_size=8)

		self.p = displayio.Palette(32)
		self.p[0] = device.hls(.6, .1, .8) # bg
		self.p[1] = device.hls(.1, .6, .5) # white
		self.p[2] = device.hls(.25, .6, .5) # white
		self.p[3] = device.hls(.4, .6, .5) # white
		self.p[4] = device.hls(.55, .6, .5) # white
		self.p[5] = device.hls(.7, .6, .5) # white
		self.p[6] = device.hls(.85, .6, .5) # white

		self.bitmap = displayio.Bitmap(device.display.width, device.display.height, len(self.p))
		self.tile_grid = displayio.TileGrid(self.bitmap, pixel_shader=self.p)
		device.effect_group.append(self.tile_grid)

		self.notegroup = displayio.Group()
		device.effect_group.append(self.notegroup)

		# create an array of the 6 channels, each containing an object of notes
		# the note's keyboard position is used as the object key because only one can be 'on' at each position per channel
		self.channels = []
		x = 0
		while x < self.channelcount:
			self.channels.append({})
			x = x + 1

		self.xspace = self.device.display.width / (self.octavecount * 12)
		if self.xspace == 0: self.xspace = 1
		self.centeroffset = round((self.device.display.width - self.octavecount*self.xspace*12) /2 )

		t = self.channelcount-1
		if t == 0: t = 1
		self.yspace = (self.device.display.height - (self.channelcount * (self.noteradius * 2)))/t

		self.firstnoteoffset = round(self.baseoctave * 12 + 24)

	def cleanupNotes(self):
		for c in self.channels:
			for n in c:
				if time.monotonic() > c[n]['timeout']:
					try:
						self.removeNote(c[n])
					except:
						pass

	def removeNote(self, note):
		#print('delete: channel', note['channel'], " note:", note['note'] )
		self.notegroup.remove(self.channels[note['channel']][note['note']]['group'])
		del self.channels[note['channel']][note['note']]
		self.device.gc()

	def resetNotes(self):
		while len(self.notegroup):
			self.notegroup.pop(0)
		for c in self.channels:
			c = {}

	def initNote(self, note, velocity, channel):
		if not hasattr(self.channels[channel], str(note)):
			v = round(self.noteradius*(velocity/127))
			if v == 0: v = 1
			c = {}
			c['note'] = note
			c['offsetnote'] = note-self.firstnoteoffset
			c['velocity'] = v 
			c['channel'] = channel
			c['group'] = vectorio.Circle(pixel_shader=self.p,
								x=math.floor((c['offsetnote']*self.xspace)+self.centeroffset), 
								y=math.floor((channel*(self.noteradius*2))+self.noteradius+(channel*self.yspace)),
								radius=v,
								color_index=channel+1)
			c['timeout'] = time.monotonic() + 2
			self.notegroup.append(c['group'])
			return c 
		else:
			# if this note already exists for this channel, extend its timeout without adding a new note
			self.channels[channel][str(note)]['timeout'] = time.monotonic() + 2

	def play(self):
	
		if self.device.menu_group.hidden and sum(locals()['keys']):
			if locals()['keys'][3]:
				self.resetNotes()

		msg = self.usbmidi.receive()

		if msg is not None:
			print("Received:", msg, "at", time.monotonic())

		if type(msg) is NoteOn:
			if msg.channel < self.channelcount and msg.velocity > 0:
				#print(msg)
				self.channels[msg.channel][msg.note] = self.initNote(msg.note, msg.velocity, msg.channel)
			elif msg.channel < self.channelcount and msg.velocity == 0:
				try:
					self.removeNote(self.channels[msg.channel][msg.note])
				except:
					pass
		elif type(msg) is NoteOff:
			if msg.channel < self.channelcount:
				#print(msg)
				try:
					self.removeNote(self.channels[msg.channel][msg.note])
				except:
					pass
			
		if (self.device.limitStep(1, self.lastCleanup)):
			# cleanup any notes that have been visible for longer than their timeout in case any noteoff messages were missed
			self.cleanupNotes()
			self.lastCleanup = time.monotonic()
	
	def handleRemote(self, key:str):
		print(key)
		if key == 'Enter':
			self.resetNotes()