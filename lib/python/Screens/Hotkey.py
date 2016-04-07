from Components.ActionMap import ActionMap, HelpableActionMap
from Components.Button import Button
from Components.ChoiceList import ChoiceList, ChoiceEntryComponent
from Components.SystemInfo import SystemInfo
from Components.config import config, ConfigSubsection, ConfigText, ConfigYesNo
from Components.PluginComponent import plugins
from Screens.ChannelSelection import SimpleChannelSelection
from Screens.ChoiceBox import ChoiceBox
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Plugins.Plugin import PluginDescriptor
from Tools.BoundFunction import boundFunction
from ServiceReference import ServiceReference
from enigma import eServiceReference, eActionMap
from Components.Label import Label
import os

updateversion = "07.04.2016"

def getHotkeys():
	return [(_("OK long"), "okbutton_long", "Infobar/openInfoBarEPG"),
	(_("Exit "), "exit", ""),
	(_("Exit long"), "exit_long", ""),
	(_("Left"), "cross_left", ""),
	(_("Right"), "cross_right", ""),
	(_("Up"), "cross_up", "Infobar/switchChannelUp"),
	(_("Down"), "cross_down", "Infobar/switchChannelDown"),
	(_("Red"), "red", "Infobar/activateRedButton"),
	(_("Red long"), "red_long", "Module/Screens.Hotkey/HotkeySetup"),
	(_("Green"), "green", "Infobar/subserviceSelection"),
	(_("Green long"), "green_long", "Infobar/subtitleSelection"),
	(_("Yellow"), "yellow", "Plugins/Extensions/EPGSearch/1"),
	(_("Yellow long"), "yellow_long", ""),
	(_("Blue"), "blue", "Infobar/showExtensionSelection"),
	(_("Blue long"), "blue_long", "Infobar/showPluginBrowser"),
	(_("Info (EPG)"), "info", "Infobar/openSingleServiceEPG"),
	(_("Info (EPG) long"), "info_long", "Infobar/showEventInfoPlugins"),
	(_("Epg/Guide"), "epg", "Infobar/openSingleServiceEPG"),
	(_("Epg/Guide long"), "epg_long", "Infobar/showEventInfoPlugins"),
	(_("F1"), "f1", "Plugins/Extensions/HDF-Toolbox/1"),
	(_("F1 long"), "f1_long", ""),
	(_("F2"), "f2", "Plugins/Extensions/MediaPortal/1"),
	(_("F2 long"), "f2_long", ""),
	(_("F3"), "f3", "Plugins/Extensions/EtPortal/1"),
	(_("F3 long"), "f3_long", ""),
	(_("F4"), "f4", "Plugins/Extensions/HDF-Toolbox/1"),
	(_("F4 long"), "f4_long", ""),
	(_("Audio"), "audio", "Infobar/audioSelection"),
	(_("Audio long"), "audio_long", ""),
	(_("Back "), "back", "Infobar/historyZap"),
	(_("Back long"), "back_long", "Plugins/Extensions/ZapHistoryBrowser/1"),
	(_("Channel up"), "channelup", "Infobar/zapUp"),
	(_("Channel down"), "channeldown", "Infobar/zapDown"),
	(_("Volume up"), "volumeUp", ""),
	(_("Volume down"), "volumeDown", ""),
	(_("Context"), "contextMenu", "Infobar/showExtensionSelection"),
	(_("Context long"), "context_long", "Infobar/showExtensionSelection"),
	(_("End"), "end", "Infobar/historyBack"),
	(_("End long"), "end_long", ""),
	(_("History"), "historyBack", ""),
	(_("History long"), "historyBack_long", ""),
	(_("Favorites"), "favor", "Infobar/openFavouritesList"),
	(_("Favorites long"), "favor_long", "Infobar/openSatellites"),
	(_("Fastforward"), "fastforward", ""),
	(_("File"), "file", "Plugins/Extensions/EnhancedMovieCenter/2"),
	(_("File long"), "file_long", "Infobar/showMovies"),
	(_("Help"), "helpshow", "Infobar/showHelp"),
	(_("Help long"), "helpshow_long", "Module/Screens.Hotkey/HotkeySetup"),
	(_("HDMI Rx"), "HDMIin", ""),
	(_("HDMI Rx long"), "HDMIin_long", ""),
	(_("Home"), "home", "Infobar/showMovies"),
	(_("Home long"), "home_long", ""),
	(_("Homepage/Portal"), "homepage", ""),
	(_("Homepage/Portal long"), "homepage_long", ""),
	(_("List/Fav/PVR"), "list", "Plugins/Extensions/EnhancedMovieCenter/2"),
	(_("List/Fav/PVR long"), "list_long", "Infobar/showMovies"),
	(_("Mark/Portal/Playlist"), "mark", "Plugins/Extensions/EtPortal/1"),
	(_("Mark/Portal/Playlist long"), "mark_long", ""),
	(_("Media"), "showMovies", "Plugins/Extensions/EnhancedMovieCenter/2"),
	(_("Media long"), "showMovies_long", "Infobar/showMovies"),
	(_("Menu"), "menu", "Infobar/mainMenu"),
	(_("Menu long"), "menu_long", "Module/Screens.ServiceInfo/ServiceInfo"),
	(_("Mute long"), "mute_long", "Infobar/audioSelection"),
	(_("Next"), "next", "Infobar/historyNext"),
	(_("Next long"), "next_long", ""),
	(_("Pause"), "pause", "Infobar/startTimeshift"),
	(_("Pause long"), "pause_long", "Infobar/startTimeshift"),
	(_("Play "), "play", "Infobar/startTimeshift"),
	(_("Play long"), "play_long", "Infobar/startTimeshift"),
	(_("Playlist"), "playlist", "Plugins/Extensions/EnhancedMovieCenter/2"),
	(_("Playlist long"), "playlist_long", "Infobar/showMovies"),
	(_("Picture in Picture"), "activatePiP", "Infobar/showPiP"),
	(_("Picture in Picture long"), "activatePiP_long", "Infobar/swapPiP"),
	(_("Plugin"), "mark", "Infobar/showMovies"),
	(_("Prov/Fav"), "ab", "Infobar/openFavouritesList"),
	(_("Prov/Fav long"), "ab_long", ""),
	(_("Power (use button menu)"), "powerstandby", ""),
	(_("Power long (use button menu)"), "powerstandby_long", ""),
	(_("Previous"), "previous", "Infobar/historyBack"),
	(_("Previous long"), "previous_long", ""),
	(_("Radio"), "radio", "Infobar/showRadio"),
	(_("Radio long"), "radio_long", "Plugins/Extensions/webradioFS/1"),
	(_("Record"), "rec", "Infobar/instantRecord"),
	(_("Record long"), "rec_long", "Infobar/startInstantRecording"),
	(_("Rewind"), "rewind", ""),
	(_("Sat "), "sat", "Infobar/openSatellites"),
	(_("Sat long"), "sat_long", ""),
	(_("Search/WEB"), "search", ""),
	(_("Search/WEB long"), "search_long", ""),
	(_("Slow "), "slow", ""),
	(_("Slow long"), "slow_long", ""),
	(_("Sleep"), "sleep", "Module/Screens.PowerTimerEdit/PowerTimerEditList"),
	(_("Sleep long"), "sleep_long", ""),
	(_("Skip back"), "skip_back", ""),
	(_("Skip forward"), "skip_forward", ""),
	(_("Stop "), "stop", "Infobar/stopTimeshift"),
	(_("Stop long"), "stop_long", "Infobar/stopTimeshift"),
	(_("Subtitle"), "subtitle", "Infobar/subtitleSelection"),
	(_("Subtitle long"), "subtitle_long", "Infobar/subserviceSelection"),
	(_("Teletext"), "texter", "Infobar/startTeletext"),
	(_("Teletext long"), "texter_long", ""),
	(_("Timer"), "timer", "Module/Screens.TimerEdit/TimerEditList"),
	(_("Timer long"), "timer_long", "Module/Screens.PowerTimerEdit/PowerTimerEditList"),
	(_("Timeshift"), "timeshift", "Infobar/startTimeshift"),
	(_("Timeshift long"), "timeshift_long", "Infobar/stopTimeshift"),
	(_("TV"), "showTv", "Infobar/showTv"),
	(_("TV long"), "showTv_long", ""),
	(_("UHF/Slow"), "slow", ""),
	(_("UHF/Slow long"), "slow_long", ""),
	(_("V-Key"), "vkey", "Plugins/Extensions/EnhancedMovieCenter/2"),
	(_("V-Key long"), "vkey_long", "Infobar/showMovies"),
	(_("Y-Tube/WWW"), "www", ""),
	(_("Y-Tube/WWW long"), "www_long", ""),
	(_("Directory "), "directory", ""),
	(_("Directory long"), "directory_long", ""),
	(_("Zoom"), "ZoomInOut", "InfobarGenerics/ZoomInOut"),]

