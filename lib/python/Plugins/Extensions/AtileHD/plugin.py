# -*- coding: utf-8 -*-

#This plugin is free software, you are allowed to
#modify it (if you keep the license),
#but you are not allowed to distribute/publish
#it without source code (this version and your modifications).
#This means you also have to distribute
#source code of your modifications.

from __future__ import print_function
from __future__ import absolute_import
from enigma import eTimer
from Components.ActionMap import ActionMap
from Components.config import config, getConfigListEntry, ConfigSubsection, ConfigSelection, ConfigYesNo, NoSave, ConfigNothing, ConfigNumber
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.MenuList import MenuList
from Components.Pixmap import Pixmap
from Components.Sources.List import List
from Components.Sources.StaticText import StaticText
from Plugins.Plugin import PluginDescriptor
from Screens.SkinSelector import SkinSelector
from Screens.InputBox import InputBox
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.Standby import TryQuitMainloop
from Tools.Directories import *
from Tools.LoadPixmap import LoadPixmap
from Tools.WeatherID import get_woeid_from_yahoo
from Tools import Notifications
from os import listdir, remove, rename, system, path, symlink, chdir, makedirs, mkdir
import shutil

cur_skin = config.skin.primary_skin.value.replace('/skin.xml', '')

# Atile
config.plugins.AtileHD = ConfigSubsection()
config.plugins.AtileHD.refreshInterval = ConfigNumber(default=10)
config.plugins.AtileHD.woeid = ConfigNumber(default=638242)
config.plugins.AtileHD.tempUnit = ConfigSelection(default="Celsius", choices=[
				("Celsius", _("Celsius")),
				("Fahrenheit", _("Fahrenheit"))
				])

def Plugins(**kwargs):
	return [PluginDescriptor(name=_("%s Setup") % cur_skin, description=_("Personalize your Skin"), where=PluginDescriptor.WHERE_MENU, icon="plugin.png", fnc=menu)]

def menu(menuid, **kwargs):
	if menuid == "gui_menu" and not config.skin.primary_skin.value == "XionHDF/skin.MySkin.xml" and not config.skin.primary_skin.value == "XionHDF/skin.xml" and not config.skin.primary_skin.value =="SevenHD/skin.xml" and not config.skin.primary_skin.value == "KravenVB/skin.xml":
		return [(_("Setup - %s") % cur_skin, main, "atilehd_setup", None)]
	else:
		pass
	return []

def main(session, **kwargs):
	print("[%s]: Config ..." % cur_skin)
	session.open(AtileHD_Config)

def isInteger(s):
	try:
		int(s)
		return True
	except ValueError:
		return False

class WeatherLocationChoiceList(Screen):
	skin = """
		<screen name="WeatherLocationChoiceList" position="center,center" size="1280,720" title="Location list" >
			<widget source="Title" render="Label" position="70,47" size="950,43" font="Regular;35" transparent="1" />
			<widget name="choicelist" position="70,115" size="700,480" scrollbarMode="showOnDemand" scrollbarWidth="6" transparent="1" />
			<eLabel position=" 55,675" size="290, 5" zPosition="-10" backgroundColor="red" />
			<eLabel position="350,675" size="290, 5" zPosition="-10" backgroundColor="green" />
			<eLabel position="645,675" size="290, 5" zPosition="-10" backgroundColor="yellow" />
			<eLabel position="940,675" size="290, 5" zPosition="-10" backgroundColor="blue" />
			<widget name="key_red" position="70,635" size="260,25" zPosition="1" font="Regular;20" halign="left" foregroundColor="foreground" transparent="1" />
			<widget name="key_green" position="365,635" size="260,25" zPosition="1" font="Regular;20" halign="left" foregroundColor="foreground" transparent="1" />
		</screen>
		"""

	def __init__(self, session, location_list):
		self.session = session
		self.location_list = location_list
		list = []
		Screen.__init__(self, session)
		self.title = _("Location list")
		self["choicelist"] = MenuList(list)
		self["key_red"] = Label(_("Cancel"))
		self["key_green"] = Label(_("OK"))
		self["myActionMap"] = ActionMap(["SetupActions", "ColorActions"],
		{
			"ok": self.keyOk,
			"green": self.keyOk,
			"cancel": self.keyCancel,
			"red": self.keyCancel,
		}, -1)
		self.createChoiceList()

	def createChoiceList(self):
		list = []
		print(self.location_list)
		for x in self.location_list:
			list.append((str(x[1]), str(x[0])))
		self["choicelist"].l.setList(list)

	def keyOk(self):
		returnValue = self["choicelist"].l.getCurrentSelection()[1]
		if returnValue is not None:
			self.close(returnValue)
		else:
			self.keyCancel()

	def keyCancel(self):
		self.close(None)


