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
from boxbranding import getBoxType, getMachineName
from enigma import eServiceReference
from Components.Label import Label

boxtype = getBoxType()

hotkeys = [(_("Red"), "red", "Infobar/activateRedButton"),
	(_("Red long"), "red_long", "Module/Screens.Hotkey/HotkeySetup"),
	(_("Green"), "green", "Infobar/subserviceSelection"),
	(_("Green long"), "green_long", "Infobar/subtitleSelection"),
	(_("Yellow"), "yellow", ""),
	(_("Yellow long"), "yellow_long", ""),
	(_("Blue"), "blue", "Infobar/showExtensionSelection"),
	(_("Blue long"), "blue_long", "Infobar/showPluginBrowser"),
	(_("Info (EPG)"), "info", "Infobar/openSingleServiceEPG"),
	(_("Info (EPG) Long"), "info_long", "Infobar/showEventInfoPlugins"),
	(_("Epg/Guide"), "epg", "Plugins/Extensions/CoolTVGuide/5"),
	(_("Epg/Guide long"), "epg_long", "Plugins/Extensions/CoolTVGuide/4"),
	(_("List/Fav/PVR"), "list", "Infobar/showMovies"),
	(_("List/Fav/PVR long"), "list_long", ""),
	(_("OK"), "ok", "Infobar/toggleShow"),
	(_("OK long"), "ok_long", "Infobar/openInfoBarEPG"),
	(_("Exit"), "exit", ""),
	(_("Exit long"), "exit_long", ""),
	(_("File"), "file", "Infobar/showMovies"),
	(_("File long"), "file_long", "Plugins/Extensions/simplelist/1"),
	(_("Media"), "showMovies", ""),
	(_("Media long"), "showMovies_long", ""),
	(_("Left"), "cross_left", ""),
	(_("Right"), "cross_right", ""),
	(_("Up"), "cross_up", ""),
	(_("Down"), "cross_down", ""),
	(_("Channel up"), "channelup", ""),
	(_("Channel down"), "channeldown", ""),
	(_("TV"), "showTv", ""),
	(_("TV long"), "showTv_long", ""),
	(_("Radio"), "radio", ""),
	(_("Radio long"), "radio_long", "Plugins/Extensions/webradioFS/1"),
	(_("Record"), "rec", "Infobar/instantRecord"),
	(_("Record long"), "rec_long", "Infobar/startInstantRecording"),
	(_("Teletext"), "text", "Infobar/startTeletext"),
	(_("Teletext long"), "text_long", ""),
	(_("Help"), "displayHelp", "Infobar/showHelp"),
	(_("Help long"), "displayHelp_long", "Module/Screens.Hotkey/HotkeySetup"),
	(_("Subtitle"), "subtitle", "Infobar/subtitleSelection"),
	(_("Subtitle long"), "subtitle_long", "Infobar/subserviceSelection"),
	(_("Menu"), "menu", "Infobar/mainMenu"),
	(_("Menu long"), "menu_long", "Module/Screens.ServiceInfo/ServiceInfo"),
	(_("Back"), "back", "Plugins/Extensions/ZapHistoryBrowser/1"),
	(_("Back long"), "back_long", "Plugins/Extensions/VirtualZap/1"),
	(_("Home"), "home", ""),
	(_("Home long"), "home_long", ""),
	(_("End"), "end", ""),
	(_("End long"), "end_long", ""),
	(_("Next"), "next", "Infobar/historyNext"),
	(_("Next long"), "next_long", ""),
	(_("Previous"), "previous", "Infobar/historyBack"),
	(_("Previous long"), "previous_long", ""),
	(_("Audio"), "audio", "Infobar/audioSelection"),
	(_("Audio long"), "audio_long", ""),
	(_("Mute long"), "mute_long", ""),
	(_("Play"), "play", ""),
	(_("Play long"), "play_long", ""),
	(_("Stop"), "stop", ""),
	(_("Stop long"), "stop_long", ""),
	(_("Pause"), "pause", ""),
	(_("Rewind"), "rewind", ""),
	(_("Fastforward"), "fastforward", ""),
	(_("Skip back"), "skip_back", ""),
	(_("Skip forward"), "skip_forward", ""),
	(_("Picture in Picture"), "activatePiP", "Infobar/showPiP"),
	(_("Picture in Picture long"), "activatePiP_long", "Infobar/swapPiP"),
	(_("Timer"), "timer", "Module/Screens.TimerEdit/TimerEditList"),
	(_("Timer long"), "timer_long", "Module/Screens.PowerTimerEdit/PowerTimerEditList"),
	(_("Playlist"), "playlist", ""),
	(_("Playlist long"), "playlist_long", ""),
	(_("Timeshift"), "timeshift", "Infobar/startTimeshift"),
	(_("Timeshift long"), "timeshift_long", "Infobar/stopTimeshift"),
	(_("Search/WEB"), "search", ""),
	(_("Search/WEB long"), "search_long", ""),
	(_("Slow"), "slow", ""),
	(_("Slow long"), "slow_long", ""),
	(_("Mark/Portal/Playlist"), "mark", "Plugins/Extensions/EtPortal/1"),
	(_("Mark/Portal/Playlist long"), "mark_long", ""),
	(_("Sleep"), "sleep", ""),
	(_("Sleep long"), "sleep_long", ""),
	(_("Power"), "power", "Module/Screens.Standby/Standby"),
	(_("Power long"), "power_long", "Module/Screens.Standby/TryQuitMainloop/1"),
	(_("Power down"), "power_down", "")]

