#
# Extended NumberZap Plugin for Enigma2
# Coded by vlamo (c) 2011,2012
#
# Version: 1.0-rc3 (06.02.2012 16:05)
# Support: http://dream.altmaster.net/
#

from . import _
from Plugins.Plugin import PluginDescriptor
from Components.config import config, ConfigSubsection, ConfigYesNo, ConfigInteger, ConfigDirectory
from Screens.Screen import Screen
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.ActionMap import NumberActionMap
from enigma import eServiceReference, eServiceCenter, eTimer, getDesktop
from Screens.InfoBarGenerics import InfoBarNumberZap, InfoBarEPG
from Screens.ChannelSelection import ChannelSelectionBase, BouquetSelector
from Tools.BoundFunction import boundFunction
from Tools.Directories import pathExists, SCOPE_SKIN_IMAGE, SCOPE_ACTIVE_SKIN, resolveFilename




base_keyNumberGlobal = None
base_getBouquetNumOffset = None
base_ChannelSelectionBase__init__ = None
config.plugins.NumberZapExt = ConfigSubsection()
config.plugins.NumberZapExt.enable = ConfigYesNo(default=False)
config.plugins.NumberZapExt.kdelay = ConfigInteger(default=3000, limits=(0,9999))	# "time to wait next keypress (milliseconds)"
config.plugins.NumberZapExt.acount = ConfigYesNo(default=False)		# "alternative service counter in bouquets"
#config.plugins.NumberZapExt.buqsel = ConfigYesNo(default=False)	# "select bouquet if not in favorites"
config.plugins.NumberZapExt.hotkey = ConfigYesNo(default=False)		# "enable number hotkeys"
config.plugins.NumberZapExt.picons = ConfigYesNo(default=False)		# "enable picons"
config.plugins.NumberZapExt.picondir = ConfigDirectory()		# "picons directory paths"
config.plugins.NumberZapExt.action = ConfigSubsection()
config.plugins.NumberZapExt.action.confirm = ConfigYesNo(default=True)
config.plugins.NumberZapExt.action.shutdown = ConfigInteger(default=0, limits=(0,9999))
config.plugins.NumberZapExt.action.reboot = ConfigInteger(default=0, limits=(0,9999))
config.plugins.NumberZapExt.action.restart = ConfigInteger(default=0, limits=(0,9999))
config.plugins.NumberZapExt.action.standby = ConfigInteger(default=0, limits=(0,9999))
config.plugins.NumberZapExt.action.plugins = ConfigInteger(default=0, limits=(0,9999))
config.plugins.NumberZapExt.action.service_info = ConfigInteger(default=0, limits=(0,9999))