config.misc.hotkey = ConfigSubsection()
config.misc.hotkey.additional_keys = ConfigYesNo(default=True)
for x in getHotkeys():
	exec "config.misc.hotkey." + x[1] + " = ConfigText(default='" + x[2] + "')"

def getHotkeyFunctions():
	hotkeyFunctions = []
	twinPlugins = []
	twinPaths = {}
	pluginlist = plugins.getPlugins(PluginDescriptor.WHERE_EVENTINFO)
	pluginlist.sort(key=lambda p: p.name)
	for plugin in pluginlist:
		if plugin.name not in twinPlugins and plugin.path and 'selectedevent' not in plugin.__call__.func_code.co_varnames:
			if twinPaths.has_key(plugin.path[24:]):
				twinPaths[plugin.path[24:]] += 1
			else:
				twinPaths[plugin.path[24:]] = 1
			hotkeyFunctions.append((plugin.name, plugin.path[24:] + "/" + str(twinPaths[plugin.path[24:]]) , "EPG"))
			twinPlugins.append(plugin.name)
	pluginlist = plugins.getPlugins([PluginDescriptor.WHERE_PLUGINMENU, PluginDescriptor.WHERE_EXTENSIONSMENU, PluginDescriptor.WHERE_EVENTINFO])
	pluginlist.sort(key=lambda p: p.name)
	for plugin in pluginlist:
		if plugin.name not in twinPlugins and plugin.path:
			if twinPaths.has_key(plugin.path[24:]):
				twinPaths[plugin.path[24:]] += 1
			else:
				twinPaths[plugin.path[24:]] = 1
			hotkeyFunctions.append((plugin.name, plugin.path[24:] + "/" + str(twinPaths[plugin.path[24:]]) , "Plugins"))
			twinPlugins.append(plugin.name)
	hotkeyFunctions.append((_("Show Graphical Multi EPG"), "Infobar/openGraphEPG", "EPG"))
	hotkeyFunctions.append((_("Show Event View"), "Infobar/openEventView", "EPG"))
	#hotkeyFunctions.append((_("Show Event Info"), "Infobar/showEventInfo", "EPG"))
	hotkeyFunctions.append((_("Show Event Info Plugins"), "Infobar/showEventInfoPlugins", "EPG"))
	hotkeyFunctions.append((_("Show Single Service EPG"), "Infobar/openSingleServiceEPG", "EPG"))
	hotkeyFunctions.append((_("Show Multi Service EPG"), "Infobar/openMultiServiceEPG", "EPG"))
	hotkeyFunctions.append((_("Show Infobar EPG"), "Infobar/openInfoBarEPG", "EPG"))
	hotkeyFunctions.append((_("Main Menu"), "Infobar/mainMenu", "InfoBar"))
	hotkeyFunctions.append((_("Show Help"), "Infobar/showHelp", "InfoBar"))
	hotkeyFunctions.append((_("Toggle Infobar/SecondInfobar"), "Infobar/toggleShow", "InfoBar"))
	hotkeyFunctions.append((_("Show First Infobar"), "Infobar/showFirstInfoBar", "InfoBar"))
	hotkeyFunctions.append((_("Show Second Infobar"), "Infobar/showSecondInfoBar", "InfoBar"))
	hotkeyFunctions.append((_("Show Extension Selection"), "Infobar/showExtensionSelection", "InfoBar"))
	hotkeyFunctions.append((_("Show Plugin Selection"), "Infobar/showPluginBrowser", "InfoBar"))
	hotkeyFunctions.append((_("Zap down"), "Infobar/zapDown", "InfoBar"))
	hotkeyFunctions.append((_("Zap up"), "Infobar/zapUp", "InfoBar"))
	hotkeyFunctions.append((_("BackZap [0]"), "Infobar/BackZap", "InfoBar"))
	hotkeyFunctions.append((_("Volume down"), "Infobar/volumeDown", "InfoBar"))
	hotkeyFunctions.append((_("Volume up"), "Infobar/volumeUp", "InfoBar"))
	hotkeyFunctions.append((_("Switch Channel up in Infobar"), "Infobar/switchChannelUp", "InfoBar"))
	hotkeyFunctions.append((_("Switch Channel down in Infobar"), "Infobar/switchChannelDown", "InfoBar"))
	hotkeyFunctions.append((_("Show Service List"), "Infobar/openServiceList", "InfoBar"))
	hotkeyFunctions.append((_("History Zap Menu +"), "Infobar/historyZapForward", "InfoBar"))
	hotkeyFunctions.append((_("History Zap Menu -"), "Infobar/historyZapBackward", "InfoBar"))
	hotkeyFunctions.append((_("History back"), "Infobar/historyBack", "InfoBar"))
	hotkeyFunctions.append((_("History next"), "Infobar/historyNext", "InfoBar"))
	hotkeyFunctions.append((_("Show Audioselection"), "Infobar/audioSelection", "InfoBar"))
	hotkeyFunctions.append((_("Switch to Radio Mode"), "Infobar/showRadio", "InfoBar"))
	hotkeyFunctions.append((_("Switch to TV Mode"), "Infobar/showTv", "InfoBar"))
	hotkeyFunctions.append((_("Show Favourites List"), "Infobar/openFavouritesList", "InfoBar"))
	hotkeyFunctions.append((_("Show Satellites List"), "Infobar/openSatellites", "InfoBar"))
	hotkeyFunctions.append((_("Show Movies"), "Infobar/showMovies", "InfoBar"))
	hotkeyFunctions.append((_("Instant Record"), "Infobar/instantRecord", "InfoBar"))
	hotkeyFunctions.append((_("Start instant recording"), "Infobar/startInstantRecording", "InfoBar"))
	#hotkeyFunctions.append((_("Activate timeshift End"), "Infobar/activateTimeshiftEnd", "InfoBar"))
	#hotkeyFunctions.append((_("Activate timeshift end and pause"), "Infobar/activateTimeshiftEndAndPause", "InfoBar"))
	hotkeyFunctions.append((_("Start Timeshift"), "Infobar/startTimeshift", "InfoBar"))
	hotkeyFunctions.append((_("Stop Timeshift"), "Infobar/stopTimeshift", "InfoBar"))
	hotkeyFunctions.append((_("Start Teletext"), "Infobar/startTeletext", "InfoBar"))
	hotkeyFunctions.append((_("Show Subservice Selection"), "Infobar/subserviceSelection", "InfoBar"))
	hotkeyFunctions.append((_("Show Subtitle Selection"), "Infobar/subtitleSelection", "InfoBar"))
	hotkeyFunctions.append((_("Letterbox Zoom"), "Infobar/vmodeSelection", "InfoBar"))
	hotkeyFunctions.append((_("ZoomInOut"), "InfobarGenerics/ZoomInOut", "InfoBar"))
	hotkeyFunctions.append((_("ZoomOff"), "InfobarGenerics/ZoomInOut", "InfoBar"))
	hotkeyFunctions.append((_("Do nothing"), "Void", "InfoBar"))
	if SystemInfo["PIPAvailable"]:
		hotkeyFunctions.append((_("Show Picture In Picture"), "Infobar/showPiP", "InfoBar"))
		hotkeyFunctions.append((_("Swap Picture In Picture"), "Infobar/swapPiP", "InfoBar"))
		hotkeyFunctions.append((_("Move Picture In Picture"), "Infobar/movePiP", "InfoBar"))
		hotkeyFunctions.append((_("Toggle Picture In Picture Zap"), "Infobar/togglePipzap", "InfoBar"))
	hotkeyFunctions.append((_("Activate HbbTV (Redbutton)"), "Infobar/activateRedButton", "InfoBar"))		
	hotkeyFunctions.append((_("Toggle HDMI-In Full Screen"), "Infobar/HDMIInFull", "InfoBar"))
	hotkeyFunctions.append((_("Toggle HDMI-In Picture In Picture"), "Infobar/HDMIInPiP", "InfoBar"))
	hotkeyFunctions.append((_("HotKey Setup"), "Module/Screens.Hotkey/HotkeySetup", "Setup"))
	hotkeyFunctions.append((_("Software Update"), "Module/Screens.SoftwareUpdate/UpdatePlugin", "Setup"))
	hotkeyFunctions.append((_("CI (Common Interface) Setup"), "Module/Screens.Ci/CiSelection", "Setup"))
	hotkeyFunctions.append((_("Tuner Configuration"), "Module/Screens.Satconfig/NimSelection", "Scanning"))
	hotkeyFunctions.append((_("Manual Scan"), "Module/Screens.ScanSetup/ScanSetup", "Scanning"))
	hotkeyFunctions.append((_("Automatic Scan"), "Module/Screens.ScanSetup/ScanSimple", "Scanning"))
	for plugin in plugins.getPluginsForMenu("scan"):
		hotkeyFunctions.append((plugin[0], "MenuPlugin/scan/" + plugin[2], "Scanning"))
	hotkeyFunctions.append((_("Network Adapter"), "Module/Screens.NetworkSetup/NetworkAdapterSelection", "Setup"))
	hotkeyFunctions.append((_("Network Menu"), "Infobar/showNetworkMounts", "Setup"))
	hotkeyFunctions.append((_("Plugin Browser"), "Module/Screens.PluginBrowser/PluginBrowser", "Setup"))
	hotkeyFunctions.append((_("Channel Info"), "Module/Screens.ServiceInfo/ServiceInfo", "Setup"))
	hotkeyFunctions.append((_("Timer"), "Module/Screens.TimerEdit/TimerEditList", "Setup"))
	hotkeyFunctions.append((_("PowerTimer"), "Module/Screens.PowerTimerEdit/PowerTimerEditList", "Setup"))
	hotkeyFunctions.append((_("Open AutoTimer"), "Infobar/showAutoTimerList", "Setup"))
	hotkeyFunctions.append((_("Memory Info"), "Module/Screens.About/MemoryInfo", "Setup"))
	for plugin in plugins.getPluginsForMenu("system"):
		if plugin[2]:
			hotkeyFunctions.append((plugin[0], "MenuPlugin/system/" + plugin[2], "Setup"))
	hotkeyFunctions.append((_("Standby"), "Module/Screens.Standby/Standby", "Power"))
	hotkeyFunctions.append((_("Restart"), "Module/Screens.Standby/TryQuitMainloop/2", "Power"))
	hotkeyFunctions.append((_("Restart Enigma"), "Module/Screens.Standby/TryQuitMainloop/3", "Power"))
	hotkeyFunctions.append((_("Deep-Standby"), "Module/Screens.Standby/TryQuitMainloop/1", "Power"))
	hotkeyFunctions.append((_("SleepTimer"), "Module/Screens.SleepTimerEdit/SleepTimerEdit", "Power"))
	hotkeyFunctions.append((_("Usage Setup"), "Setup/usage", "Setup"))
	hotkeyFunctions.append((_("User Interface"), "Setup/userinterface", "Setup"))
	hotkeyFunctions.append((_("Recording Setup"), "Setup/recording", "Setup"))
	hotkeyFunctions.append((_("Harddisk Setup"), "Setup/harddisk", "Setup"))
	hotkeyFunctions.append((_("Device Manager"), "DeviceManager", "Setup"))
	hotkeyFunctions.append((_("Subtitles Settings"), "Setup/subtitlesetup", "Setup"))
	hotkeyFunctions.append((_("Language"), "Module/Screens.LanguageSelection/LanguageSelection", "Setup"))
	hotkeyFunctions.append((_("Skin setup"), "Module/Screens.SkinSelector/SkinSelector", "Setup"))
	if os.path.isfile("/usr/lib/enigma2/python/Plugins/Extensions/Kodi/plugin.pyo"):
		hotkeyFunctions.append((_("Kodi Media Center"), "Kodi/", "Plugins"))
	if os.path.isdir("/etc/ppanel"):
		for x in [x for x in os.listdir("/etc/ppanel") if x.endswith(".xml")]:
			x = x[:-4]
			hotkeyFunctions.append((_("PPanel") + " " + x, "PPanel/" + x, "PPanels"))
	if os.path.isdir("/usr/scripts"):
		for x in [x for x in os.listdir("/usr/scripts") if x.endswith(".sh")]:
			x = x[:-3]
			hotkeyFunctions.append((_("Shellscript") + " " + x, "Shellscript/" + x, "Shellscripts"))
	return hotkeyFunctions