class AtileHD_Config(Screen, ConfigListScreen):

	skin = """
		<screen name="AtileHD_Config" position="center,center" size="1280,720" title="AtileHD Setup" >
			<widget source="Title" render="Label" position="70,47" size="950,43" font="Regular;35" transparent="1" />
			<widget name="config" position="70,115" size="700,480" scrollbarMode="showOnDemand" scrollbarWidth="6" transparent="1" />
			<widget name="Picture" position="808,342" size="400,225" alphatest="on" />
			<eLabel position=" 55,675" size="290, 5" zPosition="-10" backgroundColor="red" />
			<eLabel position="350,675" size="290, 5" zPosition="-10" backgroundColor="green" />
			<eLabel position="645,675" size="290, 5" zPosition="-10" backgroundColor="yellow" />
			<eLabel position="940,675" size="290, 5" zPosition="-10" backgroundColor="blue" />
			<widget name="key_red" position="70,635" size="260,25" zPosition="1" font="Regular;20" halign="left" foregroundColor="foreground" transparent="1" />
			<widget name="key_green" position="365,635" size="260,25" zPosition="1" font="Regular;20" halign="left" foregroundColor="foreground" transparent="1" />
			<widget name="key_yellow" position="660,635" size="260,25" zPosition="1" font="Regular;20" halign="left" foregroundColor="foreground" transparent="1" />
			<widget name="key_blue" position="955,635" size="260,25" zPosition="0" font="Regular;20" halign="left" foregroundColor="foreground" transparent="1" />
		</screen>
	"""

	def __init__(self, session, args=0):
		self.session = session
		self.skin_lines = []
		self.changed_screens = False
		Screen.__init__(self, session)

		self.start_skin = config.skin.primary_skin.value

		if self.start_skin != "skin.xml":
			self.getInitConfig()

		self.list = []
		ConfigListScreen.__init__(self, self.list, session=self.session, on_change=self.changedEntry)

		self["key_red"] = Label(_("Cancel"))
		self["key_green"] = Label(_("OK"))
		self["key_yellow"] = Label()
		self["key_blue"] = Label(_("About"))
		self["setupActions"] = ActionMap(["SetupActions", "ColorActions"],
			{
				"green": self.keyGreen,
				"red": self.cancel,
				"yellow": self.keyYellow,
				"blue": self.about,
				"cancel": self.cancel,
				"ok": self.keyOk,
				"menu": self.setWeather,
			}, -2)

		self["Picture"] = Pixmap()

		if not self.selectionChanged in self["config"].onSelectionChanged:
			self["config"].onSelectionChanged.append(self.selectionChanged)

		if self.start_skin == "skin.xml":
			self.onLayoutFinish.append(self.openSkinSelectorDelayed)
		else:
			self.createConfigList()

	def setWeather(self):
		try:
			from Plugins.Extensions.WeatherPlugin.setup import MSNWeatherPluginEntriesListConfigScreen
			self.session.open(MSNWeatherPluginEntriesListConfigScreen)
		except:
			self.session.open(MessageBox, _("'weatherplugin' is not installed!"), MessageBox.TYPE_INFO)

	def getInitConfig(self):
		global cur_skin
		self.is_atile = False
		if cur_skin == 'AtileHD':
			self.is_atile = True
		self.title = _("%s - Setup") % cur_skin
		self.skin_base_dir = "/usr/share/enigma2/%s/" % cur_skin
		if self.is_atile:
			self.default_font_file = "font_atile_Roboto.xml"
			self.default_color_file = "colors_atile_Grey_transparent.xml"
		else:
			self.default_sb_file = "sb_Original.xml"
			self.default_color_file = "colors_Original.xml"

		self.default_frame_file = "frame_Original.xml"
		self.default_center_file = "center_Original.xml"
		self.default_lines_file = "lines_Original.xml"
		self.default_sbar_file = "sbar_Original.xml"
		self.default_infobar_file = "infobar_Original.xml"
		self.default_wget_file = "wget_Original.xml"
		self.default_sib_file = "sib_Original.xml"
		self.default_ch_se_file = "ch_se_Original.xml"
		self.default_ev_file = "ev_Original.xml"
		self.default_emcsel_file = "emcsel_Original.xml"
		self.default_movsel_file = "movsel_Original.xml"
		self.default_volume_file = "volume_Original.xml"

		self.color_file = "skin_user_colors.xml"
		self.sb_file = "skin_user_sb.xml"
		self.frame_file = "skin_user_frame.xml"
		self.center_file = "skin_user_center.xml"
		self.lines_file = "skin_user_lines.xml"
		self.sbar_file = "skin_user_sbar.xml"
		self.infobar_file = "skin_user_infobar.xml"
		self.wget_file = "skin_user_wget.xml"
		self.sib_file = "skin_user_sib.xml"
		self.ch_se_file = "skin_user_ch_se.xml"
		self.ev_file = "skin_user_ev.xml"
		self.emcsel_file = "skin_user_emcsel.xml"
		self.movsel_file = "skin_user_movsel.xml"
		self.volume_file = "skin_user_volume.xml"

		# color
		current, choices = self.getSettings(self.default_color_file, self.color_file)
		self.myAtileHD_color = NoSave(ConfigSelection(default=current, choices=choices))
		# sb
		current, choices = self.getSettings(self.default_sb_file, self.sb_file)
		self.myAtileHD_sb = NoSave(ConfigSelection(default=current, choices=choices))
		# frame
		current, choices = self.getSettings(self.default_frame_file, self.frame_file)
		self.myAtileHD_frame = NoSave(ConfigSelection(default=current, choices=choices))
		# center
		current, choices = self.getSettings(self.default_center_file, self.center_file)
		self.myAtileHD_center = NoSave(ConfigSelection(default=current, choices=choices))
	    # lines
		current, choices = self.getSettings(self.default_lines_file, self.lines_file)
		self.myAtileHD_lines = NoSave(ConfigSelection(default=current, choices=choices))
		# sbar
		current, choices = self.getSettings(self.default_sbar_file, self.sbar_file)
		self.myAtileHD_sbar = NoSave(ConfigSelection(default=current, choices=choices))
		# infobar
		current, choices = self.getSettings(self.default_infobar_file, self.infobar_file)
		self.myAtileHD_infobar = NoSave(ConfigSelection(default=current, choices=choices))
		# wget
		current, choices = self.getSettings(self.default_wget_file, self.wget_file)
		self.myAtileHD_wget = NoSave(ConfigSelection(default=current, choices=choices))
		# sib
		current, choices = self.getSettings(self.default_sib_file, self.sib_file)
		self.myAtileHD_sib = NoSave(ConfigSelection(default=current, choices=choices))
		# ch_se
		current, choices = self.getSettings(self.default_ch_se_file, self.ch_se_file)
		self.myAtileHD_ch_se = NoSave(ConfigSelection(default=current, choices=choices))
		# ev
		current, choices = self.getSettings(self.default_ev_file, self.ev_file)
		self.myAtileHD_ev = NoSave(ConfigSelection(default=current, choices=choices))
		# emcsel
		current, choices = self.getSettings(self.default_emcsel_file, self.emcsel_file)
		self.myAtileHD_emcsel = NoSave(ConfigSelection(default=current, choices=choices))
		# movsel
		current, choices = self.getSettings(self.default_movsel_file, self.movsel_file)
		self.myAtileHD_movsel = NoSave(ConfigSelection(default=current, choices=choices))
		# volume
		current, choices = self.getSettings(self.default_volume_file, self.volume_file)
		self.myAtileHD_volume = NoSave(ConfigSelection(default=current, choices=choices))
		# myatile
		myatile_active = self.getmyAtileState()
		self.myAtileHD_active = NoSave(ConfigYesNo(default=myatile_active))
		self.myAtileHD_fake_entry = NoSave(ConfigNothing())

	def getSettings(self, default_file, user_file):
		# default setting
		default = ("default", _("Default"))

		# search typ
		styp = default_file.replace('_Original.xml', '')
		if self.is_atile:
			search_str = '%s_atile_' %styp
		else:
			search_str = '%s_' %styp

		# possible setting
		choices = []
		files = listdir(self.skin_base_dir)
		if path.exists(self.skin_base_dir + 'allScreens/%s/' %styp):
			files += listdir(self.skin_base_dir + 'allScreens/%s/' %styp)
		for f in sorted(files, key=str.lower):
			if f.endswith('.xml') and f.startswith(search_str):
				friendly_name = f.replace(search_str, "").replace(".xml", "").replace("_", " ")
				if path.exists(self.skin_base_dir + 'allScreens/%s/%s' %(styp, f)):
					choices.append((self.skin_base_dir + 'allScreens/%s/%s' %(styp, f), friendly_name))
				else:
					choices.append((self.skin_base_dir + f, friendly_name))
		choices.append(default)

		# current setting
		myfile = self.skin_base_dir + user_file
		current = ''
		if not path.exists(myfile):
			if path.exists(self.skin_base_dir + default_file):
				if path.islink(myfile):
					remove(myfile)
				chdir(self.skin_base_dir)
				symlink(default_file, user_file)
			elif path.exists(self.skin_base_dir + 'allScreens/%s/%s' %(styp, default_file)):
				if path.islink(myfile):
					remove(myfile)
				chdir(self.skin_base_dir)
				symlink(self.skin_base_dir + 'allScreens/%s/%s' %(styp, default_file), user_file)
			else:
				current = None
		if current is None:
			current = default
		else:
			filename = path.realpath(myfile)
			friendly_name = path.basename(filename).replace(search_str, "").replace(".xml", "").replace("_", " ")
			current = (filename, friendly_name)

		return current[0], choices

	def createConfigList(self):
		self.set_color = getConfigListEntry(_("Style:"), self.myAtileHD_color)
		self.set_sb = getConfigListEntry(_("ColorSelectedBackground:"), self.myAtileHD_sb)
		self.set_frame = getConfigListEntry(_("Frame:"), self.myAtileHD_frame)
		self.set_center = getConfigListEntry(_("Center:"), self.myAtileHD_center)
		self.set_lines = getConfigListEntry(_("Lines:"), self.myAtileHD_lines)
		self.set_sbar = getConfigListEntry(_("Scrollbar:"), self.myAtileHD_sbar)
		self.set_infobar = getConfigListEntry(_("Infobar:"), self.myAtileHD_infobar)
		self.set_wget = getConfigListEntry(_("Clock_Widget:"), self.myAtileHD_wget)
		self.set_sib = getConfigListEntry(_("Secondinfobar:"), self.myAtileHD_sib)
		self.set_ch_se = getConfigListEntry(_("Channelselection:"), self.myAtileHD_ch_se)
		self.set_ev = getConfigListEntry(_("Eventview:"), self.myAtileHD_ev)
		self.set_emcsel = getConfigListEntry(_("EMC_Selection:"), self.myAtileHD_emcsel)
		self.set_movsel = getConfigListEntry(_("Movie_Selection:"), self.myAtileHD_movsel)
		self.set_volume = getConfigListEntry(_("Volume:"), self.myAtileHD_volume)
		self.set_myatile = getConfigListEntry(_("Enable %s pro:") % cur_skin, self.myAtileHD_active)
		self.set_new_skin = getConfigListEntry(_("Change skin"), ConfigNothing())
		self.find_woeid = getConfigListEntry(_("Search weather location ID"), ConfigNothing())
		self.list = []
		self.list.append(self.set_myatile)
		if len(self.myAtileHD_color.choices)>1:
			self.list.append(self.set_color)
		if len(self.myAtileHD_sb.choices)>1:
			self.list.append(self.set_sb)
		if len(self.myAtileHD_frame.choices)>1:
			self.list.append(self.set_frame)
		if len(self.myAtileHD_center.choices)>1:
			self.list.append(self.set_center)
		if len(self.myAtileHD_lines.choices)>1:
			self.list.append(self.set_lines)
		if len(self.myAtileHD_sbar.choices)>1:
			self.list.append(self.set_sbar)
		if len(self.myAtileHD_infobar.choices)>1:
			self.list.append(self.set_infobar)
		if len(self.myAtileHD_wget.choices)>1:
			self.list.append(self.set_wget)
		if len(self.myAtileHD_sib.choices)>1:
			self.list.append(self.set_sib)
		if len(self.myAtileHD_ch_se.choices)>1:
			self.list.append(self.set_ch_se)
		if len(self.myAtileHD_ev.choices)>1:
			self.list.append(self.set_ev)
		if len(self.myAtileHD_emcsel.choices)>1:
			self.list.append(self.set_emcsel)
		if len(self.myAtileHD_movsel.choices)>1:
			self.list.append(self.set_movsel)
		if len(self.myAtileHD_volume.choices)>1:
			self.list.append(self.set_volume)
		self.list.append(self.set_new_skin)
		#if not config.skin.primary_skin.value == "iFlatFHD/skin.xml":
		#	self.list.append(getConfigListEntry(_("---Weather---"), self.myAtileHD_fake_entry))
		#	self.list.append(getConfigListEntry(_("Refresh interval in minutes:"), config.plugins.AtileHD.refreshInterval))
		#	self.list.append(getConfigListEntry(_("Temperature unit:"), config.plugins.AtileHD.tempUnit))
		#	self.list.append(self.find_woeid)
		#	self.list.append(getConfigListEntry(_("Location # (http://weather.yahoo.com/):"), config.plugins.AtileHD.woeid))
		self["config"].list = self.list
		self["config"].l.setList(self.list)
		if self.myAtileHD_active.value:
			self["key_yellow"].setText("%s pro" % cur_skin)
		else:
			self["key_yellow"].setText("")

	def changedEntry(self):
		if self["config"].getCurrent() == self.set_color:
			self.setPicture(self.myAtileHD_color.value)
		elif self["config"].getCurrent() == self.set_sb:
			self.setPicture(self.myAtileHD_sb.value)
		elif self["config"].getCurrent() == self.set_frame:
			self.setPicture(self.myAtileHD_frame.value)
		elif self["config"].getCurrent() == self.set_center:
			self.setPicture(self.myAtileHD_center.value)
		elif self["config"].getCurrent() == self.set_lines:
			self.setPicture(self.myAtileHD_lines.value)
		elif self["config"].getCurrent() == self.set_sbar:
			self.setPicture(self.myAtileHD_sbar.value)
		elif self["config"].getCurrent() == self.set_infobar:
			self.setPicture(self.myAtileHD_infobar.value)
		elif self["config"].getCurrent() == self.set_wget:
			self.setPicture(self.myAtileHD_wget.value)
		elif self["config"].getCurrent() == self.set_sib:
			self.setPicture(self.myAtileHD_sib.value)
		elif self["config"].getCurrent() == self.set_ch_se:
			self.setPicture(self.myAtileHD_ch_se.value)
		elif self["config"].getCurrent() == self.set_ev:
			self.setPicture(self.myAtileHD_ev.value)
		elif self["config"].getCurrent() == self.set_emcsel:
			self.setPicture(self.myAtileHD_emcsel.value)
		elif self["config"].getCurrent() == self.set_movsel:
			self.setPicture(self.myAtileHD_movsel.value)
		elif self["config"].getCurrent() == self.set_volume:
			self.setPicture(self.myAtileHD_volume.value)
		elif self["config"].getCurrent() == self.set_myatile:
			if self.myAtileHD_active.value:
				self["key_yellow"].setText("%s pro" % cur_skin)
			else:
				self["key_yellow"].setText("")

	def selectionChanged(self):
		if self["config"].getCurrent() == self.set_color:
			self.setPicture(self.myAtileHD_color.value)
		elif self["config"].getCurrent() == self.set_sb:
			self.setPicture(self.myAtileHD_sb.value)
		elif self["config"].getCurrent() == self.set_frame:
			self.setPicture(self.myAtileHD_frame.value)
		elif self["config"].getCurrent() == self.set_center:
			self.setPicture(self.myAtileHD_center.value)
		elif self["config"].getCurrent() == self.set_lines:
			self.setPicture(self.myAtileHD_lines.value)
		elif self["config"].getCurrent() == self.set_sbar:
			self.setPicture(self.myAtileHD_sbar.value)
		elif self["config"].getCurrent() == self.set_infobar:
			self.setPicture(self.myAtileHD_infobar.value)
		elif self["config"].getCurrent() == self.set_wget:
			self.setPicture(self.myAtileHD_wget.value)
		elif self["config"].getCurrent() == self.set_sib:
			self.setPicture(self.myAtileHD_sib.value)
		elif self["config"].getCurrent() == self.set_ch_se:
			self.setPicture(self.myAtileHD_ch_se.value)
		elif self["config"].getCurrent() == self.set_ev:
			self.setPicture(self.myAtileHD_ev.value)
		elif self["config"].getCurrent() == self.set_emcsel:
			self.setPicture(self.myAtileHD_emcsel.value)
		elif self["config"].getCurrent() == self.set_movsel:
			self.setPicture(self.myAtileHD_movsel.value)
		elif self["config"].getCurrent() == self.set_volume:
			self.setPicture(self.myAtileHD_volume.value)
		else:
			self["Picture"].hide()

	def cancel(self):
		if self["config"].isChanged():
			self.session.openWithCallback(self.cancelConfirm, MessageBox, _("Really close without saving settings?"), MessageBox.TYPE_YESNO, default=False)
		else:
			for x in self["config"].list:
				x[1].cancel()
			if self.changed_screens:
				self.restartGUI()
			else:
				self.close()

	def cancelConfirm(self, result):
		if result is None or result is False:
			print("[%s]: Cancel confirmed." % cur_skin)
		else:
			print("[%s]: Cancel confirmed. Config changes will be lost." % cur_skin)
			for x in self["config"].list:
				x[1].cancel()
			self.close()

	def getmyAtileState(self):
		chdir(self.skin_base_dir)
		if path.exists("mySkin"):
			return True
		else:
			return False

	def setPicture(self, f):
		pic = f.split('/')[-1].replace(".xml", ".png")
		preview = self.skin_base_dir + "preview/preview_" + pic
		if path.exists(preview):
			self["Picture"].instance.setPixmapFromFile(preview)
			self["Picture"].show()
		else:
			self["Picture"].hide()

	def keyYellow(self):
		if self.myAtileHD_active.value:
			self.session.openWithCallback(self.AtileHDScreenCB, AtileHDScreens)
		else:
			self["config"].setCurrentIndex(0)

	def keyOk(self):
		sel =  self["config"].getCurrent()
		if sel is not None and sel == self.set_new_skin:
			self.openSkinSelector()
		elif sel is not None and sel == self.find_woeid:
			self.session.openWithCallback(self.search_weather_id_callback, InputBox, title=_("Please enter search string for your location"), text="")
		else:
			self.keyGreen()

	def openSkinSelector(self):
		self.session.openWithCallback(self.skinChanged, SkinSelector)

	def openSkinSelectorDelayed(self):
		self.delaytimer = eTimer()
		self.delaytimer.callback.append(self.openSkinSelector)
		self.delaytimer.start(200, True)

	def search_weather_id_callback(self, res):
		if res:
			id_dic = get_woeid_from_yahoo(res)
			if 'error' in id_dic:
				error_txt = id_dic['error']
				self.session.open(MessageBox, _("Sorry, there was a problem:") + "\n%s" % error_txt, MessageBox.TYPE_ERROR)
			elif 'count' in id_dic:
				result_no = int(id_dic['count'])
				location_list = []
				for i in list(range(0, result_no)):
					location_list.append(id_dic[i])
				self.session.openWithCallback(self.select_weather_id_callback, WeatherLocationChoiceList, location_list)

	def select_weather_id_callback(self, res):
		if res and isInteger(res):
			print(res)
			config.plugins.AtileHD.woeid.value = int(res)

	def skinChanged(self, ret=None):
		global cur_skin
		cur_skin = config.skin.primary_skin.value.replace('/skin.xml', '')
		if cur_skin == "skin.xml":
			self.restartGUI()
		else:
			self.getInitConfig()
			self.createConfigList()

	def keyGreen(self):
		if self["config"].isChanged():
			for x in self["config"].list:
				x[1].save()
			chdir(self.skin_base_dir)

			# color
			self.makeSettings(self.myAtileHD_color, self.color_file)
			# sb
			self.makeSettings(self.myAtileHD_sb, self.sb_file)
			# frame
			self.makeSettings(self.myAtileHD_frame, self.frame_file)
			# center
			self.makeSettings(self.myAtileHD_center, self.center_file)
			# lines
			self.makeSettings(self.myAtileHD_lines, self.lines_file)
			# sbar
			self.makeSettings(self.myAtileHD_sbar, self.sbar_file)
			# infobar
			self.makeSettings(self.myAtileHD_infobar, self.infobar_file)
			# wget
			self.makeSettings(self.myAtileHD_wget, self.wget_file)
			# sib
			self.makeSettings(self.myAtileHD_sib, self.sib_file)
			# ch_se
			self.makeSettings(self.myAtileHD_ch_se, self.ch_se_file)
			# ev
			self.makeSettings(self.myAtileHD_ev, self.ev_file)
			# emcsel
			self.makeSettings(self.myAtileHD_emcsel, self.emcsel_file)
			# movsel
			self.makeSettings(self.myAtileHD_movsel, self.movsel_file)
			# volume
			self.makeSettings(self.myAtileHD_volume, self.volume_file)

			if not path.exists("mySkin_off"):
				mkdir("mySkin_off")
				print("makedir mySkin_off")
			if self.myAtileHD_active.value:
				if not path.exists("mySkin") and path.exists("mySkin_off"):
						symlink("mySkin_off", "mySkin")
			else:
				if path.exists("mySkin"):
					if path.exists("mySkin_off"):
						if path.islink("mySkin"):
							remove("mySkin")
						else:
							shutil.rmtree("mySkin")
					else:
						rename("mySkin", "mySkin_off")
			self.restartGUI()
		elif  config.skin.primary_skin.value != self.start_skin:
			self.restartGUI()
		else:
			if self.changed_screens:
				self.restartGUI()
			else:
				self.close()

	def makeSettings(self, config_entry, user_file):
		if path.exists(user_file) or path.islink(user_file):
			remove(user_file)
		if config_entry.value != 'default':
			symlink(config_entry.value, user_file)

	def AtileHDScreenCB(self):
		self.changed_screens = True
		self["config"].setCurrentIndex(0)

	def restartGUI(self):
		restartbox = self.session.openWithCallback(self.restartGUIcb, MessageBox, _("Restart necessary, restart GUI now?"), MessageBox.TYPE_YESNO)
		restartbox.setTitle(_("Message"))

	def about(self):
		self.session.open(AtileHD_About)

	def restartGUIcb(self, answer):
		if answer is True:
			self.session.open(TryQuitMainloop, 3)
		else:
			self.close()

