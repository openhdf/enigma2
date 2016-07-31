#
# Extended NumberZap Plugin for Enigma2
# Coded by vlamo (c) 2011,2012
#
# Version: 1.0-rc3 (06.02.2012 16:05)
# Support: http://dream.altmaster.net/
#

from . import _
from Screens.Screen import Screen
from Components.Sources.StaticText import StaticText
from Components.ActionMap import ActionMap, NumberActionMap
from Components.ConfigList import ConfigListScreen
from Components.config import config, getConfigListEntry, ConfigSubsection
from Components.FileList import FileList




class DirectoryBrowser(Screen):
	skin = """<screen name="DirectoryBrowser" position="center,center" size="520,440" title="Directory browser" >
			<ePixmap pixmap="skin_default/buttons/red.png" position="0,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/green.png" position="140,0" size="140,40" alphatest="on" />
			<widget source="key_red" render="Label" position="0,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
			<widget source="key_green" render="Label" position="140,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
			<widget source="curdir" render="Label" position="5,50" size="510,20"  font="Regular;20" halign="left" valign="center" backgroundColor="background" transparent="1" noWrap="1" />
			<widget name="filelist" position="5,80" size="510,345" scrollbarMode="showOnDemand" />
		</screen>"""
	
	def __init__(self, session, curdir, matchingPattern=None):
		Screen.__init__(self, session)

		self["key_red"] = StaticText(_("Cancel"))
		self["key_green"] = StaticText(_("Save"))
		self["curdir"] = StaticText("current:  %s"%(curdir or ''))

		self.filelist = FileList(curdir, matchingPattern=matchingPattern, enableWrapAround=True)
		self.filelist.onSelectionChanged.append(self.__selChanged)
		self["filelist"] = self.filelist

		self["FilelistActions"] = ActionMap(["SetupActions", "ColorActions"],
			{
				"green": self.keyGreen,
				"red": self.keyRed,
				"ok": self.keyOk,
				"cancel": self.keyRed
			})
		self.onLayoutFinish.append(self.__layoutFinished)

	def __layoutFinished(self):
		#self.setTitle(_("Directory browser"))
		pass

	def getCurrentSelected(self):
		dirname = self.filelist.getCurrentDirectory()
		filename = self.filelist.getFilename()
		if not filename and not dirname:
			cur = ''
		elif not filename:
			cur = dirname
		elif not dirname:
			cur = filename
		else:
			if not self.filelist.canDescent() or len(filename) <= len(dirname):
				cur = dirname
			else:
				cur = filename
		return cur or ''

	def __selChanged(self):
		self["curdir"].setText("current:  %s"%(self.getCurrentSelected()))

	def keyOk(self):
		if self.filelist.canDescent():
			self.filelist.descent()

	def keyGreen(self):
		self.close(self.getCurrentSelected())

	def keyRed(self):
		self.close(False)




class NumberZapExtSetupScreen(Screen, ConfigListScreen):
	def __init__(self, session, args = None):
		Screen.__init__(self, session)
		self.skinName = ["NumberZapExtSetup", "Setup"]
		self.setup_title = _("Extended NumberZap Setup")

		self["key_green"] = StaticText(_("Save"))
		self["key_red"] = StaticText(_("Cancel"))
		self["actions"] = NumberActionMap(["SetupActions"],
		{
			"cancel": self.keyRed,	# KEY_RED, KEY_EXIT
			"ok": self.keyOk,	# KEY_OK
			"save": self.keyGreen,	# KEY_GREEN
		}, -1)

		ConfigListScreen.__init__(self, [])

		self.initConfig()
		self.createSetup()

		self.onClose.append(self.__closed)
		self.onLayoutFinish.append(self.__layoutFinished)

	def __closed(self):
		pass

	def __layoutFinished(self):
		self.setTitle(self.setup_title)

	def initConfig(self):
		def getPrevValues(section):
			res = { }
			for (key,val) in section.content.items.items():
				if isinstance(val, ConfigSubsection):
					res[key] = getPrevValues(val)
				else:
					res[key] = val.value
			return res
		
		self.NZE = config.plugins.NumberZapExt
		self.prev_values = getPrevValues(self.NZE)
		self.cfg_enable = getConfigListEntry(_("enable extended number zap"), self.NZE.enable)
		self.cfg_kdelay = getConfigListEntry(_("time to wait next keypress (millisecond)"), self.NZE.kdelay)
		self.cfg_acount = getConfigListEntry(_("alternative service counter in bouquets"), self.NZE.acount)
		self.cfg_picons = getConfigListEntry(_("enable picons"), self.NZE.picons)
		self.cfg_picondir = getConfigListEntry(_("picons directory:"), self.NZE.picondir)
		self.cfg_hotkey = getConfigListEntry(_("enable number hotkeys"), self.NZE.hotkey)

	def createSetup(self):
		list = [ self.cfg_enable ]
		if self.NZE.enable.value:
			list.append(self.cfg_kdelay)
			list.append(self.cfg_acount)
			list.append(self.cfg_picons)
			if self.NZE.picons.value:
				list.append(self.cfg_picondir)
			list.append(self.cfg_hotkey)
			if self.NZE.hotkey.value:
				list.append(getConfigListEntry(_("confirmation on hotkey action"), self.NZE.action.confirm))
				list.append(getConfigListEntry(_("Shutdown"), self.NZE.action.shutdown))
				list.append(getConfigListEntry(_("Reboot"), self.NZE.action.reboot))
				list.append(getConfigListEntry(_("Restart GUI"), self.NZE.action.restart))
				list.append(getConfigListEntry(_("Standby"), self.NZE.action.standby))
				list.append(getConfigListEntry(_("Plugins"), self.NZE.action.plugins))
				list.append(getConfigListEntry(_("Service Info"), self.NZE.action.service_info))
		self["config"].list = list
		self["config"].l.setList(list)

	def newConfig(self):
		cur = self["config"].getCurrent()
		if cur in (self.cfg_enable, self.cfg_hotkey, self.cfg_picons):
			self.createSetup()
		elif cur == self.cfg_picondir:
			self.keyOk()

	def keyOk(self):
		cur = self["config"].getCurrent()
		if cur == self.cfg_picondir:
			self.session.openWithCallback(self.directoryBrowserClosed, DirectoryBrowser, self.NZE.picondir.value, "^.*\.png")

	def directoryBrowserClosed(self, path):
		if path != False:
			self.NZE.picondir.setValue(path)

	def keyRed(self):
		def setPrevValues(section, values):
			for (key,val) in section.content.items.items():
				value = values.get(key, None)
				if value is not None:
					if isinstance(val, ConfigSubsection):
						setPrevValues(val, value)
					else:
						val.value = value
		
		setPrevValues(self.NZE, self.prev_values)
		self.keyGreen()

	def keyGreen(self):
		if not self.NZE.enable.value:
			self.NZE.acount.value = False
		self.NZE.save()
		self.close()

	def keyLeft(self):
		ConfigListScreen.keyLeft(self)
		self.newConfig()

	def keyRight(self):
		ConfigListScreen.keyRight(self)
		self.newConfig()

