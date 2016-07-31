# -*- coding: utf-8 -*-

#This plugin is free software, you are allowed to
#modify it (if you keep the license),
#but you are not allowed to distribute/publish
#it without source code (this version and your modifications).
#This means you also have to distribute
#source code of your modifications.

from Components.ActionMap import ActionMap
from Components.MenuList import MenuList
from Components.Label import Label
from Components.PluginComponent import plugins
from Components.config import config, ConfigSubsection, ConfigYesNo, ConfigLocations, ConfigText, ConfigSelection, getConfigListEntry, ConfigInteger
from Components.ConfigList import ConfigListScreen
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.ChoiceBox import ChoiceBox
from Screens.Console import Console
from Screens.LocationBox import LocationBox
from Components.Sources.List import List
from Plugins.Plugin import PluginDescriptor
from Screens.Standby import TryQuitMainloop
from QuickButtonList import QuickButtonList, QuickButtonListEntry
from QuickButtonXML import QuickButtonXML
from enigma import getDesktop
from Tools.Directories import *
import xml.sax.xmlreader
import keymapparser
import os
import os.path
from __init__ import _

functionfile = "/usr/lib/enigma2/python/Plugins/Extensions/MultiQuickButton/mqbfunctions.xml"
config.plugins.QuickButton = ConfigSubsection()
config.plugins.QuickButton.enable = ConfigYesNo(default = True)
config.plugins.QuickButton.info = ConfigYesNo(default = True)
config.plugins.QuickButton.okexitstate = ConfigYesNo(default = False)
config.plugins.QuickButton.mainmenu = ConfigYesNo(default = True)
config.plugins.QuickButton.last_backupdir = ConfigText(default=resolveFilename(SCOPE_SYSETC))
config.plugins.QuickButton.backupdirs = ConfigLocations(default=[resolveFilename(SCOPE_SYSETC)])
config.plugins.QuickButton.channel1 = ConfigInteger(default = 1, limits = (0, 9999))
config.plugins.QuickButton.channel2 = ConfigInteger(default = 2, limits = (0, 9999))
config.plugins.QuickButton.channel3 = ConfigInteger(default = 3, limits = (0, 9999))
config.plugins.QuickButton.channel4 = ConfigInteger(default = 4, limits = (0, 9999))
config.plugins.QuickButton.channel5 = ConfigInteger(default = 5, limits = (0, 9999))
config.plugins.QuickButton.macroI = ConfigText(default = "")
config.plugins.QuickButton.macroII = ConfigText(default = "")
config.plugins.QuickButton.macroIII = ConfigText(default = "")
config.plugins.QuickButton.macroIV = ConfigText(default = "")
config.plugins.QuickButton.macroV = ConfigText(default = "")
MultiQuickButton_version = "2.7.12"
autostart=_("Autostart") + ": "
menuentry=_("Main menu") + ": "
info=_("Info") + ": "
okexit=_("OK/EXIT") + ": "

values = ("red","red_long","green","green_long","yellow","yellow_long","blue","blue_long","pvr","pvr_long","radio","radio_long","text","text_long", \
			"epg","epg_long","help","help_long","info","info_long","end","end_long","home","home_long","cross_up","cross_down","cross_left","cross_right","previous","next", \
			"channelup","channeldown","audio","ok","exit","play","pause","fastforward","stop","rewind","tv", \
			'console','f1','f2','f3','f4','web','mail','m1','m2',"fav", "fav_long", "screen", "screen_long", "history", "history_long", \
			"subtitle","subtitle_long","filelist","filelist_long","playlist","playlist_long","timer","timer_long", \
			"timeshift","timeshift_long","mark","mark_long","search","search_long","slow","slow_long")

