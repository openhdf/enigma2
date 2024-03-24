from Plugins.Plugin import PluginDescriptor
from Components.Scanner import scanDevice
from Screens.InfoBar import InfoBar
from os import access, F_OK, R_OK

parentScreen = None


def execute(option):
	#print "execute", option
	if option is None:
		if parentScreen:
			parentScreen.close()
		return

	(_, scanner, files, session) = option
	scanner.open(files, session)
	if parentScreen:
		parentScreen.close()


def mountpoint_choosen(option):
	if option is None:
		if parentScreen:
			parentScreen.close()
		return

	#print "scanning", option
	(description, mountpoint, session) = option
	res = scanDevice(mountpoint)

	list = [(r.description, r, res[r], session) for r in res]

	if not list:
		from Screens.MessageBox import MessageBox
		if access(mountpoint, F_OK | R_OK):
			session.open(MessageBox, _("No displayable files on this medium found!"), MessageBox.TYPE_INFO, simple=False, timeout=5)
		#else:
		#	print "ignore", mountpoint, "because its not accessible"
		if parentScreen:
			parentScreen.close()
		return

	from Screens.ChoiceBox import ChoiceBox
	session.openWithCallback(execute, ChoiceBox,
		title=_("The following files were found..."),
		list=list)


def scan(session, parent=None):
	global parentScreen
	parentScreen = parent
	from Screens.ChoiceBox import ChoiceBox
	parts = [(r.tabbedDescription(), r.mountpoint, session) for r in harddiskmanager.getMountedPartitions(onlyhotplug=False) if access(r.mountpoint, F_OK | R_OK)]
	parts.append((_("Memory") + "\t/tmp", "/tmp", session))
	session.openWithCallback(mountpoint_choosen, ChoiceBox, title=_("Please select medium to be scanned"), list=parts)


def main(session, **kwargs):
	scan(session)


def menuEntry(*args):
	mountpoint_choosen(args)


from Components.Harddisk import harddiskmanager


def menuHook(menuid):
	if menuid != "mainmenu":
		return []
	from Tools.BoundFunction import boundFunction
	return [(("%s (files)") % r.description, boundFunction(menuEntry, r.description, r.mountpoint), "hotplug_%s" % r.mountpoint, None) for r in harddiskmanager.getMountedPartitions(onlyhotplug=True)]


global_session = None


def partitionListChanged(action, device):
	if InfoBar.instance:
		if InfoBar.instance.execing:
			if action == 'add' and device.is_hotplug:
				#print "mountpoint", device.mountpoint
				#print "description", device.description
				#print "force_mounted", device.force_mounted
				mountpoint_choosen((device.description, device.mountpoint, global_session))
		#else:
			#print "main infobar is not execing... so we ignore hotplug event!"
	#else:
			#print "hotplug event.. but no infobar"


def sessionstart(reason, session):
	global global_session
	global_session = session


def autostart(reason, **kwargs):
	global global_session
	if reason == 0:
		harddiskmanager.on_partition_list_change.append(partitionListChanged)
	elif reason == 1:
		harddiskmanager.on_partition_list_change.remove(partitionListChanged)
		global_session = None


def Plugins(**kwargs):
	return [
		PluginDescriptor(name=_("Media scanner"), description=_("Scan files..."), where=PluginDescriptor.WHERE_PLUGINMENU, icon="MediaScanner.png", needsRestart=True, fnc=main),
#		PluginDescriptor(where = PluginDescriptor.WHERE_MENU, fnc=menuHook),
		PluginDescriptor(where=PluginDescriptor.WHERE_SESSIONSTART, needsRestart=True, fnc=sessionstart),
		PluginDescriptor(where=PluginDescriptor.WHERE_AUTOSTART, needsRestart=True, fnc=autostart)
		]
