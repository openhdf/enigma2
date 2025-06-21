# for localized messages
from . import _

from .HddSetup import HddSetup
from .HddMount import HddFastRemove
from Plugins.Plugin import PluginDescriptor
import os


def supportExtFat():
	if "exfat-fuse" in open("/etc/filesystems").read():
		pass
	else:
		os.system("echo exfat-fuse >> /etc/filesystems && opkg update && opkg install fuse-exfat")
	if not os.path.isfile("/sbin/hdparm.hdparm"):
		os.system("opkg update && opkg install hdparm")


def deviceManagerMain(session, **kwargs):
	supportExtFat()
	session.open(HddSetup)


def deviceManagerSetup(menuid, **kwargs):
	if menuid != "harddisk":
		return []
	return [(_("Device Manager"), deviceManagerMain, "device_manager", 1)]


def deviceManagerFastRemove(session, **kwargs):
	session.open(HddFastRemove)


def Plugins(**kwargs):
	return [PluginDescriptor(name=_("Device Manager"), description=_("Format/Partition your Devices and manage Mountpoints"), where=PluginDescriptor.WHERE_MENU, fnc=deviceManagerSetup),
			PluginDescriptor(name=_("Device Manager - Fast mounted remove"), description=_("Quick and safe remove for your mounted devices "), where=PluginDescriptor.WHERE_EXTENSIONSMENU, fnc=deviceManagerFastRemove)]
