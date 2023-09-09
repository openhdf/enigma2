from __future__ import absolute_import

from xml.etree.cElementTree import parse
from six import ensure_str
from boxbranding import getMachineBrand, getMachineName
from Components.ActionMap import NumberActionMap
from Components.config import config, configfile
from Components.Console import Console
from Components.PluginComponent import plugins
from Components.Sources.List import List
from Components.Sources.StaticText import StaticText
from Components.SystemInfo import SystemInfo
from Screens.ParentalControlSetup import ProtectedScreen
from Screens.MessageBox import MessageBox
from Screens.Standby import TryQuitMainloop
from Screens.Screen import Screen
from Screens.Setup import Setup, getSetupTitle, getSetupTitleLevel
from Tools.BoundFunction import boundFunction
from Tools.Directories import SCOPE_SKIN, resolveFilename
from enigma import eTimer
import subprocess

mainmenu = _("Main menu")

# read the menu
file = open(resolveFilename(SCOPE_SKIN, 'menu.xml'), 'r')
mdom = parse(file)
file.close()


class MenuUpdater:
	def __init__(self):
		self.updatedMenuItems = {}

	def addMenuItem(self, id, pos, text, module, screen, weight):
		if not self.updatedMenuAvailable(id):
			self.updatedMenuItems[id] = []
		self.updatedMenuItems[id].append([text, pos, module, screen, weight])

	def delMenuItem(self, id, pos, text, module, screen, weight):
		self.updatedMenuItems[id].remove([text, pos, module, screen, weight])

	def updatedMenuAvailable(self, id):
		return id in self.updatedMenuItems

	def getUpdatedMenu(self, id):
		return self.updatedMenuItems[id]


menuupdater = MenuUpdater()


class MenuSummary(Screen):
	pass


