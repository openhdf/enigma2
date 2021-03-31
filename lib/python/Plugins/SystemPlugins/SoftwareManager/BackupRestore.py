from __future__ import print_function
from __future__ import absolute_import
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.Console import Console
from Components.ActionMap import ActionMap, NumberActionMap
from Tools.LoadPixmap import LoadPixmap
from Components.Label import Label
from Components.Sources.StaticText import StaticText
from Components.MenuList import MenuList
from Components.Sources.List import List
from Components.Button import Button
from Components.config import ConfigLocations, ConfigSubsection, ConfigText, configfile
from Components.config import config
from Components.ConfigList import ConfigListScreen
from Components.FileList import MultiFileSelectList
from Components.Network import iNetwork
from enigma import eConsoleAppContainer, eEPGCache, eEnv
from Tools.Directories import *
from os import listdir, makedirs, path, popen, remove, rename, stat
from datetime import date
from boxbranding import getBoxType, getMachineBrand, getMachineName, getImageDistro
from . import ShellCompatibleFunctions
import six

boxtype = getBoxType()
distro = getImageDistro()

def eEnv_resolve_multi(path):
	resolve = eEnv.resolve(path)
	return resolve.split()

config.plugins.configurationbackup = ConfigSubsection()
if boxtype in ('maram9', 'classm', 'axodin', 'axodinc', 'starsatlx', 'genius', 'evo', 'galaxym6') and not path.exists("/media/hdd/backup_%s" %boxtype):
	config.plugins.configurationbackup.backuplocation = ConfigText(default = '/media/backup/', visible_width = 50, fixed_size = False)
else:
	config.plugins.configurationbackup.backuplocation = ConfigText(default = '/media/hdd/', visible_width = 50, fixed_size = False)
config.plugins.configurationbackup.backupdirs = ConfigLocations(default=[eEnv.resolve('${sysconfdir}/enigma2/'), '/etc/CCcam.cfg', '/etc/CCcam.prio', '/usr/keys/', '/usr/scripts/', '/etc/tuxbox/config/', '/var/tuxbox/config/', '/etc/model',
																			'/etc/auto.network', '/etc/default/dropbear', '/home/root/', '/etc/samba/', '/etc/fstab', '/etc/inadyn.conf', '/etc/ConfFS/', '/etc/enigma2/ci_auth_slot_0.bin', '/etc/enigma2/ci_auth_slot_1.bin',
																			'/etc/network/interfaces', '/etc/wpa_supplicant.conf', '/etc/default_gw', '/etc/wpa_supplicant.ath0.conf', '/etc/dropbear/', '/etc/volume.xml', '/etc/cron/crontabs/root', '/etc/vtuner.conf',
																			'/etc/wpa_supplicant.wlan0.conf', '/etc/wpa_supplicant.wlan1.conf', '/etc/resolv.conf', '/etc/hostname', '/usr/share/enigma2/XionHDF/skin.xml', '/etc/xmltvimport', '/etc/ava_volume.cfg', '/etc/ava_setup.cfg',
																			'/etc/openvpn/', '/etc/ipsec.conf', '/etc/ipsec.secrets', '/etc/ipsec.user', '/etc/strongswan.conf', '/usr/lib/enigma2/python/Plugins/Extensions/VMC/DB/', '/usr/lib/enigma2/python/Plugins/Extensions/VMC/youtv.pwd', '/usr/bin/enigma2_pre_start.sh',
																			'/usr/lib/enigma2/python/Plugins/Extensions/VMC/vod.config', '/usr/lib/enigma2/python/Plugins/Extensions/MP3Browser/db', '/usr/lib/enigma2/python/Plugins/Extensions/MovieBrowser/db', '/usr/lib/enigma2/python/Plugins/Extensions/TVSpielfilm/db',
																			eEnv.resolve("${datadir}/enigma2/keymap.usr"), eEnv.resolve("${datadir}/enigma2/keymap.ntr"), eEnv.resolve("${datadir}/enigma2/keymap_usermod.xml")]\
																			+eEnv_resolve_multi('/usr/bin/*cam*')\
																			+eEnv_resolve_multi('/usr/bin/gbox')\
																			+eEnv_resolve_multi('/etc/*.emu')\
																			+eEnv_resolve_multi('/etc/init.d/softcam*')\
																			+eEnv_resolve_multi('/etc/init.d/cardserver*'))