## add or remove some functions for individual boxtype from hotkeys list
## hotkeys.append((_("HDMI Rx"), "HDMIin", ""))
## hotkeys.remove((_("F1/LAN long"), "f1_long", ""))

if boxtype == "et10000" or boxtype == "et8500" or boxtype == "et8000":
	hotkeys.append((_("additional keys for ET10000, ET8500, ET8000"), "empty", ""))
	hotkeys.append((_("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"),"empty", ""))
	hotkeys.append((_("HDMI Rx"), "HDMIin", ""))
	hotkeys.append((_("HDMI Rx long"), "HDMIin_long", ""))
	hotkeys.append((_("V-Key"), "vmodeSelection", ""))
	hotkeys.append((_("V-Key long"), "vmodeSelection_long", ""))
	hotkeys.append((_("F1"), "f1", ""))
	hotkeys.append((_("F1 long"), "f1_long", ""))
	hotkeys.append((_("F2"), "f2", ""))
	hotkeys.append((_("F2 long"), "f2_long", ""))
	hotkeys.append((_("F3"), "f3", ""))
	hotkeys.append((_("F3 long"), "f3_long", ""))
	hotkeys.remove((_("Search/WEB"), "search", ""))

if boxtype == "optimussos3plus":
	hotkeys.append((_("additional keys for Optimuss OS3+"), "empty", ""))
	hotkeys.append((_("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"),"empty", ""))
	hotkeys.append((_("UHF/Slow"), "slow", ""))
	hotkeys.append((_("UHF/Slow long"), "slow_long", ""))
	hotkeys.append((_("Prov/Fav"), "ab", ""))
	hotkeys.append((_("Prov/Fav long"), "ab_long", ""))
	hotkeys.append((_("Y-Tube"), "www", ""))
	hotkeys.append((_("Y-Tube long"), "www_long", ""))
	hotkeys.remove((_("Search/WEB"), "search", ""))
	hotkeys.remove((_("Mark/Portal/Playlist"), "mark", ""))
	hotkeys.remove((_("Slow"), "slow", ""))

if boxtype.startswith('optimussos'):
	hotkeys.append((_("additional keys for Optimuss OS"), "empty", ""))
	hotkeys.append((_("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"),"empty", ""))
	hotkeys.append((_("Zoom"), "ZoomInOut", ""))

if boxtype.startswith('xpeed'):
	hotkeys.append((_("additional keys for Xpeed"), "empty", ""))
	hotkeys.append((_("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"),"empty", ""))
	hotkeys.remove((_("Mark/Portal/Playlist"), "mark", ""))
	hotkeys.append((_("PLUGIN"), "mark", ""))

