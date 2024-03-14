
from boxbranding import getBoxType

from Components.config import ConfigNothing, ConfigSelection, config
from Components.SystemInfo import BoxInfo
from Tools.Directories import fileExists


class WOL:
	def __init__(self):
		pass

	def setWolState(self, value):
		print('[WakeOnLAN] set:', value)
		if fileExists("/proc/stb/fp/wol"):
			f = open("/proc/stb/fp/wol", "w")
			f.write(value)
			f.close()
		elif fileExists("/proc/stb/power/wol"):
			f = open("/proc/stb/power/wol", "w")
			f.write(value)
			f.close()


def Init():
	if BoxInfo.getItem("WakeOnLAN") and not getBoxType() in ('gbquad', 'gbquadplus'):
		def setWOLmode(value):
			iwol.setWolState(config.network.wol.value)

		iwol = WOL()
		config.network.wol = ConfigSelection([("disable", _("No")), ("enable", _("Yes"))], default="disable")
		config.network.wol.addNotifier(setWOLmode, initial_call=True)
	elif BoxInfo.getItem("ETWOL"):
		def setWOLmode(value):
			iwol.setWolState(config.network.wol.value)

		iwol = WOL()
		config.network.wol = ConfigSelection([("off", _("No")), ("on", _("Yes"))], default="off")
		config.network.wol.addNotifier(setWOLmode, initial_call=True)
	else:
		def doNothing():
			pass
		config.network.wol = ConfigNothing()