class AtileHD_About(Screen):

	def __init__(self, session, args=0):
		self.session = session
		Screen.__init__(self, session)
		self["setupActions"] = ActionMap(["SetupActions", "ColorActions"],
			{
				"cancel": self.cancel,
				"ok": self.keyOk,
			}, -2)

	def keyOk(self):
		self.close()

	def cancel(self):
		self.close()

class AtileHDScreens(Screen):

	skin = """
		<screen name="AtileHDScreens" position="center,center" size="1280,720" title="AtileHD Setup">
			<widget source="Title" render="Label" position="70,47" size="950,43" font="Regular;35" transparent="1" />
			<widget source="menu" render="Listbox" position="70,115" size="700,480" scrollbarMode="showOnDemand" scrollbarWidth="6" scrollbarSliderBorderWidth="1" enableWrapAround="1" transparent="1">
				<convert type="TemplatedMultiContent">
					{"template":
						[
							MultiContentEntryPixmapAlphaTest(pos = (2, 2), size = (25, 24), png = 2),
							MultiContentEntryText(pos = (35, 4), size = (500, 24), font=0, flags = RT_HALIGN_LEFT|RT_VALIGN_CENTER, text = 1),
						],
						"fonts": [gFont("Regular", 22),gFont("Regular", 16)],
						"itemHeight": 30
					}
				</convert>
			</widget>
			<widget name="Picture" position="808,342" size="400,225" alphatest="on" />
			<eLabel position=" 55,675" size="290, 5" zPosition="-10" backgroundColor="red" />
			<eLabel position="350,675" size="290, 5" zPosition="-10" backgroundColor="green" />
			<widget source="key_red" render="Label" position="70,635" size="260,25" zPosition="1" font="Regular;20" halign="left" transparent="1" />
			<widget source="key_green" render="Label" position="365,635" size="260,25" zPosition="1" font="Regular;20" halign="left" transparent="1" />
		</screen>
	"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self.session = session

		global cur_skin
		self.is_atile = False
		if cur_skin == 'AtileHD':
			self.is_atile = True

		self.title = _("%s additional screens") % cur_skin
		try:
			self["title"]=StaticText(self.title)
		except:
			print('self["title"] was not found in skin')

		self["key_red"] = StaticText(_("Exit"))
		self["key_green"] = StaticText(_("on"))

		self["Picture"] = Pixmap()

		menu_list = []
		self["menu"] = List(menu_list)

		self["shortcuts"] = ActionMap(["SetupActions", "ColorActions", "DirectionActions"],
		{
			"ok": self.runMenuEntry,
			"cancel": self.keyCancel,
			"red": self.keyCancel,
			"green": self.runMenuEntry,
		}, -2)

		self.skin_base_dir = "/usr/share/enigma2/%s/" % cur_skin
		self.screen_dir = "allScreens"
		self.skinparts_dir = "skinparts"
		self.file_dir = "mySkin_off"
		my_path = resolveFilename(SCOPE_SKIN, "%s/icons/lock_on.png" % cur_skin)
		if not path.exists(my_path):
			my_path = resolveFilename(SCOPE_SKIN, "skin_default/icons/lock_on.png")
		self.enabled_pic = LoadPixmap(cached=True, path=my_path)
		my_path = resolveFilename(SCOPE_SKIN, "%s/icons/lock_off.png" % cur_skin)
		if not path.exists(my_path):
			my_path = resolveFilename(SCOPE_SKIN, "skin_default/icons/lock_off.png")
		self.disabled_pic = LoadPixmap(cached=True, path=my_path)

		if not self.selectionChanged in self["menu"].onSelectionChanged:
			self["menu"].onSelectionChanged.append(self.selectionChanged)

		self.onLayoutFinish.append(self.createMenuList)

	def selectionChanged(self):
		sel = self["menu"].getCurrent()
		if sel is not None:
			self.setPicture(sel[0])
			if sel[2] == self.enabled_pic:
				self["key_green"].setText(_("off"))
			elif sel[2] == self.disabled_pic:
				self["key_green"].setText(_("on"))

	def createMenuList(self):
		chdir(self.skin_base_dir)
		f_list = []
		dir_path = self.skin_base_dir + self.screen_dir
		if not path.exists(dir_path):
			makedirs(dir_path)
		dir_skinparts_path = self.skin_base_dir + self.skinparts_dir
		if not path.exists(dir_skinparts_path):
			makedirs(dir_skinparts_path)
		file_dir_path = self.skin_base_dir + self.file_dir
		if not path.exists(file_dir_path):
			makedirs(file_dir_path)
		dir_global_skinparts = resolveFilename(SCOPE_SKIN, "skinparts")
		if path.exists(dir_global_skinparts):
			for pack in listdir(dir_global_skinparts):
				if path.isdir(dir_global_skinparts + "/" + pack):
					for f in listdir(dir_global_skinparts + "/" + pack):
						if path.exists(dir_global_skinparts + "/" + pack + "/" + f + "/" + f + "_Atile.xml"):
							if not path.exists(dir_path + "/skin_" + f + ".xml"):
								symlink(dir_global_skinparts + "/" + pack + "/" + f + "/" + f + "_Atile.xml", dir_path + "/skin_" + f + ".xml")
							if not path.exists(dir_skinparts_path + "/" + f):
								symlink(dir_global_skinparts + "/" + pack + "/" + f, dir_skinparts_path + "/" + f)
		list_dir = sorted(listdir(dir_path), key=str.lower)
		for f in list_dir:
			if f.endswith('.xml') and f.startswith('skin_'):
				if (not path.islink(dir_path + "/" + f)) or os.path.exists(os.readlink(dir_path + "/" + f)):
					friendly_name = f.replace("skin_", "")
					friendly_name = friendly_name.replace(".xml", "")
					friendly_name = friendly_name.replace("_", " ")
					linked_file = file_dir_path + "/" + f
					if path.exists(linked_file):
						if path.islink(linked_file):
							pic = self.enabled_pic
						else:
							remove(linked_file)
							symlink(dir_path + "/" + f, file_dir_path + "/" + f)
							pic = self.enabled_pic
					else:
						pic = self.disabled_pic
					f_list.append((f, friendly_name, pic))
				else:
					if path.islink(dir_path + "/" + f):
						remove(dir_path + "/" + f)
		menu_list = []
		for entry in f_list:
			menu_list.append((entry[0], entry[1], entry[2]))
		self["menu"].updateList(menu_list)
		self.selectionChanged()

	def setPicture(self, f):
		pic = f.replace(".xml", ".png")
		preview = self.skin_base_dir + "preview/preview_" + pic
		if path.exists(preview):
			self["Picture"].instance.setPixmapFromFile(preview)
			self["Picture"].show()
		else:
			self["Picture"].hide()

	def keyCancel(self):
		self.close()

	def runMenuEntry(self):
		sel = self["menu"].getCurrent()
		if sel is not None:
			if sel[2] == self.enabled_pic:
				remove(self.skin_base_dir + self.file_dir + "/" + sel[0])
			elif sel[2] == self.disabled_pic:
				symlink(self.skin_base_dir + self.screen_dir + "/" + sel[0], self.skin_base_dir + self.file_dir + "/" + sel[0])
			self.createMenuList()
