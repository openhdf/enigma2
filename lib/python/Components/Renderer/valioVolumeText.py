########################################################
#
#    VolumeText Renderer for Dreambox/Enigma-2
#    Version: 1.0
#    Coded by Vali (c)2010
#
########################################################

from Components.VariableText import VariableText
from Components.config import config
from enigma import eLabel, eDVBVolumecontrol, eTimer
from Renderer import Renderer

class valioVolumeText(Renderer, VariableText):
	def __init__(self):
		Renderer.__init__(self)
		VariableText.__init__(self)
		try:
			if config.valiflex.VolumePRZ.value == "prz":
				self.volProper = 1
			else:
				self.volProper = 5
		except:
			self.volProper = 5
		self.vol_timer = eTimer()
		self.vol_timer.callback.append(self.pollme)
	GUI_WIDGET = eLabel

	def changed(self, what):
		if not self.suspended:
			self.text = str(eDVBVolumecontrol.getInstance().getVolume()/self.volProper)

	def pollme(self):
		self.changed(None)

	def onShow(self):
		self.suspended = False
		self.vol_timer.start(200)

	def onHide(self):
		self.suspended = True
		self.vol_timer.stop()
