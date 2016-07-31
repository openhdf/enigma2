from . import _
from Plugins.Plugin import PluginDescriptor

def main(session, **kwargs):
	import Sc
	session.open(Sc.ScSelection)

def menu(menuid, **kwargs):
	if menuid == "cam":
		return [(_("Softcam Manager..."), main, "softcam_setup", 45)]
	return []

def Plugins(**kwargs):
	return [PluginDescriptor(name = "Softcam Cardserver Manager", description = "Lets you configure your softcams", where = PluginDescriptor.WHERE_MENU, fnc = menu),
			PluginDescriptor(name="Softcam Cardserver Manager", description="start/stop Softcams", where = PluginDescriptor.WHERE_EXTENSIONSMENU, fnc=main)]
