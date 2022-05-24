from __future__ import absolute_import

from os import path as os_path
from random import randint

from enigma import ePoint, eTimer, iPlayableService

from Components.MovieList import AUDIO_EXTENSIONS
from Components.Pixmap import Pixmap
from Components.ServiceEventTracker import ServiceEventTracker
from Screens.Screen import Screen


class Screensaver(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)

		self.moveLogoTimer = eTimer()
		self.moveLogoTimer.callback.append(self.doMovePicture)
		self.onShow.append(self.__onShow)
		self.onHide.append(self.__onHide)

		self.__event_tracker = ServiceEventTracker(screen=self, eventmap={
				iPlayableService.evStart: self.serviceStarted
			})

		self["picture"] = Pixmap()

		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		picturesize = self["picture"].getSize()
		self.maxx = self.instance.size().width() - picturesize[0]
		self.maxy = self.instance.size().height() - picturesize[1]
		self.doMovePicture()

	def __onHide(self):
		self.moveLogoTimer.stop()

	def __onShow(self):
		self.moveLogoTimer.startLongTimer(5)

	def serviceStarted(self):
		if self.shown:
			ref = self.session.nav.getCurrentlyPlayingServiceOrGroup()
			if ref:
				ref = ref.toString().split(":")
				flag = ref[2] == "2" or ref[2] == "A" or os_path.splitext(ref[10])[1].lower() in AUDIO_EXTENSIONS
				if not flag:
					self.hide()

	def doMovePicture(self):
		self.posx = randint(1, self.maxx)
		self.posy = randint(1, self.maxy)
		self["picture"].instance.move(ePoint(self.posx, self.posy))
		self.moveLogoTimer.startLongTimer(9)