class HotkeySetup(Screen):
	def __init__(self, session, args=None):
		Screen.__init__(self, session)
		self['description'] = Label(_('Click on your remote on the button you want to change, then click on OK'))
		self.session = session
		self.setTitle(_("Hotkey Setup") + " - Version " + updateversion)
		self["key_red"] = Button(_("Exit"))
		self["key_green"] = Button(_("Toggle Extra Keys"))		
		self.list = []
		self.hotkeys = getHotkeys()
		self.hotkeyFunctions = getHotkeyFunctions()
		for x in self.hotkeys:
			self.list.append(ChoiceEntryComponent('',(x[0], x[1])))
		self["list"] = ChoiceList(list=self.list[:config.misc.hotkey.additional_keys.value and len(self.hotkeys) or 16], selection = 0)
		self["choosen"] = ChoiceList(list=[])
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "DirectionActions"],
		{
			"ok": self.keyOk,
			"cancel": self.close,
			"red": self.close,
			"green": self.toggleAdditionalKeys,
			"up": self.keyUp,
			"down": self.keyDown,
			"left": self.keyLeft,
			"right": self.keyRight,
		}, -1)
		self["HotkeyButtonActions"] = hotkeyActionMap(["HotkeyActions"], dict((x[1], self.hotkeyGlobal) for x in self.hotkeys))
		self.longkeyPressed = False
		self.onLayoutFinish.append(self.__layoutFinished)
		self.onExecBegin.append(self.getFunctions)

	def __layoutFinished(self):
		self["choosen"].selectionEnabled(0)

	def hotkeyGlobal(self, key):
		if self.longkeyPressed:
			self.longkeyPressed = False
		else:
			index = 0
			for x in self.list[:config.misc.hotkey.additional_keys.value and len(self.hotkeys) or 16]:
				if key == x[0][1]:
					self["list"].moveToIndex(index)
					if key.endswith("_long"):
						self.longkeyPressed = True
					break
				index += 1
			self.getFunctions()

	def keyOk(self):
		self.session.open(HotkeySetupSelect, self["list"].l.getCurrentSelection())

	def keyLeft(self):
		self["list"].instance.moveSelection(self["list"].instance.pageUp)
		self.getFunctions()

	def keyRight(self):
		self["list"].instance.moveSelection(self["list"].instance.pageDown)
		self.getFunctions()

	def keyUp(self):
		self["list"].instance.moveSelection(self["list"].instance.moveUp)
		self.getFunctions()

	def keyDown(self):
		self["list"].instance.moveSelection(self["list"].instance.moveDown)
		self.getFunctions()

	def toggleAdditionalKeys(self):
		config.misc.hotkey.additional_keys.value = not config.misc.hotkey.additional_keys.value
		config.misc.hotkey.additional_keys.save()
		self["list"].setList(self.list[:config.misc.hotkey.additional_keys.value and len(self.hotkeys) or 16])

	def getFunctions(self):
		key = self["list"].l.getCurrentSelection()[0][1]
		if key:
			selected = []
			for x in eval("config.misc.hotkey." + key + ".value.split(',')"):
				if x.startswith("ZapPanic"):
					selected.append(ChoiceEntryComponent('',((_("Panic to") + " " + ServiceReference(eServiceReference(x.split("/", 1)[1]).toString()).getServiceName()), x)))
				elif x.startswith("Zap"):
					selected.append(ChoiceEntryComponent('',((_("Zap to") + " " + ServiceReference(eServiceReference(x.split("/", 1)[1]).toString()).getServiceName()), x)))
				else:
					function = list(function for function in self.hotkeyFunctions if function[1] == x )
					if function:
						selected.append(ChoiceEntryComponent('',((function[0][0]), function[0][1])))
			self["choosen"].setList(selected)