class MultiQuickButton(Screen):

	global HD_Res

	try:
		sz_w = getDesktop(0).size().width()
	except:
		sz_w = 720

	if sz_w == 1280:
		HD_Res = True
	else:
		HD_Res = False

	if HD_Res:
		skin = """
		<screen position="240,100" size="800,520" title="MultiQuickButton Panel %s" >
			<widget name="list" position="10,10" size="780,410" scrollbarMode="showOnDemand" />
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MultiQuickButton/pic/button_red.png" zPosition="2" position="20,450" size="25,25" alphatest="on" />
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MultiQuickButton/pic/button_green.png" zPosition="2" position="210,450" size="25,25" alphatest="on" />
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MultiQuickButton/pic/button_yellow.png" zPosition="2" position="420,450" size="25,25" alphatest="on" />
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MultiQuickButton/pic/button_blue.png" zPosition="2" position="610,450" size="25,25" alphatest="on" />
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MultiQuickButton/pic/key_0.png" zPosition="2" position="15,490" size="35,25" alphatest="on" />
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MultiQuickButton/pic/key_1.png" zPosition="2" position="205,490" size="35,25" alphatest="on" />
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MultiQuickButton/pic/key_2.png" zPosition="2" position="415,490" size="35,25" alphatest="on" />
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MultiQuickButton/pic/key_3.png" zPosition="2" position="605,490" size="35,25" alphatest="on" />
			<widget name="key_red" backgroundColor="#1f771f" zPosition="2" position="50,445" size="180,40" font="Regular;20" halign="left" valign="center" transparent="1" />
			<widget name="key_green" backgroundColor="#1f771f" position="240,445" zPosition="2" size="180,40" font="Regular;20" halign="left" valign="center" transparent="1" />
			<widget name="key_yellow" backgroundColor="#1f771f" position="450,445" zPosition="2"  size="180,40" font="Regular;20" halign="left" valign="center" transparent="1" />
			<widget name="key_blue" backgroundColor="#1f771f" position="640,445" zPosition="2"  size="180,40" font="Regular;20" halign="left" valign="center" transparent="1" />
			<widget name="key_0" backgroundColor="#1f771f" zPosition="2" position="50,484" size="180,40" font="Regular;20" halign="left" valign="center" transparent="1" />
			<widget name="key_1" backgroundColor="#1f771f" position="240,484" zPosition="2" size="180,40" font="Regular;20" halign="left" valign="center" transparent="1" />
			<widget name="key_2" backgroundColor="#1f771f" position="450,484" zPosition="2"  size="180,40" font="Regular;20" halign="left" valign="center" transparent="1" />
			<widget name="key_3" backgroundColor="#1f771f" position="640,484" zPosition="2"  size="180,40" font="Regular;20" halign="left" valign="center" transparent="1" />
			<widget name="background" backgroundColor="#220a0a0a" zPosition="1" position="0,450" size="800,80" font="Regular;20" halign="left" valign="center" />
		</screen>""" % (MultiQuickButton_version)
	else:
		skin = """
		<screen position="50,190" size="620,320" title="MultiQuickButton Panel %s" >
			<widget name="list" position="10,10" size="600,210" scrollbarMode="showOnDemand" />
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MultiQuickButton/pic/button_red.png" zPosition="2" position="10,250" size="25,25" alphatest="on" />
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MultiQuickButton/pic/button_green.png" zPosition="2" position="160,250" size="25,25" alphatest="on" />
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MultiQuickButton/pic/button_yellow.png" zPosition="2" position="330,250" size="25,25" alphatest="on" />
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MultiQuickButton/pic/button_blue.png" zPosition="2" position="490,250" size="25,25" alphatest="on" />
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MultiQuickButton/pic/key_0.png" zPosition="2" position="6,290" size="35,25" alphatest="on" />
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MultiQuickButton/pic/key_1.png" zPosition="2" position="156,290" size="35,25" alphatest="on" />
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MultiQuickButton/pic/key_2.png" zPosition="2" position="326,290" size="35,25" alphatest="on" />
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MultiQuickButton/pic/key_3.png" zPosition="2" position="486,290" size="35,25" alphatest="on" />
			<widget name="key_red" backgroundColor="#1f771f" zPosition="2" position="35,245" size="250,40" font="Regular;20" halign="left" valign="center" transparent="1" />
			<widget name="key_green" backgroundColor="#1f771f" position="185,245" zPosition="2" size="250,40" font="Regular;20" halign="left" valign="center" transparent="1" />
			<widget name="key_yellow" backgroundColor="#1f771f" position="355,245" zPosition="2"  size="150,40" font="Regular;20" halign="left" valign="center" transparent="1" />
			<widget name="key_blue" backgroundColor="#1f771f" position="515,245" zPosition="2"  size="150,40" font="Regular;20" halign="left" valign="center" transparent="1" />
			<widget name="key_0" backgroundColor="#1f771f" position="35,285" zPosition="2" size="250,40" font="Regular;20" halign="left" valign="center" transparent="1" />
			<widget name="key_1" backgroundColor="#1f771f" position="185,285" zPosition="2" size="250,40" font="Regular;20" halign="left" valign="center" transparent="1" />
			<widget name="key_2" backgroundColor="#1f771f" position="355,285" zPosition="2"  size="150,40" font="Regular;20" halign="left" valign="center" transparent="1" />
			<widget name="key_3" backgroundColor="#1f771f" position="515,285" zPosition="2"  size="150,40" font="Regular;20" halign="left" valign="center" transparent="1" />
			<widget name="background" backgroundColor="#220a0a0a" zPosition="1" position="0,320" size="620,80" font="Regular;20" halign="left" valign="center" />
		</screen>""" % (MultiQuickButton_version)

	def __init__(self, session, args=None):
		Screen.__init__(self, session)
		self.session = session
		self.menu = args
		self.settigspath = ""
		

		self["background"] = Label('')
		self["key_red"] = Label(autostart)
		self["key_green"] = Label(menuentry)
		self["key_yellow"] = Label(_("Restore"))
		self["key_blue"] = Label(_("Backup"))
		self["key_0"] = Label(info)
		self["key_1"] = Label(okexit)
		self["key_2"] = Label(_("Channels"))
		self["key_3"] = Label(_("Macros"))
		self.createList()
		self["list"] = QuickButtonList(list=self.list, selection = 0)
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "NumberActions", "EPGSelectActions"],
		{
			"ok": self.run,
			"cancel": self.close,
			"red": self.autostart,
			"green": self.setMainMenu,
			"yellow": self.restore,
			"blue": self.backup,
			"0": self.setInfo,
			"1": self.toggleOkExit,
			"2": self.setChannels,
			"3": self.configMacro,
			"info": self.showAbout,
		}, -1)
		self.onShown.append(self.updateSettings)
		
	def createList(self):
		self.a = None
		for button in values:
			if config.plugins.QuickButton.info.value:
				try:
					functionbutton = " ["
					path = "/etc/MultiQuickButton/quickbutton_" + button + ".xml"
					menu = xml.dom.minidom.parse(path)
					self.XML_db = QuickButtonXML(menu)
					for a in self.XML_db.getMenu():
						if a[1] == "1":
							if functionbutton == " [":
								functionbutton = _(a[0])
							else:
								functionbutton = functionbutton + " | " + _(a[0])
					if functionbutton == " [":
						space1 = " "
						space2 = " "
						functionbutton = " "
					else:
						space1 = " ["
						space2 = "]"
					globals()['functionbutton_%s' % button] = space1 + functionbutton + space2
					
				except Exception, a:
					self.a = a
			else:
				globals()['functionbutton_%s' % button] = " "
		self.list = []
		self.list.append(QuickButtonListEntry('',(_('red') + functionbutton_red, 'red')))
		self.list.append(QuickButtonListEntry('',((_('red') + _(' long')) + functionbutton_red_long, 'red_long')))
		self.list.append(QuickButtonListEntry('',(_('green') + functionbutton_green, 'green')))
		self.list.append(QuickButtonListEntry('',((_('green') + _(' long')) + functionbutton_green_long, 'green_long')))
		self.list.append(QuickButtonListEntry('',(_('yellow') + functionbutton_yellow, 'yellow')))
		self.list.append(QuickButtonListEntry('',((_('yellow') + _(' long')) + functionbutton_yellow_long, 'yellow_long')))
		self.list.append(QuickButtonListEntry('',(_('blue') + functionbutton_blue, 'blue')))
		self.list.append(QuickButtonListEntry('',((_('blue') + _(' long')) + functionbutton_blue_long, 'blue_long')))
                self.list.append(QuickButtonListEntry('',(_('Console (kbd)') + functionbutton_console, 'console')))
                self.list.append(QuickButtonListEntry('',(_('F1') + functionbutton_f1, 'f1')))
                self.list.append(QuickButtonListEntry('',(_('F2') + functionbutton_f2, 'f2')))
                self.list.append(QuickButtonListEntry('',(_('F3') + functionbutton_f3, 'f3')))
                self.list.append(QuickButtonListEntry('',(_('F4') + functionbutton_f4, 'f4')))
                self.list.append(QuickButtonListEntry('',(_('F6 (kbd) WWW') + functionbutton_web, 'web')))
                self.list.append(QuickButtonListEntry('',(_('F7 (kbd) MAIL') + functionbutton_mail, 'mail')))
                self.list.append(QuickButtonListEntry('',(_('F10 (kbd) M2') + functionbutton_m2, 'm2')))
                self.list.append(QuickButtonListEntry('',(_('F11 (kbd) M1') + functionbutton_m1, 'm1')))
                self.list.append(QuickButtonListEntry('',(_('FAV') + functionbutton_fav, 'fav')))
                self.list.append(QuickButtonListEntry('',((_('FAV') + _(' long')) + functionbutton_fav_long, 'fav_long')))
                self.list.append(QuickButtonListEntry('',(_('SCREEN') + functionbutton_screen, 'screen')))
                self.list.append(QuickButtonListEntry('',((_('SCREEN') + _(' long')) + functionbutton_screen_long, 'screen_long')))
                #self.list.append(QuickButtonListEntry('',(_('TimerDot') + functionbutton_timer, 'timer')))
                #self.list.append(QuickButtonListEntry('',((_('TimerDot') + _(' long')) + functionbutton_timer_long, 'timer_long')))
                self.list.append(QuickButtonListEntry('',(_('HISTORY') + functionbutton_history, 'history')))
                self.list.append(QuickButtonListEntry('',((_('HISTORY') + _(' long')) + functionbutton_history_long, 'history_long')))
                self.list.append(QuickButtonListEntry('',(_('subtitle') + functionbutton_subtitle, 'subtitle')))
                self.list.append(QuickButtonListEntry('',((_('subtitle') + _(' long')) + functionbutton_subtitle_long, 'subtitle_long')))
                self.list.append(QuickButtonListEntry('',(_('TEXT') + functionbutton_text, 'text')))
                self.list.append(QuickButtonListEntry('',((_('TEXT') + _(' long')) + functionbutton_text_long, 'text_long')))
                self.list.append(QuickButtonListEntry('',(_('EPG') + functionbutton_epg, 'epg')))
                self.list.append(QuickButtonListEntry('',((_('EPG') + _(' long')) + functionbutton_epg_long, 'epg_long')))
		#self.list.append(QuickButtonListEntry('',(_('HELP') + functionbutton_help, 'help')))
		#self.list.append(QuickButtonListEntry('',((_('HELP') + _(' long')) + functionbutton_help_long, 'help_long')))
		self.list.append(QuickButtonListEntry('',(_('INFO') + functionbutton_info, 'info')))
		self.list.append(QuickButtonListEntry('',((_('INFO') + _(' long')) + functionbutton_info_long, 'info_long')))
		#self.list.append(QuickButtonListEntry('',(_('HOME') + functionbutton_home, 'home')))
		#self.list.append(QuickButtonListEntry('',((_('HOME') + _(' long')) + functionbutton_home_long, 'home_long')))
		#self.list.append(QuickButtonListEntry('',(_('END') + functionbutton_end, 'end')))
		#self.list.append(QuickButtonListEntry('',((_('END') + _(' long')) + functionbutton_end_long, 'end_long')))
		self.list.append(QuickButtonListEntry('',(_('VIDEO') + functionbutton_pvr, 'pvr')))
		self.list.append(QuickButtonListEntry('',((_('VIDEO') + _(' long')) + functionbutton_pvr_long, 'pvr_long')))
		self.list.append(QuickButtonListEntry('',(_('RADIO') + functionbutton_radio, 'radio')))
		self.list.append(QuickButtonListEntry('',((_('RADIO') + _(' long')) + functionbutton_radio_long, 'radio_long')))
		self.list.append(QuickButtonListEntry('',(_('TV') + functionbutton_tv, 'tv')))
		self.list.append(QuickButtonListEntry('',(_('Cross Up') + functionbutton_cross_up, 'cross_up')))
		self.list.append(QuickButtonListEntry('',(_('Cross Down') + functionbutton_cross_down, 'cross_down')))
		self.list.append(QuickButtonListEntry('',(_('Cross Left') + functionbutton_cross_left, 'cross_left')))
		self.list.append(QuickButtonListEntry('',(_('Cross Right') + functionbutton_cross_right, 'cross_right')))
		self.list.append(QuickButtonListEntry('',(_('Channel +') + functionbutton_channelup, 'channelup')))
		self.list.append(QuickButtonListEntry('',(_('Channel -') + functionbutton_channeldown, 'channeldown')))
		self.list.append(QuickButtonListEntry('',(_('Forward >') + functionbutton_next, 'next')))
		self.list.append(QuickButtonListEntry('',(_('Backward <') + functionbutton_previous, 'previous')))
		self.list.append(QuickButtonListEntry('',(_('Audio') + functionbutton_audio, 'audio')))
		if config.plugins.QuickButton.okexitstate.value:
			self.list.append(QuickButtonListEntry('',('OK' + functionbutton_ok, 'ok')))
			self.list.append(QuickButtonListEntry('',(_('EXIT') + functionbutton_exit, 'exit')))
		self.list.append(QuickButtonListEntry('',(_('Play') + functionbutton_play, 'play')))
		self.list.append(QuickButtonListEntry('',(_('Pause') + functionbutton_pause, 'pause')))
		self.list.append(QuickButtonListEntry('',(_('Stop') + functionbutton_stop, 'stop')))
		self.list.append(QuickButtonListEntry('',(_('Rewind <<') + functionbutton_rewind, 'rewind')))
		self.list.append(QuickButtonListEntry('',(_('FastForward >>') + functionbutton_fastforward, 'fastforward')))
		self.list.append(QuickButtonListEntry('',(_('F.List') + functionbutton_filelist, 'filelist')))
		self.list.append(QuickButtonListEntry('',((_('F.List') + _(' long')) + functionbutton_filelist_long, 'filelist_long')))
		self.list.append(QuickButtonListEntry('',(_('G.List') + functionbutton_playlist, 'playlist')))
		self.list.append(QuickButtonListEntry('',((_('G.List') + _(' long')) + functionbutton_playlist_long, 'playlist_long')))
		#self.list.append(QuickButtonListEntry('',(_('Timeshift') + functionbutton_timeshift, 'timeshift')))
		#self.list.append(QuickButtonListEntry('',((_('Timeshift') + _(' long')) + functionbutton_timeshift_long, 'timeshift_long')))
		#self.list.append(QuickButtonListEntry('',(_('Mark') + functionbutton_mark, 'mark')))
		#self.list.append(QuickButtonListEntry('',((_('Mark') + _(' long')) + functionbutton_mark_long, 'mark_long')))
		#self.list.append(QuickButtonListEntry('',(_('search') + functionbutton_search, 'search')))
		#self.list.append(QuickButtonListEntry('',((_('search') + _(' long')) + functionbutton_search_long, 'search_long')))
		#self.list.append(QuickButtonListEntry('',(_('SLOW I>') + functionbutton_slow, 'slow')))
		#self.list.append(QuickButtonListEntry('',((_('SLOW I>') + _(' long')) + functionbutton_slow_long, 'slow_long')))

		
	def updateList(self):
		self.createList()
		self["list"].l.setList(self.list)

	def updateSettings(self):
		autostart_state = autostart
		menuentry_state = menuentry
		info_state = info
		okexit_state = okexit
		if config.plugins.QuickButton.enable.value:
			autostart_state += _("on")
		else:
			autostart_state += _("off")

		if config.plugins.QuickButton.mainmenu.value:
			menuentry_state += _("on")
		else:
			menuentry_state += _("off")

		if config.plugins.QuickButton.info.value:
			info_state += _("on")
		else:
			info_state += _("off")

		if config.plugins.QuickButton.okexitstate.value:
			okexit_state += _("on")
		else:
			okexit_state += _("off")

		self["key_red"].setText(autostart_state)
		self["key_green"].setText(menuentry_state)
		self["key_0"].setText(info_state)
		self["key_1"].setText(okexit_state)

	def run(self):
		returnValue = self["list"].l.getCurrentSelection()[0][1]
		if returnValue is not None:
			if returnValue in values:
				path = '/etc/MultiQuickButton/quickbutton_' + returnValue + '.xml'
				if os.path.exists(path) is True:
					self.session.openWithCallback(self.updateAfterButtonChange, QuickButton, path, (_("Quickbutton Key : ") + _(returnValue)))
				else:
					self.session.open(MessageBox,("file %s not found!" % (path)),  MessageBox.TYPE_ERROR)

	def updateAfterButtonChange(self, res = None):
		self.updateList()

	def backup(self):
		self.session.openWithCallback(
			self.callBackup,
			BackupLocationBox,
			_("Please select the backup path..."),
			"",
			config.plugins.QuickButton.last_backupdir.value
		)

	def callBackup(self, path):
		if path is not None:
			if pathExists(path):
				config.plugins.QuickButton.last_backupdir.value = path
				config.plugins.QuickButton.last_backupdir.save()
				self.settigspath = path + "MultiQuickButton_settings.tar.gz"
				if fileExists(self.settigspath):
					self.session.openWithCallback(self.callOverwriteBackup, MessageBox,_("Overwrite existing Backup?."),type = MessageBox.TYPE_YESNO,)
				else:
					com = "tar czvf %s /etc/MultiQuickButton/" % (self.settigspath)
					self.session.open(Console,_("Backup Settings..."),[com])
			else:
				self.session.open(
					MessageBox,
					_("Directory %s nonexistent.") % (path),
					type = MessageBox.TYPE_ERROR,
					timeout = 5
					)

	def callOverwriteBackup(self, res):
		if res:
			com = "tar czvf %s /etc/MultiQuickButton/" % (self.settigspath)
			self.session.open(Console,_("Backup Settings..."),[com])

	def restore(self):
		self.session.openWithCallback(
			self.callRestore,
			BackupLocationBox,
			_("Please select the restore path..."),
			"",
			config.plugins.QuickButton.last_backupdir.value
		)

	def callRestore(self, path):
		if path is not None:
			self.settigspath = path + "MultiQuickButton_settings.tar.gz"
			if fileExists(self.settigspath):
				self.session.openWithCallback(self.callOverwriteSettings, MessageBox,_("Overwrite existing Settings?."),type = MessageBox.TYPE_YESNO,)
			else:
				self.session.open(MessageBox,_("File %s nonexistent.") % (path),type = MessageBox.TYPE_ERROR,timeout = 5)
		else:
			pass

	def callOverwriteSettings(self, res):
		if res:
			com = "cd /; tar xzvf %s" % (self.settigspath)
			self.session.open(Console,_("Restore Settings..."),[com])

	def autostart(self):
		if config.plugins.QuickButton.enable.value:
			config.plugins.QuickButton.enable.setValue(False)
			config.plugins.QuickButton.mainmenu.setValue(False)
		else:
			config.plugins.QuickButton.enable.setValue(True)

		self.updateSettings()
		config.plugins.QuickButton.enable.save()
		self.session.openWithCallback(self.callRestart,MessageBox,_("Restarting Enigma2 to set\nMulti QuickButton Autostart"), MessageBox.TYPE_YESNO, timeout=10)

	def setMainMenu(self):
		if config.plugins.QuickButton.mainmenu.value:
			config.plugins.QuickButton.mainmenu.setValue(False)
		else:
			config.plugins.QuickButton.mainmenu.setValue(True)

		config.plugins.QuickButton.mainmenu.save()
		self.updateSettings()
		self.session.openWithCallback(self.callRestart,MessageBox,_("Restarting Enigma2 to load:\n") + _("Main menu") + _("Multi QuickButton settings"), MessageBox.TYPE_YESNO, timeout=10)

	def setInfo(self):
		if config.plugins.QuickButton.info.value:
			config.plugins.QuickButton.info.setValue(False)
		else:
			config.plugins.QuickButton.info.setValue(True)

		config.plugins.QuickButton.info.save()
		self.updateList()
		self.updateSettings()

	def toggleOkExit(self):
		self.mqbkeymapfile = "/usr/lib/enigma2/python/Plugins/Extensions/MultiQuickButton/keymap.xml"
		self.mqbkeymap = open(self.mqbkeymapfile, "r")
		self.text = self.mqbkeymap.read()
		self.mqbkeymap.close()
		self.keys = [	"<key id=\"KEY_OK\" mapto=\"ok\" flags=\"m\" />", \
				"<key id=\"KEY_EXIT\" mapto=\"exit\" flags=\"m\" />" ]

		if config.plugins.QuickButton.okexitstate.value:
			config.plugins.QuickButton.okexitstate.setValue(False)
			for self.key in self.keys:
				self.keyinactive = "<!-- " + self.key + " -->"
				if not self.keyinactive in self.text:
					self.text = self.text.replace(self.key, self.keyinactive)
		else:
			config.plugins.QuickButton.okexitstate.setValue(True)
			for self.key in self.keys:
				self.keyinactive = "<!-- " + self.key + " -->"
				if self.keyinactive in self.text:
					self.text = self.text.replace(self.keyinactive, self.key)

		self.mqbkeymap = open(self.mqbkeymapfile, "w")
		self.mqbkeymap.write(self.text)
		self.mqbkeymap.close()
		keymapparser.removeKeymap(self.mqbkeymapfile)
		keymapparser.readKeymap(self.mqbkeymapfile)
		config.plugins.QuickButton.okexitstate.save()
		self.updateList()
		self.updateSettings()

	def setChannels(self):
		self.session.open(MultiQuickButtonChannelConfiguration)

	def configMacro(self):
		self.session.open(MultiQuickButtonMacro)

	def showAbout(self):
		self.session.open(MessageBox,("Multi Quickbutton idea is based on\nGP2\'s Quickbutton\nVersion: 2.7\nby Emanuel CLI-Team 2009\nwww.cablelinux.info\n ***special thanks*** to:\ngutemine & AliAbdul & Dr.Best ;-)\n\nChanges for Gigablue by scp\nsome@email.org\nwww.homepage.org\nVersion %s" % (MultiQuickButton_version)),  MessageBox.TYPE_INFO)
  
	def callRestart(self, restart):
		if restart == True:
			self.session.open(TryQuitMainloop, 3)
		else:
			pass