def getBackupPath():
	backuppath = config.plugins.configurationbackup.backuplocation.value
	if backuppath.endswith('/'):
		return backuppath + 'backup_' + distro + '_'+ boxtype
	else:
		return backuppath + '/backup_' + distro + '_'+ boxtype

def getOldBackupPath():
	backuppath = config.plugins.configurationbackup.backuplocation.value
	if backuppath.endswith('/'):
		return backuppath + 'backup_' + boxtype
	else:
		return backuppath + '/backup_' + boxtype

def getBackupFilename():
	return "enigma2settingsbackup.tar.gz"

def SettingsEntry(name, checked):
	if checked:
		picture = LoadPixmap(cached = True, path = resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/icons/lock_on.png"));
	else:
		picture = LoadPixmap(cached = True, path = resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/icons/lock_off.png"));

	return (name, picture, checked)

class BackupScreen(Screen, ConfigListScreen):
	skin = """
		<screen position="135,144" size="350,310" title="Backup is running" >
		<widget name="config" position="10,10" size="330,250" transparent="1" scrollbarMode="showOnDemand" />
		</screen>"""

	def __init__(self, session, runBackup = False):
		Screen.__init__(self, session)
		self.session = session
		self.runBackup = runBackup
		self["actions"] = ActionMap(["WizardActions", "DirectionActions"],
		{
			"ok": self.close,
			"back": self.close,
			"cancel": self.close,
		}, -1)
		self.finished_cb = None
		self.backuppath = getBackupPath()
		self.backupfile = getBackupFilename()
		self.fullbackupfilename = self.backuppath + "/" + self.backupfile
		self.list = []
		ConfigListScreen.__init__(self, self.list)
		self.onLayoutFinish.append(self.layoutFinished)
		if self.runBackup:
			self.onShown.append(self.doBackup)

	def layoutFinished(self):
		self.setWindowTitle()

	def setWindowTitle(self):
		self.setTitle(_("Backup is running..."))

	def doBackup(self):
		configfile.save()
		if config.plugins.softwaremanager.epgcache.value:
			eEPGCache.getInstance().save()
		try:
			if path.exists(self.backuppath) == False:
				makedirs(self.backuppath)
			self.backupdirs = ' '.join( config.plugins.configurationbackup.backupdirs.value )
			if not "/tmp/installed-list.txt" in self.backupdirs:
				self.backupdirs = self.backupdirs + " /tmp/installed-list.txt"
			if not "/tmp/changed-configfiles.txt" in self.backupdirs:
				self.backupdirs = self.backupdirs + " /tmp/changed-configfiles.txt"

			cmd1 = "opkg list-installed | egrep -v '^ ' | awk '{print $1 }' | egrep 'enigma2-plugin-|task-base|packagegroup-base|^ca-certificates$|minilocale|^davfs2$|^joe$|^mc$|^mergerfs$|^nano$|^openvpn|^easy-rsa$|^simple-rsa$|^perl|^rclone$|^streamproxy$|^wget$' > /tmp/installed-list.txt"
			cmd2 = "opkg list-changed-conffiles > /tmp/changed-configfiles.txt"
			cmd3 = "echo -n Backup is running ...please wait"
			cmd4 = "tar -czf " + self.fullbackupfilename + " " + self.backupdirs + " 2>/tmp/settingsbackup.log"
			cmd5 = "echo ... done"
			cmd6 = "echo"
			cmd7 = "echo Now press OK to exit"
			cmd8 = "echo"
			cmd4 = cmd4 + " --exclude home/root/.cache"
			cmd = [cmd1, cmd2, cmd3, cmd4, cmd5, cmd6, cmd7, cmd8]
			if path.exists(self.fullbackupfilename):
				dt = str(date.fromtimestamp(stat(self.fullbackupfilename).st_ctime))
				self.newfilename = self.backuppath + "/" + dt + '-' + self.backupfile
				if path.exists(self.newfilename):
					remove(self.newfilename)
				rename(self.fullbackupfilename, self.newfilename)
			if self.finished_cb:
				self.session.openWithCallback(self.finished_cb, Console, title = _("Backup is running..."), cmdlist = cmd, finishedCallback = self.backupFinishedCB, closeOnSuccess = True)
			else:
				self.session.open(Console, title = _("Backup is running..."), cmdlist = cmd, finishedCallback = self.backupFinishedCB, closeOnSuccess = True)
		except OSError:
			if self.finished_cb:
				self.session.openWithCallback(self.finished_cb, MessageBox, _("Sorry, your backup destination is not writeable.\nPlease select a different one."), MessageBox.TYPE_INFO, timeout = 10 )
			else:
				self.session.openWithCallback(self.backupErrorCB, MessageBox, _("Sorry, your backup destination is not writeable.\nPlease select a different one."), MessageBox.TYPE_INFO, timeout = 10 )

	def backupFinishedCB(self,retval = None):
		self.close(True)

	def backupErrorCB(self,retval = None):
		self.close(False)

	def runAsync(self, finished_cb):
		self.finished_cb = finished_cb
		self.doBackup()


class BackupSelection(Screen):
	skin = """
		<screen name="BackupSelection" position="center,center" size="560,400" title="Select files/folders to backup">
			<ePixmap pixmap="buttons/red.png" position="0,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="buttons/green.png" position="140,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="buttons/yellow.png" position="280,0" size="140,40" alphatest="on" />
			<widget source="key_red" render="Label" position="0,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
			<widget source="key_green" render="Label" position="140,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
			<widget source="key_yellow" render="Label" position="280,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" transparent="1" />
			<widget name="checkList" position="5,50" size="550,250" transparent="1" scrollbarMode="showOnDemand" />
		</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self["key_red"] = StaticText(_("Cancel"))
		self["key_green"] = StaticText(_("Save"))
		self["key_yellow"] = StaticText()
		self["summary_description"] = StaticText("")

		self.selectedFiles = config.plugins.configurationbackup.backupdirs.value
		defaultDir = '/'
		inhibitDirs = ["/bin", "/boot", "/dev", "/autofs", "/lib", "/proc", "/sbin", "/sys", "/hdd", "/tmp", "/mnt", "/media"]
		self.filelist = MultiFileSelectList(self.selectedFiles, defaultDir, inhibitDirs = inhibitDirs )
		self["checkList"] = self.filelist

		self["actions"] = ActionMap(["DirectionActions", "OkCancelActions", "ShortcutActions"],
		{
			"cancel": self.exit,
			"red": self.exit,
			"yellow": self.changeSelectionState,
			"green": self.saveSelection,
			"ok": self.okClicked,
			"left": self.left,
			"right": self.right,
			"down": self.down,
			"up": self.up
		}, -1)
		if not self.selectionChanged in self["checkList"].onSelectionChanged:
			self["checkList"].onSelectionChanged.append(self.selectionChanged)
		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		idx = 0
		self["checkList"].moveToIndex(idx)
		self.setWindowTitle()
		self.selectionChanged()

	def setWindowTitle(self):
		self.setTitle(_("Select files/folders to backup"))

	def selectionChanged(self):
		current = self["checkList"].getCurrent()[0]
		self["summary_description"].text = current[3]
		if current[2] is True:
			self["key_yellow"].setText(_("Deselect"))
		else:
			self["key_yellow"].setText(_("Select"))

	def up(self):
		self["checkList"].up()

	def down(self):
		self["checkList"].down()

	def left(self):
		self["checkList"].pageUp()

	def right(self):
		self["checkList"].pageDown()

	def changeSelectionState(self):
		self["checkList"].changeSelectionState()
		self.selectedFiles = self["checkList"].getSelectedList()

	def saveSelection(self):
		self.selectedFiles = self["checkList"].getSelectedList()
		config.plugins.configurationbackup.backupdirs.setValue(self.selectedFiles)
		config.plugins.configurationbackup.backupdirs.save()
		config.plugins.configurationbackup.save()
		config.save()
		self.close(None)

	def exit(self):
		self.close(None)

	def okClicked(self):
		if self.filelist.canDescent():
			self.filelist.descent()


class RestoreMenu(Screen):
	skin = """
		<screen name="RestoreMenu" position="center,center" size="560,400" title="Restore backups" >
			<ePixmap pixmap="buttons/red.png" position="0,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="buttons/green.png" position="140,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="buttons/yellow.png" position="280,0" size="140,40" alphatest="on" />
			<widget source="key_red" render="Label" position="0,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
			<widget source="key_green" render="Label" position="140,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
			<widget source="key_yellow" render="Label" position="280,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" transparent="1" />
			<widget name="filelist" position="5,50" size="550,230" scrollbarMode="showOnDemand" />
		</screen>"""

	def __init__(self, session, plugin_path):
		Screen.__init__(self, session)
		self.skin_path = plugin_path

		self["key_red"] = StaticText(_("Cancel"))
		self["key_green"] = StaticText(_("Restore"))
		self["key_yellow"] = StaticText(_("Delete"))
		self["summary_description"] = StaticText("")

		self.sel = []
		self.val = []
		self.entry = False
		self.exe = False

		self.path = ""

		self["actions"] = NumberActionMap(["SetupActions"],
		{
			"ok": self.KeyOk,
			"cancel": self.keyCancel,
			"up": self.keyUp,
			"down": self.keyDown
		}, -1)

		self["shortcuts"] = ActionMap(["ShortcutActions"],
		{
			"red": self.keyCancel,
			"green": self.KeyOk,
			"yellow": self.deleteFile,
		})
		self.flist = []
		self["filelist"] = MenuList(self.flist)
		self.fill_list()
		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.setWindowTitle()
		self.checkSummary()

	def setWindowTitle(self):
		self.setTitle(_("Restore backups"))

	def fill_list(self):
		self.flist = []
		self.path = getBackupPath()
		if path.exists(self.path) == False:
			makedirs(self.path)
		for file in listdir(self.path):
			if file.endswith(".tar.gz"):
				self.flist.append(file)
				self.entry = True
		self.flist.sort(reverse=True)
		self["filelist"].l.setList(self.flist)

	def KeyOk(self):
		if (self.exe == False) and (self.entry == True):
			self.sel = self["filelist"].getCurrent()
			if self.sel:
				self.val = self.path + "/" + self.sel
				self.session.openWithCallback(self.startRestore, MessageBox, _("Are you sure you want to restore\nthe following backup:\n%s\nYour receiver will restart after the backup has been restored!") % self.sel)

	def keyCancel(self):
		self.close()

	def keyUp(self):
		self["filelist"].up()
		self.checkSummary()

	def keyDown(self):
		self["filelist"].down()
		self.checkSummary()

	def startRestore(self, ret = False):
		if ret == True:
			self.exe = True
			self.session.open(Console, title = _("Restoring..."), cmdlist = ["cd /etc/enigma2/ ; rm -R * ", "tar -xzvf " + self.path + "/" + self.sel + " -C /", "killall -9 enigma2", "/etc/init.d/autofs restart ; /etc/init.d/softcam restart"])

	def deleteFile(self):
		if (self.exe == False) and (self.entry == True):
			self.sel = self["filelist"].getCurrent()
			if self.sel:
				self.val = self.path + "/" + self.sel
				self.session.openWithCallback(self.startDelete, MessageBox, _("Are you sure you want to delete\nthe following backup:\n") + self.sel)

	def startDelete(self, ret = False):
		if ret == True:
			self.exe = True
			print("removing:", self.val)
			if path.exists(self.val) == True:
				remove(self.val)
			self.exe = False
			self.fill_list()

	def checkSummary(self):
		cur = self["filelist"].getCurrent()
		self["summary_description"].text = cur

class RestoreScreen(Screen, ConfigListScreen):
	skin = """
		<screen position="135,144" size="350,310" title="Restore is running..." >
		<widget name="config" position="10,10" size="330,250" transparent="1" scrollbarMode="showOnDemand" />
		</screen>"""

	def __init__(self, session, runRestore = False):
		Screen.__init__(self, session)
		self.session = session
		self.runRestore = runRestore
		self["actions"] = ActionMap(["WizardActions", "DirectionActions"],
		{
			"ok": self.close,
			"back": self.close,
			"cancel": self.close,
		}, -1)
		self.backuppath = getBackupPath()
#		if path.exists(self.backuppath) == False:
#			self.backuppath = getOldBackupPath()
		if not path.isdir(self.backuppath):
			self.backuppath = getOldBackupPath()
		self.backupfile = getBackupFilename()
		self.fullbackupfilename = self.backuppath + "/" + self.backupfile
		self.list = []
		ConfigListScreen.__init__(self, self.list)
		self.onLayoutFinish.append(self.layoutFinished)
		if self.runRestore:
			self.onShown.append(self.doRestore)

	def layoutFinished(self):
		self.setWindowTitle()

	def setWindowTitle(self):
		self.setTitle(_("Restoring..."))

	def doRestore(self):
		restorecmdlist = ["tar -xzvf " + self.fullbackupfilename + " --exclude=etc/passwd --exclude=etc/shadow --exclude=etc/group -C /", "chown -R root:root /home/root /etc/auto.network /etc/default/dropbear /etc/dropbear ; chmod 600 /etc/auto.network /etc/dropbear/* /home/root/.ssh/* ; chmod 700 /home/root /home/root/.ssh"]
		if path.exists("/proc/stb/vmpeg/0/dst_width"):
			restorecmdlist += ["echo 0 > /proc/stb/vmpeg/0/dst_height", "echo 0 > /proc/stb/vmpeg/0/dst_left", "echo 0 > /proc/stb/vmpeg/0/dst_top", "echo 0 > /proc/stb/vmpeg/0/dst_width"]
		restorecmdlist.insert(0, "cd /etc/enigma2/ ; rm -R * ")
		restorecmdlist.append("/etc/init.d/autofs restart ; /etc/init.d/softcam restart")
		print("[SOFTWARE MANAGER] Restore Settings !!!!")

		self.session.open(Console, title = _("Restoring..."), cmdlist = restorecmdlist, finishedCallback = self.restoreFinishedCB)

	def restoreFinishedCB(self,retval = None):
		self.session.openWithCallback(self.checkPlugins, RestartNetwork)

	def checkPlugins(self):
		if path.exists("/tmp/installed-list.txt"):
			self.session.openWithCallback(self.restartGUI, installedPlugins)
		else:
			self.restartGUI()

	def restartGUI(self, ret = None):
		self.session.openWithCallback(self.restartGUIornot, MessageBox, _("Do you want to completely reboot your box now? \nIf not, only Enigma is restarting."))

	def restartGUIornot(self, ret = False):
		if ret == True:
			self.session.open(Console, title = _("Your %s %s will Reboot...")% (getMachineBrand(), getMachineName()), cmdlist = ["killall -9 enigma2 ; reboot"])
		else:
			self.session.open(Console, title = _("Your %s %s will restart Enigma2...")% (getMachineBrand(), getMachineName()), cmdlist = ["killall -9 enigma2"])

	def runAsync(self, finished_cb):
		self.doRestore()

class RestartNetwork(Screen):

	def __init__(self, session):
		Screen.__init__(self, session)
		skin = """
			<screen name="RestartNetwork" position="center,center" size="600,100" title="Restart Network Adapter">
			<widget name="label" position="10,30" size="500,50" halign="center" font="Regular;20" transparent="1" foregroundColor="white" />
			</screen> """
		self.skin = skin
		self["label"] = Label(_("Please wait while your network is restarting..."))
		self["summary_description"] = StaticText(_("Please wait while your network is restarting..."))
		self.onShown.append(self.setWindowTitle)
		self.onLayoutFinish.append(self.restartLan)

	def setWindowTitle(self):
		self.setTitle(_("Restart Network Adapter"))

	def restartLan(self):
		print("[SOFTWARE MANAGER] Restart Network")
		iNetwork.restartNetwork(self.restartLanDataAvail)

	def restartLanDataAvail(self, data):
		if data is True:
			iNetwork.getInterfaces(self.getInterfacesDataAvail)

	def getInterfacesDataAvail(self, data):
		self.close()

class installedPlugins(Screen):
	UPDATE = 0
	LIST = 1

	skin = """
		<screen position="center,center" size="600,100" title="Install Plugins" >
		<widget name="label" position="10,30" size="570,50" halign="center" font="Regular;20" transparent="1" foregroundColor="white" />
		</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		Screen.setTitle(self, _("Install Plugins"))
		self["label"] = Label(_("Please wait while we check your installed plugins..."))
		self["summary_description"] = StaticText(_("Please wait while we check your installed plugins..."))
		self.type = self.UPDATE
		self.container = eConsoleAppContainer()
		self.container.appClosed.append(self.runFinished)
		self.container.dataAvail.append(self.dataAvail)
		self.remainingdata = ""
		self.pluginsInstalled = []
		self.doUpdate()

	def doUpdate(self):
		print("[SOFTWARE MANAGER] update package list")
		self.container.execute("opkg update")

	def doList(self):
		print("[SOFTWARE MANAGER] read installed package list")
		self.container.execute("opkg list-installed | egrep 'enigma2-plugin-|task-base|packagegroup-base'")

	def dataAvail(self, strData):
		strData = six.ensure_str(strData)
		if self.type == self.LIST:
			strData = self.remainingdata + strData
			lines = strData.split('\n')
			if len(lines[-1]):
				self.remainingdata = lines[-1]
				lines = lines[0:-1]
			else:
				self.remainingdata = ""
			for x in lines:
				self.pluginsInstalled.append(x[:x.find(' - ')])

	def runFinished(self, retval):
		if self.type == self.UPDATE:
			self.type = self.LIST
			self.doList()
		elif self.type == self.LIST:
			self.readPluginList()

	def readPluginList(self):
		installedpkgs=ShellCompatibleFunctions.listpkg(type="installed")
		self.PluginList = []
		with open('/tmp/installed-list.txt') as f:
			for line in f:
				if line.strip() not in installedpkgs:
					self.PluginList.append(line.strip())
		f.close()
		self.createMenuList()

	def createMenuList(self):
		self.Menulist = []
		for x in self.PluginList:
			if x not in self.pluginsInstalled:
				self.Menulist.append(SettingsEntry(x, True))
		if len(self.Menulist) == 0:
			self.close()
		else:
			if os.path.exists("/media/hdd/images/config/plugins") and config.misc.firstrun.value:
				self.startInstall(True)
			else:
				self.session.openWithCallback(self.startInstall, MessageBox, _("Backup plugins found\ndo you want to install now?"))

	def startInstall(self, ret = None):
		if ret:
			self.session.openWithCallback(self.restoreCB, RestorePlugins, self.Menulist)
		else:
			self.close()

	def restoreCB(self, ret = None):
		self.close()

class RestorePlugins(Screen):

	def __init__(self, session, menulist):
		Screen.__init__(self, session)
		Screen.setTitle(self, _("Restore Plugins"))
		self.index = 0
		self.list = menulist
		for r in menulist:
			print("[SOFTWARE MANAGER] Plugin to restore: %s" % r[0])
		self.container = eConsoleAppContainer()
		self["menu"] = List(list())
		self["menu"].onSelectionChanged.append(self.selectionChanged)
		self["key_green"] = Button(_("Install"))
		self["key_red"] = Button(_("Cancel"))
		self["summary_description"] = StaticText("")

		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
				{
					"red": self.exit,
					"green": self.green,
					"cancel": self.exit,
					"ok": self.ok
				}, -2)

		self["menu"].setList(menulist)
		self["menu"].setIndex(self.index)
		self.selectionChanged()
		self.onShown.append(self.setWindowTitle)

	def setWindowTitle(self):
		self.setTitle(_("Restore Plugins"))

	def exit(self):
		self.close()

	def green(self):
		pluginlist = []
		self.myipklist = []
		for x in self.list:
			if x[2]:
				myipk = self.SearchIPK(x[0])
				if myipk:
					self.myipklist.append(myipk)
				else:
					pluginlist.append(x[0])
		if len(pluginlist) > 0:
			if len(self.myipklist) > 0:
				self.session.open(Console, title = _("Installing plugins..."), cmdlist = ['opkg --force-overwrite install ' + ' '.join(pluginlist)], finishedCallback = self.installLocalIPK, closeOnSuccess = True)
			else:
				self.session.open(Console, title = _("Installing plugins..."), cmdlist = ['opkg --force-overwrite install ' + ' '.join(pluginlist)], finishedCallback = self.exit, closeOnSuccess = True)
		elif len(self.myipklist) > 0:
			self.installLocalIPK()

	def installLocalIPK(self):
		self.session.open(Console, title = _("Installing plugins..."), cmdlist = ['opkg --force-overwrite install ' + ' '.join(self.myipklist)], finishedCallback = self.exit, closeOnSuccess = True)

	def ok(self):
		index = self["menu"].getIndex()
		item = self["menu"].getCurrent()[0]
		state = self["menu"].getCurrent()[2]
		if state:
			self.list[index] = SettingsEntry(item, False)
		else:
			self.list[index] = SettingsEntry(item, True)

		self["menu"].setList(self.list)
		self["menu"].setIndex(index)

	def selectionChanged(self):
		index = self["menu"].getIndex()
		if index == None:
			index = 0
		else:
			self["summary_description"].text = self["menu"].getCurrent()[0]
		self.index = index

	def drawList(self):
		self["menu"].setList(self.Menulist)
		self["menu"].setIndex(self.index)

	def exitNoPlugin(self, ret):
		self.close()

	def SearchIPK(self, ipkname):
		ipkname = ipkname + "*"
		search_dirs = [ "/media/hdd", "/media/usb" ]
		sdirs = " ".join(search_dirs)
		cmd = 'find %s -name "%s" | grep -iv "./open-multiboot/*" | head -n 1' % (sdirs, ipkname)
		res = popen(cmd).read()
		if res == "":
			return None
		else:
			return res.replace("\n", "")
