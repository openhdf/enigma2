from __future__ import absolute_import

from Components.Sources.Clock import Clock
from Components.Sources.OnlineUpdate import (OnlineUpdateStableCheck,
                                             OnlineUpdateUnstableCheck)
from Screens.Screen import Screen


class Globals(Screen):
	def __init__(self):
		Screen.__init__(self, None)
		self["CurrentTime"] = Clock()
		self["OnlineStableUpdateState"] = OnlineUpdateStableCheck()
		self["OnlineUnstableUpdateState"] = OnlineUpdateUnstableCheck()