class BackupLocationBox(LocationBox):
	def __init__(self, session, text, filename, dir, minFree = None):
		inhibitDirs = ["/bin", "/boot", "/dev", "/lib", "/proc", "/sbin", "/sys", "/usr", "/var"]
		LocationBox.__init__(self, session, text = text, filename = filename, currDir = dir, bookmarks = config.plugins.QuickButton.backupdirs, autoAdd = True, editDir = True, inhibitDirs = inhibitDirs, minFree = minFree)
		self.skinName = "LocationBox"

class QuickButton(Screen):

	global HD_Res

	try:
		sz_w = getDesktop(0).size().width()
	except:
		sz_w = 720

	if sz_w == 1280:
		HD_Res = True
	else:
		HD_Res = False

	if HD_Res:
		skin = """
		<screen position="240,100" size="800,520" title="QuickButton" >
			<widget name="list" position="10,10" size="780,450" scrollbarMode="showOnDemand" />
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MultiQuickButton/pic/button_red.png" zPosition="2" position="15,487" size="25,25" alphatest="on" />
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MultiQuickButton/pic/button_green.png" zPosition="2" position="205,487" size="25,25" alphatest="on" />
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MultiQuickButton/pic/button_yellow.png" zPosition="2" position="395,487" size="25,25" alphatest="on" />
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MultiQuickButton/pic/button_blue.png" zPosition="2" position="585,487" size="25,25" alphatest="on" />
			<widget name="key_red" backgroundColor="#1f771f" zPosition="2" position="50,480" size="180,40" font="Regular;20" halign="left" valign="center" transparent="1" />
			<widget name="key_green" backgroundColor="#1f771f" position="240,480" zPosition="2" size="180,40" font="Regular;20" halign="left" valign="center" transparent="1" />
			<widget name="key_yellow" backgroundColor="#1f771f" position="430,480" zPosition="2"  size="180,40" font="Regular;20" halign="left" valign="center" transparent="1" />
			<widget name="key_blue" backgroundColor="#1f771f" position="620,480" zPosition="2"  size="180,40" font="Regular;20" halign="left" valign="center" transparent="1" />
			<widget name="background" backgroundColor="#220a0a0a" zPosition="1" position="0,480" size="800,40" font="Regular;20" halign="left" valign="center" />
		</screen>"""
	else:
		skin = """
		<screen position="60,90" size="600,420" title="QuickButton" >
			<widget name="list" position="10,10" size="580,350" scrollbarMode="showOnDemand" />
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MultiQuickButton/pic/button_red.png" zPosition="2" position="15,387" size="25,25" alphatest="on" />
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MultiQuickButton/pic/button_green.png" zPosition="2" position="155,387" size="25,25" alphatest="on" />
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MultiQuickButton/pic/button_yellow.png" zPosition="2" position="295,387" size="25,25" alphatest="on" />
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MultiQuickButton/pic/button_blue.png" zPosition="2" position="435,387" size="25,25" alphatest="on" />
			<widget name="key_red" backgroundColor="#1f771f" zPosition="2" position="40,380" size="150,40" font="Regular;20" halign="left" valign="center" transparent="1" />
			<widget name="key_green" backgroundColor="#1f771f" position="180,380" zPosition="2" size="150,40" font="Regular;20" halign="left" valign="center" transparent="1" />
			<widget name="key_yellow" backgroundColor="#1f771f" position="320,380" zPosition="2"  size="150,40" font="Regular;20" halign="left" valign="center" transparent="1" />
			<widget name="key_blue" backgroundColor="#1f771f" position="460,380" zPosition="2"  size="150,40" font="Regular;20" halign="left" valign="center" transparent="1" />
			<widget name="background" backgroundColor="#220a0a0a" zPosition="1" position="0,380" size="600,40" font="Regular;20" halign="left" valign="center" />
		</screen>"""

	def __init__(self, session, path=None, title = "" ):
		Screen.__init__(self, session)
		self.session = session
		self.path = path
		self.newtitle = title
		self.changed = False
		self.e = None
		list = []
		try:
			menu = xml.dom.minidom.parse(self.path)
			self.XML_db = QuickButtonXML(menu)
			for e in self.XML_db.getMenu():
				if e[1] == "1":
					list.append(QuickButtonListEntry('green',(_(e[0]),e[0], '1')))
					
				else:
					list.append(QuickButtonListEntry('red',(_(e[0]),e[0], '')))
					
		except Exception, e:
			self.e = e
			list = []

		self["list"] = QuickButtonList(list=list, selection = 0)
		self["background"] = Label('')
		self["key_red"] = Label(_("Cancel"))
		self["key_green"] = Label(_("Save"))
		self["key_yellow"] = Label(_("delete"))
		self["key_blue"] = Label(_("Add"))
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "DirectionActions"], 
		{
			"ok": self.run,
			"cancel": self.cancel,
			"red": self.close,
			"green": self.save,
			"yellow": self.delete,
			"blue": self.add,
			"up": self.up,
			"down": self.down,
			"left": self.keyLeft,
			"right": self.keyRight
		}, -1)
		self.onExecBegin.append(self.error)
		self.onShown.append(self.updateTitle)

	def error(self):
		if self.e:
			self.session.open(MessageBox,("XML " + _("Error") + ": %s" % self.e),  MessageBox.TYPE_ERROR)
			self.close(None)

			
	def updateTitle(self):
		self.setTitle(self.newtitle)

	def run(self):
		returnValue = self["list"].l.getCurrentSelection()[0][2]
		name = self["list"].l.getCurrentSelection()[0][1]
		self.changed = True
		if returnValue is not None:
			idx = 0;
			if returnValue is "1":
				list = []
				self.XML_db.setSelection(name, "")
				for e in self.XML_db.getMenu():
					if e[1] == "1":
						list.append(QuickButtonListEntry('green',(_(e[0]),e[0], '1')))
						idx += 1
					else:
						list.append(QuickButtonListEntry('red',(_(e[0]),e[0], '')))

			else:
				list = []
				self.XML_db.setSelection(name, "1")
				for e in self.XML_db.getMenu():
					if e[1] == "1":
						list.append(QuickButtonListEntry('green',(_(e[0]),e[0], '1')))
						idx += 1
					else:
						list.append(QuickButtonListEntry('red',(_(e[0]),e[0], '')))

			self["list"].setList(list)

	def save(self):
		self.XML_db.saveMenu(self.path)
		self.changed = False
		self.cancel()

	def keyLeft(self):
		if len(self["list"].list) > 0:
			while 1:
				self["list"].instance.moveSelection(self["list"].instance.pageUp)
				if self["list"].l.getCurrentSelection()[0][1] != "--" or self["list"].l.getCurrentSelectionIndex() == 0:
					break

	def keyRight(self):
		if len(self["list"].list) > 0:
			while 1:
				self["list"].instance.moveSelection(self["list"].instance.pageDown)
				if self["list"].l.getCurrentSelection()[0][1] != "--" or self["list"].l.getCurrentSelectionIndex() == len(self["list"].list) - 1:
					break

	def up(self):
		if len(self["list"].list) > 0:
			while 1:
				self["list"].instance.moveSelection(self["list"].instance.moveUp)
				if self["list"].l.getCurrentSelection()[0][1] != "--" or self["list"].l.getCurrentSelectionIndex() == 0:
					break

	def down(self):
		if len(self["list"].list) > 0:
			while 1:
				self["list"].instance.moveSelection(self["list"].instance.moveDown)
				if self["list"].l.getCurrentSelection()[0][1] != "--" or self["list"].l.getCurrentSelectionIndex() == len(self["list"].list) - 1:
					break

	def getPluginsList(self):
		unic = []
		twins = [""]
		pluginlist = plugins.getPlugins([PluginDescriptor.WHERE_PLUGINMENU ,PluginDescriptor.WHERE_EXTENSIONSMENU, PluginDescriptor.WHERE_EVENTINFO])
		pluginlist.sort(key = lambda p: p.name)
		for plugin in pluginlist:
			if plugin.name in twins:
				pass 
			else:
				unic.append((_(plugin.name), plugin.name, "plugins", ""))
				twins.append(plugin.name)
		return unic

	def getFunctionList(self):
		unic = []
		mqbfunctionfile = functionfile
		self.mqbfunctions = xml.dom.minidom.parse(mqbfunctionfile)
		for mqbfunction in self.mqbfunctions.getElementsByTagName("mqbfunction"):
			functionname = str(mqbfunction.getElementsByTagName("name")[0].childNodes[0].data)
			unic.append((_(functionname),functionname, "functions" ""))
		return unic

	def add(self):
		self.changed = True
		self.session.openWithCallback(self.setNewEntryType,ChoiceBox,_("MQB Functions and Plugins") ,self.getNewEntryType())

	def setNewEntryType(self, selection):
		if selection:
			if selection[1] == "functions":
				self.addfunction()
			elif selection[1] == "plugins":
				self.addplugin()
			else:
				self.session.open(MessageBox,_("No valid selection"), type = MessageBox.TYPE_ERROR,timeout = 5)

	def getNewEntryType(self):
		entrytype = []
		entrytype.append((_("Add Functions to MQB Key"),"functions"))
		entrytype.append((_("Add Plugins to MQB Key"),"plugins"))
		return entrytype

	def addfunction(self):
		self.changed = True
		try:
			self.session.openWithCallback(self.QuickPluginSelected,ChoiceBox,_("Functions") ,self.getFunctionList())
		except Exception,e:
			self.session.open(MessageBox,_("No valid function file found"), type = MessageBox.TYPE_ERROR,timeout = 5)

	def addplugin(self):
		self.changed = True
		self.session.openWithCallback(self.QuickPluginSelected,ChoiceBox,_("Plugins") ,self.getPluginsList())

	def QuickPluginSelected(self, choice):
		if choice:
			for entry in self["list"].list:
				if entry[0][0] == choice[0]:
					self.session.open(MessageBox,_("Entry %s already exists.") % (entry[0][0]),type = MessageBox.TYPE_ERROR,timeout = 5)
					return
			if choice[2] == "plugins":
				self.XML_db.addPluginEntry(choice[1])
			elif choice[2] == "functions":
				self.XML_db.addFunctionEntry(choice[1])
			else:
				return
			list = []
			for newEntry in self.XML_db.getMenu():
				if newEntry[1] == "1":
					list.append(QuickButtonListEntry('green',(_(newEntry[0]), _(newEntry[0]), '1')))
				else:
					list.append(QuickButtonListEntry('red',(_(newEntry[0]), _(newEntry[0]), '')))
					
			self["list"].setList(list)
			if len(self["list"].list) > 0:
				while 1:
					self["list"].instance.moveSelection(self["list"].instance.moveDown)
					if self["list"].l.getCurrentSelection()[0][1] != '--' or self["list"].l.getCurrentSelectionIndex() == len(self["list"].list) - 1:
						break

	def delete(self):
		self.changed = True
		name = self["list"].l.getCurrentSelection()[0][1]
		if name and name <> "--":
			self.XML_db.rmEntry(name)

			list = []
			for e in self.XML_db.getMenu():
				if e[1] == "1":
					list.append(QuickButtonListEntry('green',(_(e[0]),e[0], '1')))
				else:
					list.append(QuickButtonListEntry('red',(_(e[0]),e[0], '')))

			lastValue="--"
			tmplist = []
			for i in list:
				if i[0][1] == "--" and lastValue == "--":
					lastValue = ""
				else:
					tmplist.append(i)
					lastValue = i[0][1]
			list = tmplist
			self["list"].setList(list)

	def cancel(self):
		if self.changed is True:
			self.session.openWithCallback(self.callForSaveValue,MessageBox,_("Save Settings"), MessageBox.TYPE_YESNO)
		else:
			self.close(None)

	def callForSaveValue(self, result):
		if result is True:
			self.save()
			self.close(None)
		else:
			self.close(None)