class NumberZapExt(Screen):
	if getDesktop(0).size().width() > 720:
		skin = """<screen name="NumberZapExt" position="center,center" size="600,160" title="Channel">
				<widget name="chPicon" position="475,10" size="100,60" alphatest="on" />
				<widget name="number"  position="5,35"   size="190,30" halign="right" font="Regular;26" />
				<widget name="chNum"   position="210,35" size="240,30" halign="left"  font="Regular;26" />
				<widget name="channel" position="5,75"   size="190,30" halign="right" font="Regular;26" />
				<widget name="chName"  position="210,75" size="375,30" halign="left"  font="Regular;24" noWrap="1" />
				<widget name="bouquet" position="5,115"   size="190,30" halign="right" font="Regular;26" />
				<widget name="chBouq"  position="210,115" size="375,30" halign="left"  font="Regular;24" noWrap="1" />
			</screen>"""
	else:
		skin = """<screen name="NumberZapExt" position="center,center" size="350,145" title="Channel">
				<widget name="chPicon" position="273,7" size="70,53" alphatest="on" />
				<widget name="number"  position="5,35"   size="110,25" halign="right" font="Regular;23" />
				<widget name="chNum"   position="130,35" size="130,25" halign="left"  font="Regular;23" />
				<widget name="channel" position="5,70"   size="110,25" halign="right" font="Regular;23" />
				<widget name="chName"  position="130,70" size="215,25" halign="left"  font="Regular;21" noWrap="1" />
				<widget name="bouquet" position="5,105"   size="110,25" halign="right" font="Regular;23" />
				<widget name="chBouq"  position="130,105" size="215,25" halign="left"  font="Regular;21" noWrap="1" />
			</screen>"""

	def __init__(self, session, number, servicelist=None):
		Screen.__init__(self, session)
		self.digits = 4
		self.field = str(number)
		self.servicelist = servicelist
		self.kdelay = config.plugins.NumberZapExt.kdelay.value
		self.bouqSelDlg = None
		self.bouquet = None
		self.action = ''
		self.action_prio = 'low'
		self.defpicon = None
		for scope, path in {SCOPE_SKIN_IMAGE: "skin_default/picon_default.png", SCOPE_ACTIVE_SKIN: "picon_default.png"}.items():
			tmp = resolveFilename(scope, path)
			if pathExists(tmp):
				self.defpicon = tmp
				break
		self.picons = config.plugins.NumberZapExt.picons.value

		self["number"]  = Label(_("Number:"))
		self["channel"] = Label(_("Channel:"))
		self["bouquet"] = Label(_("Bouquet:"))
		self["chNum"]   = Label()
		self["chName"]  = Label()
		self["chBouq"]  = Label()
		self["chPicon"] = Pixmap()
		self["actions"] = NumberActionMap(["SetupActions"],
			{
				"cancel": self.quit,
				"ok": self.keyOK,
				"1": self.keyNumberGlobal,
				"2": self.keyNumberGlobal,
				"3": self.keyNumberGlobal,
				"4": self.keyNumberGlobal,
				"5": self.keyNumberGlobal,
				"6": self.keyNumberGlobal,
				"7": self.keyNumberGlobal,
				"8": self.keyNumberGlobal,
				"9": self.keyNumberGlobal,
				"0": self.keyNumberGlobal
			})

		self.Timer = eTimer()
		self.Timer.callback.append(self.keyOK)
		self.onFirstExecBegin.append(self.__onStart)

	def __onStart(self):
		if self.servicelist and self.servicelist.getMutableList() is None and config.plugins.NumberZapExt.acount.value:
			bouquets = self.servicelist.getBouquetList()
			if not bouquets: self.quit()
			if len(bouquets) == 1:
				self.bouquetSelected(bouquet[0][1])
			else:
				self.bouqSelDlg = self.session.openWithCallback(self.bouquetSelectorClosed, BouquetSelector, bouquets, self.bouquetSelected, enableWrapAround=True)
		else:
			self.printLabels()
			self.startTimer()

	def bouquetSelectorClosed(self, retval):
		if retval is False:
			self.quit()
		else:
			self.bouqSelDlg = None

	def bouquetSelected(self, bouquet):
		if self.bouqSelDlg:
			self.bouqSelDlg.close(True)
		self.bouquet = bouquet
		self.printLabels()
		self.startTimer()

	def startTimer(self):
		if self.kdelay:
			self.Timer.start(self.kdelay, True)

	def printLabels(self):
		if self.action_prio != 'low':
			self.action = self.getHotkeyAction(int(self.field))
			if self.action:
				name = self.action.replace('_',' ').title()
				channel = _("Action:")
				bouquet = bqname = ""
			else:
				channel = _("Channel:")
				bouquet = _("Bouquet:")
				service, name, bqname = self.getNameFromNumber(int(self.field))
				if name == 'N/A': name = _('invalid channel number')
		else:
			channel = _("Channel:")
			bouquet = _("Bouquet:")
			self.action = ''
			service, name, bqname = self.getNameFromNumber(int(self.field))
			if name == 'N/A':
				if not service is None:
					name = _("service not found")
				else:
					name = _("invalid channel number")
					self.action = self.getHotkeyAction(int(self.field))
					if self.action:
						name = self.action.replace('_',' ').title()
						channel = _("Action:")
						bouquet = bqname = ""
		
		self["chNum"].setText(self.field)
		self["channel"].setText(channel)
		self["bouquet"].setText(bouquet)
		self["chName"].setText(name)
		self["chBouq"].setText(bqname)
		if self.picons:
			pngname = self.defpicon
			if service:
				sname = service.toString()
				pos = sname.rfind(':')
				if pos != -1:
					sname = sname[:pos].rstrip(':').replace(':','_')
					sname = config.plugins.NumberZapExt.picondir.value + sname + '.png'
					if pathExists(sname):
						pngname = sname
			self["chPicon"].instance.setPixmapFromFile(pngname)

	def quit(self):
		self.Timer.stop()
		self.close(0, None)

	def keyOK(self):
		self.Timer.stop()
		self.close(int(self["chNum"].getText()), self.action or self.bouquet)

	def keyNumberGlobal(self, number):
		self.startTimer()
		l = len(self.field)
		if l < self.digits:
			l += 1
			self.field = self.field + str(number)
			self.printLabels()
		if l >= self.digits and self.kdelay:
			self.keyOK()

	def getNameFromNumber(self, number):
		name = 'N/A'
		bqname = 'N/A'
		service, bouquet = getServiceFromNumber(self, number, config.plugins.NumberZapExt.acount.value, self.bouquet)
		if not service is None:
			serviceHandler = eServiceCenter.getInstance()
			info = serviceHandler.info(service)
			name = info and info.getName(service) or 'N/A'
			if bouquet and bouquet.valid():
				info = serviceHandler.info(bouquet)
				bqname = info and info.getName(bouquet)
		return service, name, bqname

	def getHotkeyAction(self, number):
		if config.plugins.NumberZapExt.hotkey.value:
			for (key,val) in config.plugins.NumberZapExt.action.content.items.items():
				if val.value == number:
					return key
		return ''




