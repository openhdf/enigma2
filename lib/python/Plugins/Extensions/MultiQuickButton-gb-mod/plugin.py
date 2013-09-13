# -*- coding: utf-8 -*-
# Multi QuickButton Rel. 2.7
# from Emanuel CLI 2009
#
# ***special thanks*** to Dr.Best & AliAbdul ;-)
# modified for VU+ by plnick <plnick@vuplus-support.org>
# modified version is based on original MQB version 2.7

#This plugin is free software, you are allowed to
#modify it (if you keep the license),
#but you are not allowed to distribute/publish
#it without source code (this version and your modifications).
#This means you also have to distribute
#source code of your modifications.

from Screens.Screen import Screen
from Screens.ChoiceBox import ChoiceBox
from Screens.ChannelSelection import ChannelSelection
from Screens.MessageBox import MessageBox
from  Screens.InfoBarGenerics import InfoBarPlugins
from Components.ActionMap import ActionMap
from Components.PluginComponent import plugins
from Components.config import config, ConfigSubsection, ConfigYesNo
from Plugins.Plugin import PluginDescriptor
from Plugins.Plugin import PluginDescriptor
from QuickButtonXML import QuickButtonXML
from MultiQuickButton import MultiQuickButton, QuickButton

import xml.sax.xmlreader
import os.path
import os
import keymapparser
from __init__ import _


baseInfoBarPlugins__init__ = None
baserunPlugin = None
StartOnlyOneTime = False
line = "------------------------------------------------------------------"

def autostart(reason, **kwargs):
	if reason == 0:
		if config.plugins.QuickButton.enable.value:
			print line
			print "[MultiQuickButton] enabled: ",config.plugins.QuickButton.enable.getValue()
			checkMQBKeys()
			print line
			global baseInfoBarPlugins__init__, baserunPlugin
			if "session" in kwargs:
				session = kwargs["session"]
				if baseInfoBarPlugins__init__ is None:
					baseInfoBarPlugins__init__ = InfoBarPlugins.__init__
				if baserunPlugin is None:
					baserunPlugin = InfoBarPlugins.runPlugin	
				InfoBarPlugins.__init__ = InfoBarPlugins__init__
				InfoBarPlugins.runPlugin = runPlugin
				InfoBarPlugins.checkQuickSel = checkQuickSel
				InfoBarPlugins.askForQuickList = askForQuickList
				InfoBarPlugins.getQuickList = getQuickList
				InfoBarPlugins.execQuick = execQuick
				InfoBarPlugins.quickSelectGlobal = quickSelectGlobal
		else:
			print line
			print "[MultiQuickButton] disabled"
			print line
	else:
		print "[MultiQuickButton] checking keymap.xml..."
		rePatchKeymap()