class MultiQuickButtonChannelConfiguration(Screen, ConfigListScreen):
	skin = """
		<screen position="center,center" size="550,300" title="MultiQuickButton Channel Selection" >
		<widget name="config" position="0,0" size="550,260" scrollbarMode="showOnDemand" />
		<widget name="buttonred" position="10,260" size="100,40" backgroundColor="red" valign="center" halign="center" zPosition="2" foregroundColor="white" font="Regular;18"/>
		<widget name="buttongreen" position="120,260" size="100,40" backgroundColor="green" valign="center" halign="center" zPosition="2" foregroundColor="white" font="Regular;18"/>
		</screen>"""

	def __init__(self, session, args = 0):
		self.session = session
		Screen.__init__(self, session)

		self.createConfigList()
		self.onShown.append(self.setWindowTitle)
		ConfigListScreen.__init__(self, self.list, session = self.session, on_change = self.changedEntry)

		self["buttonred"] = Label(_("Cancel"))
		self["buttongreen"] = Label(_("OK"))
		self["setupActions"] = ActionMap(["SetupActions", "ColorActions"],
			{
				"green": self.save,
				"red": self.cancel,
				"save": self.save,
				"cancel": self.cancel,
				"ok": self.save,
			}, -2)

	def createConfigList(self):
		self.list = []
		self.list.append(getConfigListEntry((_("Channel") + (" 1")), config.plugins.QuickButton.channel1))
		self.list.append(getConfigListEntry((_("Channel") + (" 2")), config.plugins.QuickButton.channel2))
		self.list.append(getConfigListEntry((_("Channel") + (" 3")), config.plugins.QuickButton.channel3))
		self.list.append(getConfigListEntry((_("Channel") + (" 4")), config.plugins.QuickButton.channel4))
		self.list.append(getConfigListEntry((_("Channel") + (" 5")), config.plugins.QuickButton.channel5))

	def changedEntry(self):
		self.createConfigList()
		self["config"].setList(self.list)

	def setWindowTitle(self):
		self.setTitle(_("Channel Selection"))

	def save(self):
		for x in self["config"].list:
			x[1].save()
		self.changedEntry()
		self.close(True,self.session)

	def cancel(self):
		if self["config"].isChanged():
			self.session.openWithCallback(self.cancelConfirm, MessageBox, _("Quite without saving changes ?"), MessageBox.TYPE_YESNO, default = False)
		else:
			for x in self["config"].list:
				x[1].cancel()
			self.close(False,self.session)

	def cancelConfirm(self, result):
		if result is None or result is False:
			pass
		else:
			for x in self["config"].list:
				x[1].cancel()
			self.close(False,self.session)