class HotkeySetupSelect(Screen):
	def __init__(self, session, key, args=None):
		Screen.__init__(self, session)
		self['description'] = Label(_('Select the desired function and click on OK to assign it. Use CH+/- to toggle between the lists. Select an assigned function and click on OK to de-assign it.'))
		self.skinName="ButtonSetupSelect"
		self.session = session
		self.key = key
		self.setTitle(_("Hotkey Setup") + " " + key[0][0])
		self["key_red"] = Button(_("Cancel"))
		self["key_green"] = Button(_("Save"))
		self.mode = "list"
		self.hotkeyFunctions = getHotkeyFunctions()
		self.config = eval("config.misc.hotkey." + key[0][1])
		self.expanded = []
		self.selected = []
		for x in self.config.value.split(','):
			if x.startswith("ZapPanic"):
				self.selected.append(ChoiceEntryComponent('',((_("Panic to") + " " + ServiceReference(eServiceReference(x.split("/", 1)[1]).toString()).getServiceName()), x)))
			elif x.startswith("Zap"):
				self.selected.append(ChoiceEntryComponent('',((_("Zap to") + " " + ServiceReference(eServiceReference(x.split("/", 1)[1]).toString()).getServiceName()), x)))
			else:
				function = list(function for function in self.hotkeyFunctions if function[1] == x )
				if function:
					self.selected.append(ChoiceEntryComponent('',((function[0][0]), function[0][1])))
		self.prevselected = self.selected[:]
		self["choosen"] = ChoiceList(list=self.selected, selection=0)
		self["list"] = ChoiceList(list=self.getFunctionList(), selection=0)
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "DirectionActions", "KeyboardInputActions"], 
		{
			"ok": self.keyOk,
			"cancel": self.cancel,
			"red": self.cancel,
			"green": self.save,
			"up": self.keyUp,
			"down": self.keyDown,
			"left": self.keyLeft,
			"right": self.keyRight,
			"upRepeated": self.keyUp,
			"downRepeated": self.keyDown,
			"leftRepeated": self.keyLeft,
			"rightRepeated": self.keyRight,
			"pageUp": self.toggleMode,
			"pageDown": self.toggleMode,
			"moveUp": self.moveUp,
			"moveDown": self.moveDown
		}, -1)
		self.onLayoutFinish.append(self.__layoutFinished)

	def __layoutFinished(self):
		self["choosen"].selectionEnabled(0)

	def getFunctionList(self):
		functionslist = []
		catagories = {}
		for function in self.hotkeyFunctions:
			if not catagories.has_key(function[2]):
				catagories[function[2]] = []
			catagories[function[2]].append(function)
		for catagorie in sorted(list(catagories)):
			if catagorie in self.expanded:
				functionslist.append(ChoiceEntryComponent('expanded',((catagorie), "Expander")))
				for function in catagories[catagorie]:
					functionslist.append(ChoiceEntryComponent('verticalline',((function[0]), function[1])))
				if catagorie == "InfoBar":
					functionslist.append(ChoiceEntryComponent('verticalline',((_("Zap to")), "Zap")))
					functionslist.append(ChoiceEntryComponent('verticalline',((_("Panic to")), "ZapPanic")))
			else:
				functionslist.append(ChoiceEntryComponent('expandable',((catagorie), "Expander")))
		return functionslist

	def toggleMode(self):
		if self.mode == "list" and self.selected:
			self.mode = "choosen"
			self["choosen"].selectionEnabled(1)
			self["list"].selectionEnabled(0)
		elif self.mode == "choosen":
			self.mode = "list"
			self["choosen"].selectionEnabled(0)
			self["list"].selectionEnabled(1)

	def keyOk(self):
		if self.mode == "list":
			currentSelected = self["list"].l.getCurrentSelection()
			if currentSelected[0][1] == "Expander":
				if currentSelected[0][0] in self.expanded:
					self.expanded.remove(currentSelected[0][0])
				else:
					self.expanded.append(currentSelected[0][0])
				self["list"].setList(self.getFunctionList())
			else:
				if currentSelected[:2] in self.selected:
					self.selected.remove(currentSelected[:2])
				else:
					if currentSelected[0][1].startswith("ZapPanic"):
						self.session.openWithCallback(self.zaptoCallback, SimpleChannelSelection, _("Hotkey Panic") + " " + self.key[0][0], currentBouquet=True)
					elif currentSelected[0][1].startswith("Zap"):
						self.session.openWithCallback(self.zaptoCallback, SimpleChannelSelection, _("Hotkey zap") + " " + self.key[0][0], currentBouquet=True)
					else:
						self.selected.append(currentSelected[:2])
		elif self.selected:
			self.selected.remove(self["choosen"].l.getCurrentSelection())
			if not self.selected:
				self.toggleMode()
		self["choosen"].setList(self.selected)

	def zaptoCallback(self, *args):
		if args:
			currentSelected = self["list"].l.getCurrentSelection()[:]
			currentSelected[1]=currentSelected[1][:-1] + (currentSelected[0][0] + " " + ServiceReference(args[0]).getServiceName(),)
			self.selected.append([(currentSelected[0][0], currentSelected[0][1] + "/" + args[0].toString()), currentSelected[1]])

	def keyLeft(self):
		self[self.mode].instance.moveSelection(self[self.mode].instance.pageUp)

	def keyRight(self):
		self[self.mode].instance.moveSelection(self[self.mode].instance.pageDown)

	def keyUp(self):
		self[self.mode].instance.moveSelection(self[self.mode].instance.moveUp)

	def keyDown(self):
		self[self.mode].instance.moveSelection(self[self.mode].instance.moveDown)

	def moveUp(self):
		self.moveChoosen(self.keyUp)

	def moveDown(self):
		self.moveChoosen(self.keyDown)

	def moveChoosen(self, direction):
		if self.mode == "choosen":
			currentIndex = self["choosen"].getSelectionIndex()
			swapIndex = (currentIndex + (direction == self.keyDown and 1 or -1)) % len(self["choosen"].list)
			self["choosen"].list[currentIndex], self["choosen"].list[swapIndex] = self["choosen"].list[swapIndex], self["choosen"].list[currentIndex]
			self["choosen"].setList(self["choosen"].list)
			direction()
		else:
			return 0

	def save(self):
		configValue = []
		for x in self.selected:
			configValue.append(x[0][1])
		self.config.value = ",".join(configValue)
		self.config.save()
		self.close()

	def cancel(self):
		if self.selected != self.prevselected:
			self.session.openWithCallback(self.cancelCallback, MessageBox, _("are you sure to cancel all changes"), default=False)
		else:
			self.close()

	def cancelCallback(self, answer):
		answer and self.close()