def checkMQBKeys():
	mqbkeymapfile = "/usr/lib/enigma2/python/Plugins/Extensions/MultiQuickButton/keymap.xml"
	mqbkeymap = open(mqbkeymapfile, "r")
	text = mqbkeymap.read()
	mqbkeymap.close()
	ptskeys = [	"<key id=\"KEY_PLAY\" mapto=\"play\" flags=\"m\" />", \
			"<key id=\"KEY_STOP\" mapto=\"stop\" flags=\"b\" />", \
			"<key id=\"KEY_PAUSE\" mapto=\"pause\" flags=\"m\" />", \
			"<key id=\"KEY_REWIND\" mapto=\"rewind\" flags=\"b\" />", \
			"<key id=\"KEY_FASTFORWARD\" mapto=\"fastforward\" flags=\"b\" />", \
			"<key id=\"KEY_PREVIOUSSONG\" mapto=\"rewind\" flags=\"b\" />", \
			"<key id=\"KEY_NEXTSONG\" mapto=\"fastforward\" flags=\"b\" />" ]

	keys = [	"<key id=\"KEY_OK\" mapto=\"ok\" flags=\"m\" />", \
			"<key id=\"KEY_EXIT\" mapto=\"exit\" flags=\"m\" />" ]

	if os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/PermanentTimeshift"):
		for ptskey in ptskeys:
			ptskeyinactive = "<!-- " + ptskey + " -->"
			if not ptskeyinactive in text:
				text = text.replace(ptskey, ptskeyinactive)
	else:
		for ptskey in ptskeys:
			ptskeyinactive = "<!-- " + ptskey + " -->"
			if ptskeyinactive in text:
				text = text.replace(ptskeyinactive, ptskey)

	if config.plugins.QuickButton.okexitstate.value:
		for key in keys:
			okexitinactive = "<!-- " + key + " -->"
			if okexitinactive in text:
				text = text.replace(okexitinactive, key)
	else:
		for key in keys:
			okexitinactive = "<!-- " + key + " -->"
			if okexitinactive not in text:
				text = text.replace(key, okexitinactive)

	mqbkeymap = open(mqbkeymapfile, "w")
	mqbkeymap.write(text)
	mqbkeymap.close()
	keymapparser.removeKeymap(mqbkeymapfile)
	keymapparser.readKeymap(mqbkeymapfile)

def rePatchKeymap():
	globalkeymapfile = "/usr/share/enigma2/keymap.xml"
	globalkeymap = open(globalkeymapfile, "r")
	text = globalkeymap.read()
	globalkeymap.close()
	globalkeys = [ 	"<key id=\"KEY_YELLOW\" mapto=\"timeshiftStart\" flags=\"m\" />", \
			"<key id=\"KEY_YELLOW\" mapto=\"timeshiftActivateEndAndPause\" flags=\"m\" />", \
			"<key id=\"KEY_VIDEO\" mapto=\"showMovies\" flags=\"m\" />", \
			"<key id=\"KEY_RADIO\" mapto=\"showRadio\" flags=\"m\" />", \
			"<key id=\"KEY_TEXT\" mapto=\"startTeletext\" flags=\"m\" />", \
			"<key id=\"KEY_HELP\" mapto=\"displayHelp\" flags=\"m\" />" ]
	for globalkey in globalkeys:
		globalkeyreplace = globalkey.replace("\"m\"", "\"b\"")
		text = text.replace(globalkey, globalkeyreplace)
	globalkeymap = open(globalkeymapfile, "w")
	globalkeymap.write(text)
	globalkeymap.close()