class MultiQuickButtonMacro(Screen):
	skin = """
		<screen position="center,center" size="640,400" title="MultiQuickButton macro configuration" >
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MultiQuickButton/pic/button_red.png" zPosition="2" position="10,350" size="25,25" alphatest="on" />
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MultiQuickButton/pic/button_green.png" zPosition="2" position="160,350" size="25,25" alphatest="on" />
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MultiQuickButton/pic/button_yellow.png" zPosition="2" position="330,350" size="25,25" alphatest="on" />
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MultiQuickButton/pic/button_blue.png" zPosition="2" position="490,350" size="25,25" alphatest="on" />
		<widget name="buttonred" backgroundColor="#1f771f" position="35,343" zPosition="2" size="250,40" font="Regular;20" halign="left" valign="center" transparent="1" />
		<widget name="buttongreen" backgroundColor="#1f771f" position="185,343" zPosition="2" size="250,40" font="Regular;20" halign="left" valign="center" transparent="1" />
		<widget name="buttonyellow" backgroundColor="#1f771f" position="355,343" zPosition="2"  size="150,40" font="Regular;20" halign="left" valign="center" transparent="1" />
		<widget name="buttonblue" backgroundColor="#1f771f" position="515,343" zPosition="2"  size="150,40" font="Regular;20" halign="left" valign="center" transparent="1" />
		<widget source="menu" render="Listbox" position="10,50" size="500,285" scrollbarMode="showOnDemand" >
			<convert type="TemplatedMultiContent" transparent="0">
				{"template": [
						MultiContentEntryText(pos = (52, 2), size = (500, 20), font=0, flags = RT_HALIGN_LEFT|RT_VALIGN_CENTER, text = 0),
					],
				"fonts": [gFont("Regular", 22)],
				"itemHeight": 26
				}
			</convert>
		</widget>
		</screen>"""

	def __init__(self, session, args = 0):
		self.session = session
		Screen.__init__(self, session)

		self.title=_("MultiQuickButton macro configuration")
		try:
			self["title"]=StaticText(self.title)
		except:
			print 'self["title"] was not found in skin'

		self.list = []
		self["menu"] = List(self.list)

		self["buttonred"] = Label(_("Exit"))
		self["buttongreen"] = Label(_("OK"))
		self["buttonyellow"] = Label()
		self["buttonblue"] = Label()
		self["setupActions"] = ActionMap(["SetupActions", "ColorActions"],
			{
				"green": self.save,
				"red": self.cancel,
				"blue": self.addButton,
				"yellow": self.removeButton,
				"save": self.save,
				"cancel": self.cancel,
				"ok": self.keyOk,
			}, -2)
		self.selectmacro = True
		self.configmacro = False
		self.addkey = False
		
		self.buttondic = {
					"011" : "0",
					"002" : "1",
					"003" : "2",
					"004" : "3",
					"005" : "4",
					"006" : "5",
					"007" : "6",
					"008" : "7",
					"009" : "8",
					"010" : "9",
					"116" : _("Power"),
					"139" : _("Menu"),
					"402" : _("Channel +"),
					"403" : _("Channel -"),
					"358" : _("Info"),
					"352" : _("OK"),
					"105" : _("Cross Left"),
					"106" : _("Cross Right"),
					"103" : _("Cross Up"),
					"108" : _("Cross Down"),
					"174" : _("EXIT"),
					"398" : _("red"),
					"401" : _("blue"),
					"399" : _("green"),
					"400" : _("yellow"),
					"207" : _("Play"),
					"119" : _("Pause"),
					"128" : _("Stop"),
					"167" : _("Record"),
					"208" : _("FastForward >>"),
					"168" : _("Rewind <<"),
					"107" : _("END"),
					"102" : _("HOME"),
					"392" : _("Audio"),
					"370" : _("Subtitle"),
					"168" : _("Rewind <<"),
					"388" : _("TEXT"),
					"377" : _("TV"),
					"385" : _("RADIO"),
					"393" : _("PVR"),
					"138" : _("HELP"),
					"115" : _("Volume +"),
					"114" : _("Volume -"),
					"113" : _("Mute"),
					"407" : _("Forward >"),
					"412" : _("Backward <")
				}

		self.onLayoutFinish.append(self.createMenu)

	def createMenu(self):
		self.textstring = _("Configure macro")
		self.list = []
		self.list.append((self.textstring + " I", "macroI"))
		self.list.append((self.textstring + " II", "macroII"))
		self.list.append((self.textstring + " III", "macroIII"))
		self.list.append((self.textstring + " IV", "macroIV"))
		self.list.append((self.textstring + " V", "macroV"))
		self["menu"].setList(self.list)

	def keyOk(self):
		cur = self["menu"].getCurrent()
		if cur:
			self["buttonred"].setText(_("Cancel"))
			self["buttongreen"].setText(_("Save"))
			self["buttonyellow"].setText(_("Delete"))
			self["buttonblue"].setText(_("Add"))
			if self.configmacro == False and self.selectmacro == True:
				self.selectmacro = False
				self.configmacro = True
				if cur[1] == "macroI":
					keys = config.plugins.QuickButton.macroI.value
				elif cur[1] == "macroII":
					keys = config.plugins.QuickButton.macroII.value
				elif cur[1] == "macroIII":
					keys = config.plugins.QuickButton.macroIII.value
				elif cur[1] == "macroIV":
					keys = config.plugins.QuickButton.macroIV.value
				elif cur[1] == "macroV":
					keys = config.plugins.QuickButton.macroV.value
				self.current_macro = cur[1]
				self.macrolist = []
				for key in keys.split(","):
					if key in self.buttondic:
						self.macrolist.append((_("Button : ") + _(self.buttondic[key]), key))
				self["menu"].setList(self.macrolist)
			elif self.configmacro == True and self.selectmacro == False and self.addkey == True:
				self.addkey = False
				self.macrolist.append(cur)
				self["menu"].setList(self.macrolist)

	def addButton(self):
		if self.configmacro == True and self.selectmacro == False:
			self["buttonred"].setText(_("Cancel"))
			self["buttongreen"].setText(_("Ok"))
			self["buttonyellow"].setText("")
			self["buttonblue"].setText("")
			self.addkey = True
			self.buttonlist =[]
			for key in sorted(self.buttondic.iterkeys()):
				self.buttonlist.append((_("Button : ") + self.buttondic[key], key))
			self["menu"].setList(self.buttonlist)

	def removeButton(self):
		if self.configmacro == True and self.selectmacro == False:
			cur = self["menu"].getCurrent()
			if cur:
				self.macrolist.remove(cur)
			self['menu'].updateList(self.macrolist)

	def save(self):
		if self.configmacro == True and self.selectmacro == False and self.addkey == False:
			self.selectmacro = True
			self.configmacro = False
			self.addkey = False
			self.new_config_value = ""
			for entry in self.macrolist:
				self.new_config_value = self.new_config_value + "," + entry[1]
			self.new_config_value = self.new_config_value.strip(",")
			if self.current_macro == "macroI":
				config.plugins.QuickButton.macroI.value = self.new_config_value
				config.plugins.QuickButton.macroI.save()
			elif self.current_macro == "macroII":
				config.plugins.QuickButton.macroII.value = self.new_config_value
				config.plugins.QuickButton.macroII.save()
			elif self.current_macro == "macroIII":
				config.plugins.QuickButton.macroIII.value = self.new_config_value
				config.plugins.QuickButton.macroIII.save()
			elif self.current_macro == "macroIV":
				config.plugins.QuickButton.macroIV.value = self.new_config_value
				config.plugins.QuickButton.macroIV.save()
			elif self.current_macro == "macroV":
				config.plugins.QuickButton.macroV.value = self.new_config_value
				config.plugins.QuickButton.macroV.save()
			self["buttonred"].setText(_("Exit"))
			self["buttongreen"].setText(_("Ok"))
			self["buttonyellow"].setText("")
			self["buttonblue"].setText("")
			self["menu"].setList(self.list)
		elif self.selectmacro == True:
			self.keyOk()
		else:
			self.close(True,self.session)

	def cancel(self):
		if self.selectmacro == True:
			self.close(False,self.session)
		elif self.configmacro == True and self.selectmacro == False and self.addkey == False:
			self.selectmacro = True
			self.configmacro = False
			self["buttonred"].setText(_("Exit"))
			self["buttongreen"].setText(_("Ok"))
			self["buttonyellow"].setText("")
			self["buttonblue"].setText("")
			self["menu"].setList(self.list)
		elif self.configmacro == True and self.selectmacro == False and self.addkey == True:
			self.addkey = False
			self["buttonred"].setText(_("Cancel"))
			self["buttongreen"].setText(_("Save"))
			self["buttonyellow"].setText(_("Delete"))
			self["buttonblue"].setText(_("Add"))
			self["menu"].setList(self.macrolist)