class hotkeyActionMap(ActionMap):
	def action(self, contexts, action):
		if (action in tuple(x[1] for x in getHotkeys()) and self.actions.has_key(action)):
			res = self.actions[action](action)
			if res is not None:
				return res
			return 1
		else:
			return ActionMap.action(self, contexts, action)

class helpableHotkeyActionMap(HelpableActionMap):
	def action(self, contexts, action):
		if (action in tuple(x[1] for x in getHotkeys()) and self.actions.has_key(action)):
			res = self.actions[action](action)
			if res is not None:
				return res
			return 1
		else:
			return ActionMap.action(self, contexts, action)

class InfoBarHotkey():
	def __init__(self):
		self.hotkeys = getHotkeys()
		self["HotkeyButtonActions"] = helpableHotkeyActionMap(self, "HotkeyActions",
			dict((x[1],(self.hotkeyGlobal, boundFunction(self.getHelpText, x[1]))) for x in self.hotkeys), -10)
		self.onExecBegin.append(self.clearLongkeyPressed)

	def clearLongkeyPressed(self):
		self.longkeyPressed = False

	def getKeyFunctions(self, key):
		if key in ("play", "playpause", "Stop", "stop", "pause", "rewind", "next", "previous", "fastforward", "skip_back", "skip_forward") and (self.__class__.__name__ == "MoviePlayer" or hasattr(self, "timeshiftActivated") and self.timeshiftActivated()):
			return False
		selection = eval("config.misc.hotkey." + key + ".value.split(',')")
		selected = []
		for x in selection:
			if x.startswith("ZapPanic"):
				selected.append(((_("Panic to") + " " + ServiceReference(eServiceReference(x.split("/", 1)[1]).toString()).getServiceName()), x))
			elif x.startswith("Zap"):
				selected.append(((_("Zap to") + " " + ServiceReference(eServiceReference(x.split("/", 1)[1]).toString()).getServiceName()), x))
			else:
				function = list(function for function in getHotkeyFunctions() if function[1] == x )
				if function:
					selected.append(function[0])
		return selected

	def getHelpText(self, key):
		selected = self.getKeyFunctions(key)
		if not selected:
			return
		if len(selected) == 1:
			return selected[0][0]
		else:
			return _("Hotkey") + " " + tuple(x[0] for x in self.hotkeys if x[1] == key)[0]

	def hotkeyGlobal(self, key):
		if self.longkeyPressed:
			self.longkeyPressed = False
		else:
			selected = self.getKeyFunctions(key)
			if not selected:
				return 0
			elif len(selected) == 1:
				self.longkeyPressed = key.endswith("_long") and (selected[0][1].startswith("Infobar") or selected[0][1].startswith("Zap"))
				return self.execHotkey(selected[0])
			else:
				key = tuple(x[0] for x in self.hotkeys if x[1] == key)[0]
				self.session.openWithCallback(self.execHotkey, ChoiceBox, _("Hotkey") + " " + key, selected)

	def execHotkey(self, selected):
		if selected:
			selected = selected[1].split("/")
			if selected[0] == "Plugins":
				twinPlugins = []
				twinPaths = {}
				pluginlist = plugins.getPlugins(PluginDescriptor.WHERE_EVENTINFO)
				pluginlist.sort(key=lambda p: p.name)
				for plugin in pluginlist:
					if plugin.name not in twinPlugins and plugin.path and 'selectedevent' not in plugin.__call__.func_code.co_varnames:
						if twinPaths.has_key(plugin.path[24:]):
							twinPaths[plugin.path[24:]] += 1
						else:
							twinPaths[plugin.path[24:]] = 1
						if plugin.path[24:] + "/" + str(twinPaths[plugin.path[24:]])== "/".join(selected):
							self.runPlugin(plugin)
							return
						twinPlugins.append(plugin.name)
				pluginlist = plugins.getPlugins([PluginDescriptor.WHERE_PLUGINMENU, PluginDescriptor.WHERE_EXTENSIONSMENU])
				pluginlist.sort(key=lambda p: p.name)
				for plugin in pluginlist:
					if plugin.name not in twinPlugins and plugin.path:
						if twinPaths.has_key(plugin.path[24:]):
							twinPaths[plugin.path[24:]] += 1
						else:
							twinPaths[plugin.path[24:]] = 1
						if plugin.path[24:] + "/" + str(twinPaths[plugin.path[24:]])== "/".join(selected):
							self.runPlugin(plugin)
							return
						twinPlugins.append(plugin.name)
			elif selected[0] == "MenuPlugin":
				for plugin in plugins.getPluginsForMenu(selected[1]):
					if plugin[2] == selected[2]:
						self.runPlugin(plugin[1])
						return
			elif selected[0] == "Infobar":
				if hasattr(self, selected[1]):
					exec "self." + ".".join(selected[1:]) + "()"
				else:
					return 0
			elif selected[0] == "Module":
				try:
					exec "from " + selected[1] + " import *"
					exec "self.session.open(" + ",".join(selected[2:]) + ")"
				except:
					print "[Hotkey] error during executing module %s, screen %s" % (selected[1], selected[2])
			elif selected[0] == "Setup":
				exec "from Screens.Setup import *"
				exec "self.session.open(Setup, \"" + selected[1] + "\")"
			elif selected[0].startswith("Zap"):
				if selected[0] == "ZapPanic":
					self.servicelist.history = []
				self.servicelist.servicelist.setCurrent(eServiceReference("/".join(selected[1:])))
				self.servicelist.zap(enable_pipzap = True)
				if hasattr(self, "lastservice"):
					self.lastservice = eServiceReference("/".join(selected[1:]))
					self.close()
				else:
					self.show()
			elif selected[0] == "PPanel":
				ppanelFileName = '/etc/ppanels/' + selected[1] + ".xml"
				if os.path.isfile(ppanelFileName) and os.path.isdir('/usr/lib/enigma2/python/Plugins/Extensions/PPanel'):
					from Plugins.Extensions.PPanel.ppanel import PPanel
					self.session.open(PPanel, name=selected[1] + ' PPanel', node=None, filename=ppanelFileName, deletenode=None)
			elif selected[0] == "Shellscript":
				command = '/usr/scripts/' + selected[1] + ".sh"
				if os.path.isfile(command) and os.path.isdir('/usr/lib/enigma2/python/Plugins/Extensions/PPanel'):
					from Plugins.Extensions.PPanel.ppanel import Execute
					self.session.open(Execute, selected[1] + " shellscript", None, command)
			elif selected[0] == "EMC":
				try:
					from Plugins.Extensions.EnhancedMovieCenter.plugin import showMoviesNew
					from Screens.InfoBar import InfoBar
					open(showMoviesNew(InfoBar.instance))
				except Exception as e:
					print('[EMCPlayer] showMovies exception:\n' + str(e))
			elif selected[0] == "Kodi":
				if os.path.isfile("/usr/lib/enigma2/python/Plugins/Extensions/Kodi/plugin.pyo"):
					from Plugins.Extensions.Kodi.plugin import KodiMainScreen
					self.session.open(KodiMainScreen)
			elif selected[0] == "DeviceManager":
				from Plugins.SystemPlugins.DeviceManager.HddSetup import *
				self.session.open(HddSetup)