def getServiceFromNumber(self, number, acount=True, bouquet=None):
	def searchHelper(serviceHandler, num, bouquet):
		servicelist = serviceHandler.list(bouquet)
		if not servicelist is None:
			while num:
				s = servicelist.getNext()
				if not s.valid(): break
				if not (s.flags & (eServiceReference.isMarker|eServiceReference.isDirectory)):
					num -= 1
			if not num: return s, num
		return None, num

	if self.servicelist is None: return None
	service = None
	serviceHandler = eServiceCenter.getInstance()
	if not config.usage.multibouquet.value:
		bouquet = self.servicelist.bouquet_root
		service, number = searchHelper(serviceHandler, number, bouquet)
	elif acount and self.servicelist.getMutableList() is not None:
		bouquet = self.servicelist.getRoot()
		service, number = searchHelper(serviceHandler, number, bouquet)
	elif acount and bouquet is not None:
		service, number = searchHelper(serviceHandler, number, bouquet)
	else:
		bouquet = self.servicelist.bouquet_root
		bouquetlist = serviceHandler.list(bouquet)
		if not bouquetlist is None:
			while number:
				bouquet = bouquetlist.getNext()
				if not bouquet.valid(): break
				if bouquet.flags & eServiceReference.isDirectory:
					service, number = searchHelper(serviceHandler, number, bouquet)
					if acount: break
	return service, bouquet




def zapToNumber(self, number, bouquet):
	service, bouquet = getServiceFromNumber(self, number, config.plugins.NumberZapExt.acount.value, bouquet)
	if not service is None:
		if self.servicelist.getRoot() != bouquet:
			self.servicelist.clearPath()
			if self.servicelist.bouquet_root != bouquet:
				self.servicelist.enterPath(self.servicelist.bouquet_root)
			self.servicelist.enterPath(bouquet)
		self.servicelist.setCurrentSelection(service)
		self.servicelist.zap()

