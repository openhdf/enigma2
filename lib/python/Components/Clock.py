from __future__ import absolute_import
from Components.HTMLComponent import HTMLComponent
from Components.GUIComponent import GUIComponent
from Components.VariableText import VariableText

from enigma import eTimer, eLabel

import time
# now some "real" components:


class Clock(VariableText, HTMLComponent, GUIComponent):
	def __init__(self):
		VariableText.__init__(self)
		GUIComponent.__init__(self)
		self.doClock()

		self.clockTimer = eTimer()
		self.clockTimer.callback.append(self.doClock)

	def onShow(self):
		self.doClock()
		self.clockTimer.start(1000)

	def onHide(self):
		self.clockTimer.stop()

	def doClock(self):
		t = time.localtime()
		timestr = "%2d:%02d:%02d" % (t.tm_hour, t.tm_min, t.tm_sec)
		self.setText(timestr)

	def createWidget(self, parent):
		return eLabel(parent)

	def removeWidget(self, w):
		del self.clockTimer

	def produceHTML(self):
		return self.getText()