config.misc.hotkey = ConfigSubsection()
config.misc.hotkey.additional_keys = ConfigYesNo(default=True)
for x in hotkeys:
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
	hotkeyFunctions.append((_("Show graphical multi EPG"), "Infobar/openGraphEPG", "EPG"))
	hotkeyFunctions.append((_("Show event view"), "Infobar/openEventView", "EPG"))
	hotkeyFunctions.append((_("Show eventinfo plugins"), "Infobar/showEventInfoPlugins", "EPG"))
	hotkeyFunctions.append((_("Show single service EPG"), "Infobar/openSingleServiceEPG", "EPG"))
	hotkeyFunctions.append((_("Show multi Service EPG"), "Infobar/openMultiServiceEPG", "EPG"))
	hotkeyFunctions.append((_("Show Infobar EPG"), "Infobar/openInfoBarEPG", "EPG"))
	hotkeyFunctions.append((_("Main menu"), "Infobar/mainMenu", "InfoBar"))
	hotkeyFunctions.append((_("Show help"), "Infobar/showHelp", "InfoBar"))
	hotkeyFunctions.append((_("Toggle Infobar/SecondInfobar"), "Infobar/toggleShow", "InfoBar"))
	hotkeyFunctions.append((_("Toggle InfoBar only"), "Infobar/showOnlyFirstInfoBar", "InfoBar"))
	hotkeyFunctions.append((_("Show extension selection"), "Infobar/showExtensionSelection", "InfoBar"))
	hotkeyFunctions.append((_("Show plugin selection"), "Infobar/showPluginBrowser", "InfoBar"))
	hotkeyFunctions.append((_("Zap down"), "Infobar/zapDown", "InfoBar"))
	hotkeyFunctions.append((_("Zap up"), "Infobar/zapUp", "InfoBar"))
	hotkeyFunctions.append((_("Switch channel up"), "Infobar/switchChannelUp", "InfoBar"))
	hotkeyFunctions.append((_("Switch channel down"), "Infobar/switchChannelDown", "InfoBar"))
	hotkeyFunctions.append((_("Show service list"), "Infobar/openServiceList", "InfoBar"))
	hotkeyFunctions.append((_("History back"), "Infobar/historyBack", "InfoBar"))
	hotkeyFunctions.append((_("History next"), "Infobar/historyNext", "InfoBar"))
	hotkeyFunctions.append((_("Show Audioselection"), "Infobar/audioSelection", "InfoBar"))
	hotkeyFunctions.append((_("Switch to radio mode"), "Infobar/showRadio", "InfoBar"))
	hotkeyFunctions.append((_("Switch to TV mode"), "Infobar/showTv", "InfoBar"))
	hotkeyFunctions.append((_("Show favourites list"), "Infobar/openFavouritesList", "InfoBar"))
	hotkeyFunctions.append((_("Show movies"), "Infobar/showMovies", "InfoBar"))
	hotkeyFunctions.append((_("Instant record"), "Infobar/instantRecord", "InfoBar"))
	hotkeyFunctions.append((_("Start instant recording"), "Infobar/startInstantRecording", "InfoBar"))
	hotkeyFunctions.append((_("Activate timeshift End"), "Infobar/activateTimeshiftEnd", "InfoBar"))
	hotkeyFunctions.append((_("Activate timeshift end and pause"), "Infobar/activateTimeshiftEndAndPause", "InfoBar"))
	hotkeyFunctions.append((_("Start timeshift"), "Infobar/startTimeshift", "InfoBar"))
	hotkeyFunctions.append((_("Stop timeshift"), "Infobar/stopTimeshift", "InfoBar"))
	hotkeyFunctions.append((_("Start teletext"), "Infobar/startTeletext", "InfoBar"))
	hotkeyFunctions.append((_("Show subservice selection"), "Infobar/subserviceSelection", "InfoBar"))
	hotkeyFunctions.append((_("Show subtitle selection"), "Infobar/subtitleSelection", "InfoBar"))
	hotkeyFunctions.append((_("Letterbox zoom"), "Infobar/vmodeSelection", "InfoBar"))
	hotkeyFunctions.append((_("ZoomInOut"), "InfobarGenerics/ZoomInOut", "InfoBar"))
	hotkeyFunctions.append((_("ZoomOff"), "InfobarGenerics/ZoomInOut", "InfoBar"))
	if SystemInfo["PIPAvailable"]:
		hotkeyFunctions.append((_("Show PIP"), "Infobar/showPiP", "InfoBar"))
		hotkeyFunctions.append((_("Swap PIP"), "Infobar/swapPiP", "InfoBar"))
		hotkeyFunctions.append((_("Move PIP"), "Infobar/movePiP", "InfoBar"))
		hotkeyFunctions.append((_("Toggle PIPzap"), "Infobar/togglePipzap", "InfoBar"))
	hotkeyFunctions.append((_("Activate HbbTV (Redbutton)"), "Infobar/activateRedButton", "InfoBar"))		
	hotkeyFunctions.append((_("Toggle HDMI-In full screen"), "Infobar/HDMIInFull", "InfoBar"))
	hotkeyFunctions.append((_("Toggle HDMI-In PiP"), "Infobar/HDMIInPiP", "InfoBar"))
	hotkeyFunctions.append((_("HotKey Setup"), "Module/Screens.Hotkey/HotkeySetup", "Setup"))
	hotkeyFunctions.append((_("Software update"), "Module/Screens.SoftwareUpdate/UpdatePlugin", "Setup"))
	hotkeyFunctions.append((_("CI (Common Interface) Setup"), "Module/Screens.Ci/CiSelection", "Setup"))
	hotkeyFunctions.append((_("Tuner Configuration"), "Module/Screens.Satconfig/NimSelection", "Scanning"))
	hotkeyFunctions.append((_("Manual Scan"), "Module/Screens.ScanSetup/ScanSetup", "Scanning"))
	hotkeyFunctions.append((_("Automatic Scan"), "Module/Screens.ScanSetup/ScanSimple", "Scanning"))
	for plugin in plugins.getPluginsForMenu("scan"):
		hotkeyFunctions.append((plugin[0], "MenuPlugin/scan/" + plugin[2], "Scanning"))
	hotkeyFunctions.append((_("Network setup"), "Module/Screens.NetworkSetup/NetworkAdapterSelection", "Setup"))
	hotkeyFunctions.append((_("Network menu"), "Infobar/showNetworkMounts", "Setup"))
	hotkeyFunctions.append((_("Plugin Browser"), "Module/Screens.PluginBrowser/PluginBrowser", "Setup"))
	hotkeyFunctions.append((_("Channel Info"), "Module/Screens.ServiceInfo/ServiceInfo", "Setup"))
	hotkeyFunctions.append((_("Timer"), "Module/Screens.TimerEdit/TimerEditList", "Setup"))
	hotkeyFunctions.append((_("PowerTimer"), "Module/Screens.PowerTimerEdit/PowerTimerEditList", "Setup"))
	hotkeyFunctions.append((_("Open AutoTimer"), "Infobar/showAutoTimerList", "Setup"))
	for plugin in plugins.getPluginsForMenu("system"):
		if plugin[2]:
			hotkeyFunctions.append((plugin[0], "MenuPlugin/system/" + plugin[2], "Setup"))
	hotkeyFunctions.append((_("Standby"), "Module/Screens.Standby/Standby", "Power"))
	hotkeyFunctions.append((_("Restart"), "Module/Screens.Standby/TryQuitMainloop/2", "Power"))
	hotkeyFunctions.append((_("Restart enigma"), "Module/Screens.Standby/TryQuitMainloop/3", "Power"))
	hotkeyFunctions.append((_("Deep-Standby"), "Module/Screens.Standby/TryQuitMainloop/1", "Power"))
	hotkeyFunctions.append((_("Usage Setup"), "Setup/usage", "Setup"))
	hotkeyFunctions.append((_("User interface settings"), "Setup/userinterface", "Setup"))
	hotkeyFunctions.append((_("Recording Setup"), "Setup/recording", "Setup"))
	hotkeyFunctions.append((_("Harddisk Setup"), "Setup/harddisk", "Setup"))
	hotkeyFunctions.append((_("Subtitles Settings"), "Setup/subtitlesetup", "Setup"))
	return hotkeyFunctions

