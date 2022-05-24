from __future__ import absolute_import

from Components.Pixmap import Pixmap
from Screens.Screen import Screen


class UnhandledKey(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self["UnhandledKeyPixmap"] = Pixmap()
