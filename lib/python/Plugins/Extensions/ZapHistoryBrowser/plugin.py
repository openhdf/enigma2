# -*- coding: UTF-8 -*-
## Zap-History Browser by AliAbdul
from Components.ActionMap import ActionMap
from Components.config import config, ConfigInteger, ConfigSelection, ConfigSubsection, getConfigListEntry
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.Language import language
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText
from enigma import eListboxPythonMultiContent, eServiceCenter, gFont, getDesktop, eSize
from os import environ
from Plugins.Plugin import PluginDescriptor
from Screens.ChannelSelection import ChannelSelection
from Screens.ParentalControlSetup import ProtectedScreen
from Screens.Screen import Screen
from Tools.Directories import resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
import gettext

################################################

def localeInit():
	lang = language.getLanguage()
	environ["LANGUAGE"] = lang[:2]
	gettext.bindtextdomain("enigma2", resolveFilename(SCOPE_LANGUAGE))
	gettext.textdomain("enigma2")
	gettext.bindtextdomain("ZapHistoryBrowser", "%s%s" % (resolveFilename(SCOPE_PLUGINS), "Extensions/ZapHistoryBrowser/locale/"))

def _(txt):
	t = gettext.dgettext("ZapHistoryBrowser", txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t

localeInit()
language.addCallback(localeInit)

################################################

config.plugins.ZapHistoryConfigurator = ConfigSubsection()
config.plugins.ZapHistoryConfigurator.enable_zap_history = ConfigSelection(choices = {"off": _("disabled"), "on": _("enabled"), "parental_lock": _("disabled at parental lock")}, default="on")
config.plugins.ZapHistoryConfigurator.maxEntries_zap_history = ConfigInteger(default=20, limits=(1, 60))

################################################

def addToHistory(instance, ref):
	if config.plugins.ZapHistoryConfigurator.enable_zap_history.value == "off":
		return
	if config.ParentalControl.configured.value and config.plugins.ZapHistoryConfigurator.enable_zap_history.value == "parental_lock":
		if parentalControl.getProtectionLevel(ref.toCompareString()) != -1:
			return
	if instance.servicePath is not None:
		tmp = instance.servicePath[:]
		tmp.append(ref)
		try: del instance.history[instance.history_pos+1:]
		except: pass
		instance.history.append(tmp)
		hlen = len(instance.history)
		if hlen > config.plugins.ZapHistoryConfigurator.maxEntries_zap_history.value:
			del instance.history[0]
			hlen -= 1
		instance.history_pos = hlen-1

ChannelSelection.addToHistory = addToHistory

################################################

class ZapHistoryConfigurator(ConfigListScreen, Screen):
	skin = """
		<screen position="center,center" size="420,70" title="%s" >
			<widget name="config" position="0,0" size="420,70" scrollbarMode="showOnDemand" />
		</screen>""" % _("Zap-History Configurator")

	def __init__(self, session):
		Screen.__init__(self, session)
		self.session = session
		
		ConfigListScreen.__init__(self, [
			getConfigListEntry(_("Enable zap history:"), config.plugins.ZapHistoryConfigurator.enable_zap_history),
			getConfigListEntry(_("Maximum zap history entries:"), config.plugins.ZapHistoryConfigurator.maxEntries_zap_history)])
		
		self["actions"] = ActionMap(["OkCancelActions"], {"ok": self.save, "cancel": self.exit}, -2)

	def save(self):
		for x in self["config"].list:
			x[1].save()
		self.close()

	def exit(self):
		for x in self["config"].list:
			x[1].cancel()
		self.close()

################################################

class ZapHistoryBrowserList(MenuList):
	def __init__(self, list, enableWrapAround=True):
		MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
		desktopSize = getDesktop(0).size()
		if desktopSize.width() == 1920:
			self.l.setItemHeight(30)
			self.l.setFont(0, gFont("Regular", 28))
			self.l.setFont(1, gFont("Regular", 25))
		elif desktopSize.width() == 1280:
			self.l.setItemHeight(21)
			self.l.setFont(0, gFont("Regular", 21))
			self.l.setFont(1, gFont("Regular", 16))
		else:
			self.l.setItemHeight(21)
			self.l.setFont(0, gFont("Regular", 21))
			self.l.setFont(1, gFont("Regular", 16))		

def ZapHistoryBrowserListEntry(serviceName, eventName):
	desktopSize = getDesktop(0).size()
	if desktopSize.width() == 1920:
		res = [serviceName]
		res.append(MultiContentEntryText(pos=(0, 0), size=(230, 30), font=0, text=serviceName))
		res.append(MultiContentEntryText(pos=(240, 0), size=(550, 30), font=1, text=eventName))
		return res
	elif desktopSize.width() == 1280:
		res = [serviceName]
		res.append(MultiContentEntryText(pos=(0, 0), size=(180, 22), font=0, text=serviceName))
		res.append(MultiContentEntryText(pos=(190, 0), size=(550, 16), font=1, text=eventName))
		return res
	else:
		res = [serviceName]
		res.append(MultiContentEntryText(pos=(0, 0), size=(180, 22), font=0, text=serviceName))
		res.append(MultiContentEntryText(pos=(190, 0), size=(550, 16), font=1, text=eventName))
		return res

################################################

class ZapHistoryBrowser(Screen, ProtectedScreen):
	skin = """
	<screen position="670,440" size="560,210" title="%s" >
		<ePixmap pixmap="skin_default/buttons/red.png" position="0,0" size="140,40" transparent="1" alphatest="on" />
		<ePixmap pixmap="skin_default/buttons/green.png" position="140,0" size="140,40" transparent="1" alphatest="on" />
		<ePixmap pixmap="skin_default/buttons/yellow.png" position="280,0" size="140,40" transparent="1" alphatest="on" />
		<ePixmap pixmap="skin_default/buttons/blue.png" position="420,0" size="140,40" transparent="1" alphatest="on" />
		<widget name="key_red" position="0,0" zPosition="1" size="140,40" font="Regular;20" valign="center" halign="center" backgroundColor="#1f771f" transparent="1" />
		<widget name="key_green" position="140,0" zPosition="1" size="140,40" font="Regular;20" valign="center" halign="center" backgroundColor="#1f771f" transparent="1" />
		<widget name="key_yellow" position="280,0" zPosition="1" size="140,40" font="Regular;20" valign="center" halign="center" backgroundColor="#1f771f" transparent="1" />
		<widget name="key_blue" position="420,0" zPosition="1" size="140,40" font="Regular;20" valign="center" halign="center" backgroundColor="#1f771f" transparent="1" />
		<widget name="list" position="0,40" size="560,180" scrollbarMode="showOnDemand" />
	</screen>""" % _("Zap-History")

	def __init__(self, session, servicelist):
		Screen.__init__(self, session)
		ProtectedScreen.__init__(self)
		self.session = session
		
		self.servicelist = servicelist
		self.serviceHandler = eServiceCenter.getInstance()
		self.allowChanges = True
		
		self["list"] = ZapHistoryBrowserList([])
		self["key_red"] = Label(_("Clear"))
		self["key_green"] = Label(_("Delete"))
		self["key_yellow"] = Label(_("Zap+Close"))
		self["key_blue"] = Label(_("Config"))
		
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
			{
				"ok": self.zap,
				"cancel": self.close,
				"red": self.clear,
				"green": self.delete,
				"yellow": self.zapAndClose,
				"blue": self.config
			}, prio=-1)
		
		self.onLayoutFinish.append(self.buildList)

	def buildList(self):
		list = []
		for x in self.servicelist.history:
			if len(x) == 2: # Single-Bouquet
				ref = x[1]
			else: # Multi-Bouquet
				ref = x[2]
			info = self.serviceHandler.info(ref)
			if info:
				name = info.getName(ref).replace('\xc2\x86', '').replace('\xc2\x87', '')
				event = info.getEvent(ref)
				if event is not None:
					eventName = event.getEventName()
					if eventName is None:
						eventName = ""
				else:
					eventName = ""
			else:
				name = "N/A"
				eventName = ""
			list.append(ZapHistoryBrowserListEntry(name, eventName))
		list.reverse()
		self["list"].setList(list)

	def zap(self):
		length = len(self.servicelist.history)
		if length > 0:
			self.servicelist.history_pos = (length - self["list"].getSelectionIndex()) - 1
			self.servicelist.setHistoryPath()

	def clear(self):
		if self.allowChanges:
			for i in range(0, len(self.servicelist.history)):
				del self.servicelist.history[0]
			self.buildList()
			self.servicelist.history_pos = 0

	def delete(self):
		if self.allowChanges:
			length = len(self.servicelist.history)
			if length > 0:
				idx = (length - self["list"].getSelectionIndex()) - 1
				del self.servicelist.history[idx]
				self.buildList()
				currRef = self.session.nav.getCurrentlyPlayingServiceReference()
				idx = 0
				for x in self.servicelist.history:
					if len(x) == 2: # Single-Bouquet
						ref = x[1]
					else: # Multi-Bouquet
						ref = x[2]
					if ref == currRef:
						self.servicelist.history_pos = idx
						break
					else:
						idx += 1

	def zapAndClose(self):
		self.zap()
		self.close()

	def config(self):
		if self.allowChanges:
			self.session.open(ZapHistoryConfigurator)

	def isProtected(self):
		return config.ParentalControl.setuppinactive.value and config.ParentalControl.configured.value
	
	def pinEntered(self, result):
		if result is None:
			self.allowChanges = False
		elif not result:
			self.allowChanges = False
		else:
			self.allowChanges = True

################################################

def main(session, servicelist, **kwargs):
	session.open(ZapHistoryBrowser, servicelist)

def Plugins(**kwargs):
	return PluginDescriptor(name=_("Zap-History Browser"), where=PluginDescriptor.WHERE_EXTENSIONSMENU, fnc=main)