def actionConfirmed(self, action, retval):
	if retval:
		if action == 'shutdown':
			from Screens.Standby import TryQuitMainloop
			self.session.open(TryQuitMainloop, 1)
		elif action == 'reboot':
			from Screens.Standby import TryQuitMainloop
			self.session.open(TryQuitMainloop, 2)
		elif action == 'restart':
			from Screens.Standby import TryQuitMainloop
			self.session.open(TryQuitMainloop, 3)
		elif action == 'standby':
			from Screens.Standby import Standby
			self.session.open(Standby)
		elif action == 'plugins':
			from Screens.PluginBrowser import PluginBrowser
			self.session.open(PluginBrowser)
		elif action == 'service_info':
			from Screens.ServiceInfo import ServiceInfo
			self.session.open(ServiceInfo)

def numberEntered(self, retval, bouquet=None):
	if retval > 0:
		if isinstance(bouquet, str):
			if config.plugins.NumberZapExt.action.confirm.value:
				from Screens.MessageBox import MessageBox
				self.session.openWithCallback(boundFunction(actionConfirmed, self, bouquet), MessageBox, _("Really run %s now?")%(bouquet.replace('_',' ').title()), type=MessageBox.TYPE_YESNO, timeout=10, default=True)
			else:
				actionConfirmed(self, bouquet, True)
		else:
			zapToNumber(self, retval, bouquet)

def new_keyNumberGlobal(self, number):
	if not config.plugins.NumberZapExt.enable.value or number == 0:
			base_keyNumberGlobal(self, number)
	else:
		try:
			pts_enabled = config.plugins.pts.enabled.value
		except:
			pts_enabled = False
		if (self.has_key("TimeshiftActions") and not self.timeshift_enabled) or pts_enabled:
			self.session.openWithCallback(boundFunction(numberEntered, self), NumberZapExt, number, self.servicelist)

def new_getBouquetNumOffset(self, bouquet):
	if config.plugins.NumberZapExt.acount.value:
		return 0
	else:
		return base_getBouquetNumOffset(self, bouquet)

def new_AltCountChanged(self, configElement):
	service = self.getCurrentSelection()
	self.setRoot(self.getRoot())
	self.setCurrentSelection(service)

def new_ChannelSelectionBase__init__(self, session):
	config.plugins.NumberZapExt.acount.addNotifier(self.AltCountChanged, False)
	base_ChannelSelectionBase__init__(self, session)




def StartMainSession(session, **kwargs):
	global base_getBouquetNumOffset, base_keyNumberGlobal, base_ChannelSelectionBase__init__
	if base_getBouquetNumOffset is None:
		base_getBouquetNumOffset = ChannelSelectionBase.getBouquetNumOffset
		ChannelSelectionBase.getBouquetNumOffset = new_getBouquetNumOffset
	if base_ChannelSelectionBase__init__ is None:
		base_ChannelSelectionBase__init__ = ChannelSelectionBase.__init__
		ChannelSelectionBase.__init__ = new_ChannelSelectionBase__init__
		ChannelSelectionBase.AltCountChanged = new_AltCountChanged
	if base_keyNumberGlobal is None:
		base_keyNumberGlobal = InfoBarNumberZap.keyNumberGlobal
		InfoBarNumberZap.keyNumberGlobal = new_keyNumberGlobal

def OpenSetup(session, **kwargs):
	import NumberZapExtSetup
	session.open(NumberZapExtSetup.NumberZapExtSetupScreen)

def StartSetup(menuid, **kwargs):
	if menuid == "system":
		return [(_("Extended NumberZap"), OpenSetup, "numzapext_setup", None)]
	else:
		return []


def Plugins(**kwargs):
	return [PluginDescriptor(name=_("Extended NumberZap"), description=_("Extended NumberZap addon"), where = PluginDescriptor.WHERE_SESSIONSTART, fnc = StartMainSession),
		PluginDescriptor(name=_("Extended NumberZap"), description=_("Extended NumberZap addon"), where = PluginDescriptor.WHERE_MENU, fnc = StartSetup)]