def InfoBarPlugins__init__(self):
	global StartOnlyOneTime
	if not StartOnlyOneTime:
		StartOnlyOneTime = True

		self["QuickButtonActions"] = MQBActionMap(["QuickButtonActions"],
			{
				"red": self.quickSelectGlobal,
				"red_long": self.quickSelectGlobal,
				"green": self.quickSelectGlobal,
				"green_long": self.quickSelectGlobal,
				"yellow": self.quickSelectGlobal,
				"yellow_long": self.quickSelectGlobal,
				"blue": self.quickSelectGlobal,
				"blue_long": self.quickSelectGlobal,
				"pvr": self.quickSelectGlobal,
				"pvr_long": self.quickSelectGlobal,
				"radio": self.quickSelectGlobal,
				"radio_long": self.quickSelectGlobal,
				"tv": self.quickSelectGlobal,
				"text": self.quickSelectGlobal,
				"text_long": self.quickSelectGlobal,
				"fav": self.quickSelectGlobal,
				"fav_long": self.quickSelectGlobal,
				"screen": self.quickSelectGlobal,
				"screen_long": self.quickSelectGlobal,
				"history": self.quickSelectGlobal,
				"history_long": self.quickSelectGlobal,
				"epg": self.quickSelectGlobal,
				"epg_long": self.quickSelectGlobal,
				"help": self.quickSelectGlobal,
				"help_long": self.quickSelectGlobal,
				"info": self.quickSelectGlobal,
				"info_long": self.quickSelectGlobal,
				"end": self.quickSelectGlobal,
				"end_long": self.quickSelectGlobal,
				"home": self.quickSelectGlobal,
				"home_long": self.quickSelectGlobal,
				"cross_up": self.quickSelectGlobal,
				"cross_down": self.quickSelectGlobal,
				"cross_left": self.quickSelectGlobal,
				"cross_right": self.quickSelectGlobal,
				"channeldown": self.quickSelectGlobal,
				"channelup": self.quickSelectGlobal,
				"next": self.quickSelectGlobal,
				"previous": self.quickSelectGlobal,
				"audio": self.quickSelectGlobal,
				"ok": self.quickSelectGlobal,
				"exit": self.quickSelectGlobal,	
				"play": self.quickSelectGlobal,
				"stop": self.quickSelectGlobal,	
				"pause": self.quickSelectGlobal,	
				"fastforward": self.quickSelectGlobal,	
				"rewind": self.quickSelectGlobal,	
				"f1": self.quickSelectGlobal,
				"f2": self.quickSelectGlobal,
				"f3": self.quickSelectGlobal,
				"f4": self.quickSelectGlobal,
				"console": self.quickSelectGlobal,
				"web": self.quickSelectGlobal,
				"mail": self.quickSelectGlobal,
				"m1": self.quickSelectGlobal,
				"m2": self.quickSelectGlobal,
				"subtitle": self.quickSelectGlobal,
				"subtitle_long": self.quickSelectGlobal,
				"filelist": self.quickSelectGlobal,
				"filelist_long": self.quickSelectGlobal,
				"playlist": self.quickSelectGlobal,
				"playlist_long": self.quickSelectGlobal,
				"timer": self.quickSelectGlobal,
				"timer_long": self.quickSelectGlobal,
				"timeshift": self.quickSelectGlobal,
				"timeshift_long": self.quickSelectGlobal,
				"mark": self.quickSelectGlobal,
				"mark_long": self.quickSelectGlobal,
				"search": self.quickSelectGlobal,
				"search_long": self.quickSelectGlobal,
				"slow": self.quickSelectGlobal,
				"slow_long": self.quickSelectGlobal,
			})
	else:
		InfoBarPlugins.__init__ = InfoBarPlugins.__init__
		InfoBarPlugins.runPlugin = InfoBarPlugins.runPlugin
		InfoBarPlugins.quickSelectGlobal = None
	baseInfoBarPlugins__init__(self)

def runPlugin(self, plugin):
	baserunPlugin(self,plugin)

def checkQuickSel(self, path):
	list = None
	button = os.path.basename(path)[12:-4]
	try:
		menu = xml.dom.minidom.parse(path)
		db = QuickButtonXML(menu)
		list = db.getSelection()
	except Exception, e:
		self.session.open(MessageBox,("XML " + _("Error") + ": %s" % (e)),  MessageBox.TYPE_ERROR)
		print "[MultiQuickbutton] ERROR: ",e
		
	if list <> None:
		if len(list) == 1:
			self.execQuick(list[0])
		elif len(list) > 1:
			self.session.openWithCallback(self.askForQuickList,ChoiceBox,"Multi Quickbutton Menu %s" % (button), self.getQuickList(list))
		else:
			if os.path.exists(path):
				self.session.open(QuickButton, path, (_('Quickbutton: Key ') + button))
			else:
				self.session.open(MessageBox,(_("file %s not found!") % (path)),  MessageBox.TYPE_ERROR)

def askForQuickList(self, res):
	if res is None:
		pass
	else:
		self.execQuick(res)

def getQuickList(self, list):
	quickList = []
	for e in list:
		e2 = [_(e[0]), e[1], e[2], e[3], e[4], e[5]]
		quickList.append((e2))
		
	return quickList