class HotkeySetup(Screen):
	def __init__(self, session, args=None):
		Screen.__init__(self, session)
		self['description'] = Label(_('Click on your remote on the button you want to change, then click on OK'))
		self.session = session
		self.setTitle(_("Button setup"))
		self["key_red"] = Button(_("Exit"))
		self["key_green"] = Button(_("Toggle Extra Keys"))		
		self.list = []
		self.hotkeyFunctions = getHotkeyFunctions()
		for x in hotkeys:
			self.list.append(ChoiceEntryComponent('',((x[0]), x[1])))
		self["list"] = ChoiceList(list=self.list[:config.misc.hotkey.additional_keys.value and len(hotkeys) or 16], selection = 0)
		self["choosen"] = ChoiceList(list=[])
		self.getFunctions()
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
		self["HotkeyButtonActions"] = hotkeyActionMap(["HotkeyActions"], dict((x[1], self.hotkeyGlobal) for x in hotkeys))
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
			for x in self.list[:config.misc.hotkey.additional_keys.value and len(hotkeys) or 16]:
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
		self["list"].setList(self.list[:config.misc.hotkey.additional_keys.value and len(hotkeys) or 16])

	def getFunctions(self):
		key = self["list"].l.getCurrentSelection()[0][1]
		if key:
			selected = []
			for x in eval("config.misc.hotkey." + key + ".value.split(',')"):
				if x.startswith("Zap"):
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
		self.skinName="HotkeySetupSelect"
		self.session = session
		self.key = key
		self.setTitle(_("Button setup for") + ": " + key[0][0])
		self["key_red"] = Button(_("Cancel"))
		self["key_green"] = Button(_("Save"))
		self.mode = "list"
		self.hotkeyFunctions = getHotkeyFunctions()
		self.config = eval("config.misc.hotkey." + key[0][1])
		self.expanded = []
		self.selected = []
		for x in self.config.value.split(','):
			if x.startswith("Zap"):
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
			"pageUp": self.toggleMode,
			"pageDown": self.toggleMode
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
					if currentSelected[0][1].startswith("Zap"):
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
			currentSelected[1]=currentSelected[1][:-1] + (_("Zap to") + " " + ServiceReference(args[0]).getServiceName(),)
			self.selected.append([(currentSelected[0][0], currentSelected[0][1] + "/" + args[0].toString()), currentSelected[1]])

	def keyLeft(self):
		self[self.mode].instance.moveSelection(self[self.mode].instance.pageUp)

	def keyRight(self):
		self[self.mode].instance.moveSelection(self[self.mode].instance.pageDown)

	def keyUp(self):
		self[self.mode].instance.moveSelection(self[self.mode].instance.moveUp)

	def keyDown(self):
		self[self.mode].instance.moveSelection(self[self.mode].instance.moveDown)

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
		if (action in tuple(x[1] for x in hotkeys) and self.actions.has_key(action)):
			res = self.actions[action](action)
			if res is not None:
				return res
			return 1
		else:
			return ActionMap.action(self, contexts, action)