class Menu(Screen, ProtectedScreen):
	ALLOW_SUSPEND = True

	def okbuttonClick(self):
		# print "okbuttonClick"
		selection = self["menu"].getCurrent()
		if selection is not None:
			selection[1]()

	def execText(self, text):
		exec(text)

	def runScreen(self, arg):
		# arg[0] is the module (as string)
		# arg[1] is Screen inside this module
		#	plus possible arguments, as
		#	string (as we want to reference
		#	stuff which is just imported)
		if arg[0] != "":
			exec("from %s import %s" % (arg[0], arg[1].split(",")[0]))
			self.openDialog(*eval(arg[1]))

	def nothing(self): #dummy
		pass

	def gotoStandby(self, *res):
		from Screens.Standby import Standby2
		self.session.open(Standby2)
		self.close(True)

	def openDialog(self, *dialog):				# in every layer needed
		self.session.openWithCallback(self.menuClosed, *dialog)

	def openSetup(self, dialog):
		if dialog == "channelselection":
			self.oldHdfPiconValue = config.usage.hdfpicon.value
			self.oldYtdlpValue = config.usage.ytdlp.value
			self.oldServiceAppValue = config.usage.serviceapp.value
			self.oldStreamlinkSrvValue = config.usage.streamlinkserver.value
			self.session.openWithCallback(self.pluginCheck, Setup, dialog)
		else:
			self.session.openWithCallback(self.menuClosed, Setup, dialog)

	def pluginCheck(self, args=None):
		configfile.save()
		self.message = None
		self.installFailed = False
		self.errorText = ""
		self.errorTimer = eTimer()
		self.errorTimer.callback.append(self.showErrorMessage)
		self.restartTimer = eTimer()
		self.restartTimer.callback.append(self.showRestartMessage)
		self.opkgString = ""

		# check hdfpicon
		if self.oldHdfPiconValue != config.usage.hdfpicon.value:
			if config.usage.hdfpicon.value:
				self.opkgString += "/usr/bin/opkg install --force-overwrite enigma2-plugin-picons-default-hdf && "
			else:
				self.opkgString += "/usr/bin/opkg remove --force-depends enigma2-plugin-picons-default-hdf && "

		# check ytdlp
		if self.oldYtdlpValue != config.usage.ytdlp.value:
			if config.usage.ytdlp.value:
				self.opkgString += "/usr/bin/opkg install --force-overwrite python3-youtube-dl && "
				self.opkgString += "/usr/bin/opkg install --force-overwrite python3-yt-dlp && "
				self.opkgString += "/usr/bin/opkg install --force-overwrite enigma2-plugin-extensions-streamlinkwrapper && "
				self.opkgString += "/usr/bin/opkg install --force-overwrite enigma2-plugin-extensions-ytdlpwrapper && "
				self.opkgString += "/usr/bin/opkg install --force-overwrite enigma2-plugin-extensions-ytdlwrapper && "
			else:
				self.opkgString += "/usr/bin/opkg remove --force-depends enigma2-plugin-extensions-streamlinkwrapper && "
				self.opkgString += "/usr/bin/opkg remove --force-depends enigma2-plugin-extensions-ytdlpwrapper && "
				self.opkgString += "/usr/bin/opkg remove --force-depends enigma2-plugin-extensions-ytdlwrapper && "

		# check serviceapp
		if self.oldServiceAppValue != config.usage.serviceapp.value:
			if config.usage.serviceapp.value:
				self.opkgString += "/usr/bin/opkg remove --force-depends enigma2-plugin-systemplugins-servicehisilicon && "
				self.opkgString += "/usr/bin/opkg install --force-overwrite enigma2-plugin-systemplugins-serviceapp && "
			else:
				self.opkgString += "/usr/bin/opkg remove --force-depends enigma2-plugin-systemplugins-serviceapp && "
				self.opkgString += "/usr/bin/opkg install --force-overwrite enigma2-plugin-systemplugins-servicehisilicon && "

		# check streamlinkserver
		if self.oldStreamlinkSrvValue != config.usage.streamlinkserver.value:
			if config.usage.streamlinkserver.value:
				self.opkgString += "/usr/bin/opkg install --force-overwrite enigma2-plugin-extensions-streamlinkserver && "
				try:
					cmdstring = subprocess.Popen("chmod 755 /usr/sbin/streamlinksrv && /etc/rc3.d/S50streamlinksrv start", shell=True)
					cmdstring.wait()
				except:
					pass
			else:
				try:
					cmdstring = subprocess.Popen("/etc/rc3.d/S50streamlinksrv stop && chmod 644 /usr/sbin/streamlinksrv", shell=True)
					cmdstring.wait()
				except:
					pass

		self.opkgString = self.opkgString.rsplit(" && ", 1)[0]

		if (self.oldHdfPiconValue != config.usage.hdfpicon.value) or (self.oldYtdlpValue != config.usage.ytdlp.value) or (self.oldServiceAppValue != config.usage.serviceapp.value) or (self.oldStreamlinkSrvValue != config.usage.streamlinkserver.value):
			self.message = self.session.open(MessageBox, _("please wait..."), MessageBox.TYPE_INFO, enable_input=False)
			self.message.setTitle(_("Installing plugins from feed ..."))
			PingConsole = Console()
			PingConsole.ePopen("/bin/ping -c 1 hdfreaks.cc", self.checkPing)

	def checkPing(self, ping, retval, extra_args=None):
		ping = ensure_str(ping)
		if "bad address" in ping:
			self.resetValues()
			self.errorText = _("Your %s %s is not connected to the internet, please check your network settings and try again.") % (getMachineBrand(), getMachineName())
			self.errorTimer.start(5, True)
		else:
			UpdateConsole = Console()
			UpdateConsole.ePopen("/usr/bin/opkg update", self.checkServer)

	def checkServer(self, result, retval, extra_args=None):
		result = ensure_str(result)
		if ("wget returned 1" or "wget returned 255" or "404 Not Found") in result:
			self.resetValues()
			self.errorText = _("Sorry feeds are down for maintenance, please try again later.")
			self.errorTimer.start(5, True)
		else:
			opkg = subprocess.Popen(self.opkgString, shell=True)
			opkg.wait()
			if self.message:
				self.message.close()
			if (self.oldHdfPiconValue != config.usage.hdfpicon.value) or (self.oldYtdlpValue != config.usage.ytdlp.value) or (self.oldServiceAppValue != config.usage.serviceapp.value) or (self.oldStreamlinkSrvValue != config.usage.streamlinkserver.value) and not self.installFailed:
				self.restartTimer.start(5, True)

	def showErrorMessage(self):
		self.session.open(MessageBox, self.errorText, MessageBox.TYPE_INFO, timeout=10)

	def showRestartMessage(self):
		self.session.openWithCallback(self.restartImage, MessageBox, _("Your %s %s needs a restart to apply the changes.\nRestart your box now?") % (getMachineBrand(), getMachineName()), MessageBox.TYPE_YESNO, timeout=20)

	def restartImage(self, answer):
		if answer is True:
			self.session.open(TryQuitMainloop, 2)
		else:
			self.close()

	def resetValues(self):
		if self.message:
			self.message.close()
		self.installFailed = True
		if self.oldHdfPiconValue != config.usage.hdfpicon.value:
			config.usage.hdfpicon.value = self.oldHdfPiconValue
			config.usage.hdfpicon.save()
		if self.oldYtdlpValue != config.usage.ytdlp.value:
			config.usage.ytdlp.value = self.oldYtdlpValue
			config.usage.ytdlp.save()
		if self.oldServiceAppValue != config.usage.serviceapp.value:
			config.usage.serviceapp.value = self.oldServiceAppValue
			config.usage.serviceapp.save()
		if self.oldStreamlinkSrvValue != config.usage.streamlinkserver.value:
			config.usage.streamlinkserver.value = self.oldStreamlinkSrvValue
			config.usage.streamlinkserver.save()
			if self.oldStreamlinkSrvValue:
				try:
					cmdstring = subprocess.Popen("chmod 755 /usr/sbin/streamlinksrv && /etc/rc3.d/S50streamlinksrv start", shell=True)
					cmdstring.wait()
				except:
					pass
			else:
				try:
					cmdstring = subprocess.Popen("/etc/rc3.d/S50streamlinksrv stop && chmod 644 /usr/sbin/streamlinksrv", shell=True)
					cmdstring.wait()
				except:
					pass

		configfile.save()

	def addMenu(self, destList, node):
		requires = node.get("requires")
		if requires:
			if requires[0] == '!':
				if SystemInfo.get(requires[1:], False):
					return
			elif not SystemInfo.get(requires, False):
				return
		MenuTitle = _(ensure_str(node.get("text", "??")))
		entryID = node.get("entryID", "undefined")
		weight = node.get("weight", 50)
		x = node.get("flushConfigOnClose")
		if x:
			a = boundFunction(self.session.openWithCallback, self.menuClosedWithConfigFlush, Menu, node)
		else:
			a = boundFunction(self.session.openWithCallback, self.menuClosed, Menu, node)
		#TODO add check if !empty(node.childNodes)
		destList.append((MenuTitle, a, entryID, weight))

	def menuClosedWithConfigFlush(self, *res):
		configfile.save()
		self.menuClosed(*res)

	def menuClosed(self, *res):
		if res and res[0]:
			self.close(True)

	def addItem(self, destList, node):
		requires = node.get("requires")
		if requires:
			if requires[0] == '!':
				if SystemInfo.get(requires[1:], False):
					return
			elif not SystemInfo.get(requires, False):
				return
		configCondition = node.get("configcondition")
		if configCondition and not eval(configCondition + ".value"):
			return
		item_text = ensure_str(node.get("text", ""))
		entryID = node.get("entryID", "undefined")
		weight = node.get("weight", 50)
		for x in node:
			if x.tag == 'screen':
				module = x.get("module")
				screen = x.get("screen")

				if screen is None:
					screen = module

				# print module, screen
				if module:
					module = "Screens." + module
				else:
					module = ""

				# check for arguments. they will be appended to the
				# openDialog call
				args = x.text or ""
				screen += ", " + args

				destList.append((_(item_text or "??"), boundFunction(self.runScreen, (module, screen)), entryID, weight))
				return
			elif x.tag == 'plugin':
				extensions = x.get("extensions")
				system = x.get("system")
				screen = x.get("screen")

				if extensions:
					module = extensions
				elif system:
					module = system

				if screen is None:
					screen = module

				if extensions:
					module = "Plugins.Extensions." + extensions + '.plugin'
				elif system:
					module = "Plugins.SystemPlugins." + system + '.plugin'
				else:
					module = ""

				# check for arguments. they will be appended to the
				# openDialog call
				args = x.text or ""
				screen += ", " + args

				destList.append((_(item_text or "??"), boundFunction(self.runScreen, (module, screen)), entryID, weight))
				return
			elif x.tag == 'code':
				destList.append((_(item_text or "??"), boundFunction(self.execText, x.text), entryID, weight))
				return
			elif x.tag == 'setup':
				id = x.get("id")
				if item_text == "":
					if getSetupTitleLevel(id) > config.usage.setup_level.index:
						return
					item_text = _(getSetupTitle(id))
				else:
					item_text = _(item_text)
				destList.append((item_text, boundFunction(self.openSetup, id), entryID, weight))
				return
		destList.append((item_text, self.nothing, entryID, weight))

	def __init__(self, session, parent):
		Screen.__init__(self, session)
		list = []

		menuID = None
		for x in parent:						#walk through the actual nodelist
			if not x.tag:
				continue
			if x.tag == 'item':
				item_level = int(x.get("level", 0))
				if item_level <= config.usage.setup_level.index:
					self.addItem(list, x)
					count += 1
			elif x.tag == 'menu':
				item_level = int(x.get("level", 0))
				if item_level <= config.usage.setup_level.index:
					self.addMenu(list, x)
					count += 1
			elif x.tag == "id":
				menuID = x.get("val")
				count = 0

			if menuID is not None:
				# menuupdater?
				if menuupdater.updatedMenuAvailable(menuID):
					for x in menuupdater.getUpdatedMenu(menuID):
						if x[1] == count:
							list.append((x[0], boundFunction(self.runScreen, (x[2], x[3] + ", ")), x[4]))
							count += 1

		self.menuID = menuID
		if config.ParentalControl.configured.value:
			ProtectedScreen.__init__(self)

		if menuID is not None:
			# plugins
			for l in plugins.getPluginsForMenu(menuID):
				# check if a plugin overrides an existing menu
				plugin_menuid = l[2]
				for x in list:
					if x[2] == plugin_menuid:
						list.remove(x)
						break
				if len(l) > 4 and l[4]:
					list.append((l[0], boundFunction(l[1], self.session, self.close), l[2], l[3] or 50))
				else:
					list.append((l[0], boundFunction(l[1], self.session), l[2], l[3] or 50))

		# for the skin: first try a menu_<menuID>, then Menu
		self.skinName = []
		if menuID is not None:
			self.skinName.append("menu_" + menuID)
		self.skinName.append("Menu")
		self.menuID = menuID
		ProtectedScreen.__init__(self)

		# Sort by Weight
		if config.usage.sort_menus.value:
			list.sort()
		else:
			list.sort(key=lambda x: int(x[3]))

		self["menu"] = List(list)

		self["actions"] = NumberActionMap(["OkCancelActions", "MenuActions", "NumberActions"],
			{
				"ok": self.okbuttonClick,
				"cancel": self.closeNonRecursive,
				"menu": self.closeRecursive,
				"1": self.keyNumberGlobal,
				"2": self.keyNumberGlobal,
				"3": self.keyNumberGlobal,
				"4": self.keyNumberGlobal,
				"5": self.keyNumberGlobal,
				"6": self.keyNumberGlobal,
				"7": self.keyNumberGlobal,
				"8": self.keyNumberGlobal,
				"9": self.keyNumberGlobal
			})

		a = ensure_str(parent.get("title", "")) or None
		a = a and _(a)
		if a is None:
			a = _(ensure_str(parent.get("text", "")))
		self["title"] = StaticText(a)
		Screen.setTitle(self, a)
		self.menu_title = a

	def isProtected(self):
		if config.ParentalControl.setuppinactive.value:
			if config.ParentalControl.config_sections.main_menu.value and self.menuID == "mainmenu":
				return True
			elif config.ParentalControl.config_sections.configuration.value and self.menuID == "setup":
				return True
			elif config.ParentalControl.config_sections.timer_menu.value and self.menuID == "timermenu":
				return True
			elif config.ParentalControl.config_sections.standby_menu.value and self.menuID == "shutdown":
				return True

	def keyNumberGlobal(self, number):
		# print "menu keyNumber:", number
		# Calculate index
		number -= 1

		if len(self["menu"].list) > number:
			self["menu"].setIndex(number)
			self.okbuttonClick()

	def closeNonRecursive(self):
		self.close(False)

	def closeRecursive(self):
		self.close(True)

	def createSummary(self):
		return MenuSummary

	def isProtected(self):
		if config.ParentalControl.setuppinactive.value:
			if config.ParentalControl.config_sections.main_menu.value:
				return self.menuID == "mainmenu"
			elif config.ParentalControl.config_sections.configuration.value and self.menuID == "setup":
				return True
			elif config.ParentalControl.config_sections.timer_menu.value and self.menuID == "timermenu":
				return True
			elif config.ParentalControl.config_sections.standby_menu.value and self.menuID == "shutdown":
				return True


class MainMenu(Menu):
	#add file load functions for the xml-file

	def __init__(self, *x):
		self.skinName = "Menu"
		Menu.__init__(self, *x)