def execQuick(self,entry):
	if entry <> None:
		if entry[3] <> "":
			try:
				module_import = "from " + entry[3] + " import *"
				exec(module_import)
				if entry[4] <> "":
					try:
						screen = "self.session.open(" + entry[4] + ")"
						exec(screen)
					except Exception, e:
						self.session.open(MessageBox,("Screen " + _("Error") + ": %s" % (e)),  MessageBox.TYPE_ERROR)
			except Exception, e:
				self.session.open(MessageBox,("Module " + _("Error") + ": %s" % (e)),  MessageBox.TYPE_ERROR)
		if entry[5] <> "":
			try:
				exec(entry[5])
			except Exception, e:
				self.session.open(MessageBox,("Code " + _("Error") + ": %s" % (e)),  MessageBox.TYPE_ERROR)

def quickSelectGlobal(self, key):
	if key:
		path = '/etc/MultiQuickButton/quickbutton_' + key + '.xml'
		if os.path.exists(path):
			self.checkQuickSel(path)
		else:
			self.session.open(MessageBox,("file %s not found!" % (path)),  MessageBox.TYPE_ERROR)

class MQBActionMap(ActionMap):
	def action(self, contexts, action):
		quickSelection = ("red","red_long","green","green_long","yellow","yellow_long","blue","blue_long","pvr","pvr_long","radio","radio_long", \
				  "text","text_long","epg","epg_long","help","help_long","info","info_long","end","end_long","home","home_long","cross_up","cross_down","cross_left", \
				  "cross_right","previous","next","channelup","channeldown","f1","f2","f3","audio","exit","ok","play","pause","rewind","fastforward","stop","tv", \
				  "console","f4","web","mail","m1","m2","fav", "fav_long", "screen", "screen_long", "history", "history_long", \
				  "subtitle","subtitle_long","filelist","filelist_long","playlist","playlist_long","timer","timer_long", \
				  "timeshift","timeshift_long","mark","mark_long","search","search_long","slow","slow_long")
		if (action in quickSelection and self.actions.has_key(action)):
			res = self.actions[action](action)
			if res is not None:
				return res
			return 1
		else:
			return ActionMap.action(self, contexts, action)

def main(session,**kwargs):
	session.open(MultiQuickButton)

def menu(menuid, **kwargs):
	if menuid == "mainmenu":
		return [(_("Multi Quickbutton"), main, "multi_quick", 55)]
	return []

def Plugins(**kwargs):
	if config.plugins.QuickButton.mainmenu.value:
		return [PluginDescriptor(
				where = [PluginDescriptor.WHERE_SESSIONSTART, PluginDescriptor.WHERE_AUTOSTART],
				fnc = autostart),
				PluginDescriptor(
				name="Multi Quickbutton",
				description="Multi Quickbutton for Keyboard and RC SCP Version",
				where = PluginDescriptor.WHERE_PLUGINMENU,
				icon="multiquickbutton.png",
				fnc=main),
				PluginDescriptor(
				name="Multi Quickbutton",
				where = PluginDescriptor.WHERE_EXTENSIONSMENU,
				fnc=main),
				PluginDescriptor(
				name="Multi Quickbutton",
				description="Multi Quickbutton for Keyboard and RC SCP Version",
				where = PluginDescriptor.WHERE_MENU,
				fnc=menu)]
	else:
		return [PluginDescriptor(
				where = [PluginDescriptor.WHERE_SESSIONSTART, PluginDescriptor.WHERE_AUTOSTART],
				fnc = autostart),
				PluginDescriptor(
				name="Multi Quickbutton",
				description="Multi Quickbutton for Keyboard and RC SCP Version",
				where = PluginDescriptor.WHERE_PLUGINMENU,
				icon="multiquickbutton.png",
				fnc=main),
				PluginDescriptor(
				name="Multi Quickbutton",
				where = PluginDescriptor.WHERE_EXTENSIONSMENU,
				fnc=main)]