class helpableHotkeyActionMap(HelpableActionMap):
	def action(self, contexts, action):
		if (action in tuple(x[1] for x in hotkeys) and self.actions.has_key(action)):
			res = self.actions[action](action)
			if res is not None:
				return res
			return 1
		else:
			return ActionMap.action(self, contexts, action)

class InfoBarHotkey():
	def __init__(self):
		self["HotkeyButtonActions"] = helpableHotkeyActionMap(self, "HotkeyActions",
			dict((x[1],(self.hotkeyGlobal, boundFunction(self.getHelpText, x[1]))) for x in hotkeys), -10)
		self.longkeyPressed = False

	def getKeyFunctions(self, key):
		selection = eval("config.misc.hotkey." + key + ".value.split(',')")
		selected = []
		for x in selection:
			if x.startswith("Zap"):
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
			return _("Hotkey") + " " + tuple(x[0] for x in hotkeys if x[1] == key)[0]

	def hotkeyGlobal(self, key):
		if self.longkeyPressed:
			self.longkeyPressed = False
		else:
			selected = self.getKeyFunctions(key)
			if not selected:
				return 0
			elif len(selected) == 1:
				if key.endswith("_long"):
					self.longkeyPressed = True
				return self.execHotkey(selected[0])
			else:
				key = tuple(x[0] for x in hotkeys if x[1] == key)[0]
				self.session.openWithCallback(self.execHotkey, ChoiceBox, _("Hotkey") + " " + key, selected)

	def execHotkey(self, selected):
		if selected:
			selected = selected[1].split("/")
			if selected[0] == "Plugins":
				twinPlugins = []
				twinPaths = {}
				pluginlist = plugins.getPlugins([PluginDescriptor.WHERE_PLUGINMENU ,PluginDescriptor.WHERE_EXTENSIONSMENU, PluginDescriptor.WHERE_EVENTINFO])
				pluginlist.sort(key=lambda p: p.name)
				for plugin in pluginlist:
					if plugin.name not in twinPlugins and plugin.path:
						if twinPaths.has_key(plugin.path[24:]):
							twinPaths[plugin.path[24:]] += 1
						else:
							twinPaths[plugin.path[24:]] = 1
						if plugin.path[24:] + "/" + str(twinPaths[plugin.path[24:]])== "/".join(selected):
							self.runPlugin(plugin)
							break
						twinPlugins.append(plugin.name)
			elif selected[0] == "MenuPlugin":
				for plugin in plugins.getPluginsForMenu(selected[1]):
					if plugin[2] == selected[2]:
						self.runPlugin(plugin[1])
						break
			elif selected[0] == "Infobar":
				if hasattr(self, selected[1]):
					exec "self." + selected[1] + "()"
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
			elif selected[0] == "Zap":
				self.servicelist.servicelist.setCurrent(eServiceReference("/".join(selected[1:])))
				self.servicelist.zap(enable_pipzap = True)
				if hasattr(self, "lastservice"):
					self.lastservice = eServiceReference("/".join(selected[1:]))
					self.close()
				else:
					self.show()
