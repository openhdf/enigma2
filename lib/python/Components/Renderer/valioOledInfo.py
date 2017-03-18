# -*- coding: utf-8 -*-
#
#    OLED-Info Renderer for Dreambox/Enigma-2
#    Version: 1.0
#    Coded by Vali (c)2011
#
#######################################################################

from enigma import eLabel
from Renderer import Renderer
from os import popen
from time import localtime, strftime
from Components.VariableText import VariableText
from Components.Sensors import sensors
from Components.config import config
from Tools.HardwareInfo import HardwareInfo

class valioOledInfo(Renderer, VariableText):
	def __init__(self):
		Renderer.__init__(self)
		VariableText.__init__(self)
		try:
			self.infozahl = int(config.valiflex.OledInfo.value)
		except:
			self.infozahl = 12
		self.Zaehler = 0
		self.oben = "---"
		self.unten = "---"
	GUI_WIDGET = eLabel

	def changed(self, what):
		if not self.suspended:
			if self.Zaehler > self.infozahl:
				self.Zaehler = 0
			if self.Zaehler == 0:
				self.hide()
			elif self.Zaehler == 6:
				self.show()
				t = localtime(self.source.time)
				self.oben = _(strftime("%a", t)) + " " +strftime("%d", t)
				self.unten = "%02d:%02d" % (t.tm_hour, t.tm_min)
			elif self.Zaehler == 14:
				self.oben = "temp:"
				maxtemp = 0
				try:
					templist = sensors.getSensorsList(sensors.TYPE_TEMPERATURE)
					tempcount = len(templist)
					for count in range(tempcount):
						id = templist[count]
						tt = sensors.getSensorValue(id)
						if tt > maxtemp:
							maxtemp = tt
				except:
					pass
				self.unten = str(maxtemp) + " °C"
			elif self.Zaehler == 21:
				self.oben = "loads:"
				loada = 0
				try:
					out_line = open("/proc/loadavg").readline()
					loada = out_line[:4]
				except:
					pass
				self.unten = loada
			elif self.Zaehler == 28:
				self.oben = "free:"
				out_lines = []
				out_lines = open("/proc/meminfo").readlines()
				for lidx in range(len(out_lines)-1):
					tstLine = out_lines[lidx].split()
					if "MemFree:" in tstLine:
						templ = int(out_lines[lidx].split()[1])
						fmem = "%d mb" %(templ/1024)
						self.unten = str(fmem)
			self.Zaehler = self.Zaehler + 1
			self.text = self.oben + "\n" + self.unten

	def onShow(self):
		self.suspended = False
		self.changed(None)

	def onHide(self):
		self.suspended = True
