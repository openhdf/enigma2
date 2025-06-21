# for localized messages
from . import _
from enigma import *
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Sources.List import List
from Tools.Directories import resolveFilename, SCOPE_CURRENT_PLUGIN
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Tools.LoadPixmap import LoadPixmap
from Components.Button import Button
from Components.Label import Label
from Components.SystemInfo import BoxInfo
from Screens.MessageBox import MessageBox
from Screens.ChoiceBox import ChoiceBox
from Screens.Standby import TryQuitMainloop
from .HddPartitions import HddPartitions
from .HddInfo import HddInfo
from .Disks import Disks
from .ExtraMessageBox import ExtraMessageBox
from .ExtraActionBox import ExtraActionBox
from .MountPoints import MountPoints
import os

FULLHD = False
if getDesktop(0).size().width() >= 1920:
	FULLHD = True

sfdisk = os.path.exists('/usr/sbin/sfdisk')


def DiskEntry(model, size, removable, rotational, internal):
	if not removable and internal and rotational:
		picture = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_PLUGIN, "SystemPlugins/DeviceManager/icons/disk.png"))
	elif internal and not rotational:
		picture = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_PLUGIN, "SystemPlugins/DeviceManager/icons/ssddisk.png"))
	else:
		picture = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_PLUGIN, "SystemPlugins/DeviceManager/icons/diskusb.png"))
	return (picture, model, size)


class HddSetup(Screen):
	if FULLHD:
		skin = """
		<screen name="HddSetup" position="center,center" size="560,430" title="Hard Drive Setup">
			<ePixmap pixmap="skin_default/buttons/red.png" position="0,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/green.png" position="140,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/yellow.png" position="280,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/blue.png" position="420,0" size="140,40" alphatest="on" />
			<widget name="key_red" position="0,0" zPosition="1" size="140,40" font="Regular;18" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
			<widget name="key_green" position="140,0" zPosition="1" size="140,40" font="Regular;18" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
			<widget name="key_yellow" position="280,0" zPosition="1" size="140,40" font="Regular;18" halign="center" valign="center" backgroundColor="#a08500" transparent="1" />
			<widget name="key_blue" position="420,0" zPosition="1" size="140,40" font="Regular;18" halign="center" valign="center" backgroundColor="#18188b" transparent="1" />
			<widget source="menu" render="Listbox" position="20,45" size="520,380" scrollbarMode="showOnDemand">
				<convert type="TemplatedMultiContent">
					{"template": [
						MultiContentEntryPixmapAlphaTest(pos = (5, 0), size = (48, 48), png = 0),
						MultiContentEntryText(pos = (65, 10), size = (330, 38), font=0, flags = RT_HALIGN_LEFT|RT_VALIGN_TOP, text = 1),
						MultiContentEntryText(pos = (405, 10), size = (125, 38), font=0, flags = RT_HALIGN_LEFT|RT_VALIGN_TOP, text = 2),
						],
						"fonts": [gFont("Regular", 22)],
						"itemHeight": 50
					}
				</convert>
			</widget>
		</screen>"""
	else:
		skin = """
		<screen name="HddSetup" position="center,center" size="560,430" title="Hard Drive Setup">
			<ePixmap pixmap="skin_default/buttons/red.png" position="0,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/green.png" position="140,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/yellow.png" position="280,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/blue.png" position="420,0" size="140,40" alphatest="on" />
			<widget name="key_red" position="0,0" zPosition="1" size="140,40" font="Regular;18" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
			<widget name="key_green" position="140,0" zPosition="1" size="140,40" font="Regular;18" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
			<widget name="key_yellow" position="280,0" zPosition="1" size="140,40" font="Regular;18" halign="center" valign="center" backgroundColor="#a08500" transparent="1" />
			<widget name="key_blue" position="420,0" zPosition="1" size="140,40" font="Regular;18" halign="center" valign="center" backgroundColor="#18188b" transparent="1" />
			<widget source="menu" render="Listbox" position="20,45" size="520,380" scrollbarMode="showOnDemand">
				<convert type="TemplatedMultiContent">
					{"template": [
						MultiContentEntryPixmapAlphaTest(pos = (5, 0), size = (48, 48), png = 0),
						MultiContentEntryText(pos = (65, 10), size = (330, 38), font=0, flags = RT_HALIGN_LEFT|RT_VALIGN_TOP, text = 1),
						MultiContentEntryText(pos = (405, 10), size = (125, 38), font=0, flags = RT_HALIGN_LEFT|RT_VALIGN_TOP, text = 2),
						],
						"fonts": [gFont("Regular", 22)],
						"itemHeight": 50
					}
				</convert>
			</widget>
		</screen>"""

	def __init__(self, session, args=0):
		self.session = session
		Screen.__init__(self, session)
		self.disks = list()
		self.mdisks = Disks()
		self.asHDD = False
		for disk in self.mdisks.disks:
			size_kb = disk[1] / 1024
			size_mb = size_kb / 1024
			size_gb = size_mb / 1024
			size_tb = size_gb / 1024
			if size_tb > 1:
				capacity = "%.2f TB" % size_tb
			elif size_gb > 1:
				capacity = "%.2f GB" % size_gb
			else:
				capacity = "%.2f MB" % size_mb
			if disk[4] and disk[3]:
				fullname = disk[4] + " (" + disk[3] + ")"
			elif disk[4]:
				fullname = disk[4]
			elif disk[3]:
				fullname = disk[3]
			else:
				fullname = "-?-"
			self.disks.append(DiskEntry(fullname, capacity, disk[2], disk[6], disk[7]))
		self["menu"] = List(self.disks)
		self["key_red"] = Button(_("Exit"))
		self["key_green"] = Button(_("Info"))
		if sfdisk:
			self["key_yellow"] = Button(_("Initialize"))
		else:
			self["key_yellow"] = Button("")
		self["key_blue"] = Button(_("Partitions"))
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
		{
			"blue": self.blue,
			"yellow": self.yellow,
			"green": self.green,
			"red": self.quit,
			"cancel": self.quit,
		}, -2)
		self.onShown.append(self.setWindowTitle)

	def setWindowTitle(self):
		self.setTitle(_("Device Manager"))

	def isExt4Supported(self):
		return "ext4" in open("/proc/filesystems").read()

	def mkfs(self):
		self.formatted += 1
		disk1 = self.mdisks.disks[self.sindex][0]
		if "mmcblk" in disk1:
			disk1 = disk1 + "p"
		return self.mdisks.mkfs(disk1, self.formatted, self.fsresult)

	def refresh(self):
		self.disks = list()
		self.mdisks = Disks()
		for disk in self.mdisks.disks:
			size = int(disk[1] / 1024)
			if (((float(size) / 1024) / 1024) / 1024) > 1:
				capacity = "%d %s" % (int(round((((float(size) / 1024) / 1024) / 1024), 2)), "TB")
			elif ((size / 1024) / 1024) > 1:
				capacity = "%d %s" % (int(round(((float(size) / 1024) / 1024), 2)), "GB")
			else:
				capacity = "%d %s" % (int(round((float(size) / 1024), 2)), "MB")
			if disk[4] and disk[3]:
				fullname = disk[4] + " (" + disk[3] + ")"
			elif disk[4]:
				fullname = disk[4]
			elif disk[3]:
				fullname = disk[3]
			else:
				fullname = "-?-"
			self.disks.append(DiskEntry(fullname, capacity, disk[2], disk[6], disk[7]))

		self["menu"].setList(self.disks)

	def checkDefault(self):
		mp = MountPoints()
		mp.read()
		disk1 = self.mdisks.disks[self.sindex][0]
		if "mmcblk" in disk1:
			disk1 = disk1 + "p"
		if self.asHDD and not mp.exist("/media/hdd"):
			mp.add(disk1, 1, "/media/hdd")
			mp.write()
			mp.mount(disk1, 1, "/media/hdd")
			os.system("mkdir -p /media/hdd/movie")
			message = _("Fixed mounted first initialized Storage Device to /media/hdd. It needs a system restart in order to take effect.\nRestart your %s %s now?") % (BoxInfo.getItem("displaybrand"), BoxInfo.getItem("displaymodel"))
			mbox = self.session.openWithCallback(self.restartBox, MessageBox, message, MessageBox.TYPE_YESNO)
			mbox.setTitle(_("Restart %s %s") % (BoxInfo.getItem("displaybrand"), BoxInfo.getItem("displaymodel")))

	def restartBox(self, answer):
		if answer is True:
			self.session.open(TryQuitMainloop, 2)

	def format(self, result):
		if result != 0:
			self.session.open(MessageBox, _("Cannot format partition %d") % (self.formatted), MessageBox.TYPE_ERROR)
		if self.result == 0:
			if self.formatted > 0:
				self.checkDefault()
				self.refresh()
				return
		elif self.result > 0 and self.result < 3:
			if self.formatted > 1:
				self.checkDefault()
				self.refresh()
				return
		elif self.result == 3:
			if self.formatted > 2:
				self.checkDefault()
				self.refresh()
				return
		elif self.result == 4:
			if self.formatted > 3:
				self.checkDefault()
				self.refresh()
				return
		self.session.openWithCallback(self.format, ExtraActionBox, _("Formatting partition %d") % (self.formatted + 1), _("Initialize disk"), self.mkfs)

	def fdiskEnded(self, result):
		if result == 0:
			self.format(0)
		elif result == -1:
			self.session.open(MessageBox, _("Cannot umount current device.\nA record in progress, timeshift or some external tools (like samba, swapfile and nfsd) may cause this problem.\nPlease stop this actions/applications and try again"), MessageBox.TYPE_ERROR)
		else:
			self.session.open(MessageBox, _("Partitioning failed!"), MessageBox.TYPE_ERROR)

	def fdisk(self):
		disk1 = self.mdisks.disks[self.sindex][0]
		return self.mdisks.fdisk(disk1, self.mdisks.disks[self.sindex][1], self.result, self.fsresult)

	def initialaze(self, result):
		if not self.isExt4Supported():
			result += 1
		if result != 6:
			disk1 = self.mdisks.disks[self.sindex][0]
			if "mmcblk" in disk1:
				disk1 = disk1 + "p"
			self.fsresult = result
			self.formatted = 0
			mp = MountPoints()
			mp.read()
			mp.deleteDisk(disk1)
			mp.write()
			self.session.openWithCallback(self.fdiskEnded, ExtraActionBox, _("Partitioning..."), _("Initialize disk"), self.fdisk)

	def chooseFSType(self, result):
		if result != 5:
			self.result = result
			if self.isExt4Supported():
				self.session.openWithCallback(self.initialaze, ExtraMessageBox, _("Format as"), _("Partitioner"),
											[["Ext4", "partitionmanager.png"],
											["Ext3", "partitionmanager.png"],
											["Ext2", "partitionmanager.png"],
											["NTFS", "partitionmanager.png"],
											["exFAT", "partitionmanager.png"],
											["Fat32", "partitionmanager.png"],
											[_("Cancel"), "cancel.png"],
											], 1, 6)
			else:
				self.session.openWithCallback(self.initialaze, ExtraMessageBox, _("Format as"), _("Partitioner"),
											[["Ext3", "partitionmanager.png"],
											["Ext2", "partitionmanager.png"],
											["NTFS", "partitionmanager.png"],
											["exFAT", "partitionmanager.png"],
											["Fat32", "partitionmanager.png"],
											[_("Cancel"), "cancel.png"],
											], 1, 5)

	def yellow(self):
		self.asHDD = False
		if sfdisk and len(self.mdisks.disks) > 0:
			_list = [(_("No - simple"), "simple"), (_("Yes - fstab entry as /media/hdd"), "as_hdd")]

			def extraOption(ret):
				if ret:
					if ret[1] == "as_hdd":
						self.asHDD = True
					self.yellowAswer()
			self.session.openWithCallback(extraOption, ChoiceBox, title=_("Initialize as HDD?"), list=_list)

	def yellowAswer(self):
		if sfdisk and len(self.mdisks.disks) > 0:
			self.sindex = self['menu'].getIndex()
			self.session.openWithCallback(self.chooseFSType, ExtraMessageBox, _("Please select your preferred configuration."), _("Partitioner"),
										[[_("One partition"), "partitionmanager.png"],
										[_("Two partitions (50% - 50%)"), "partitionmanager.png"],
										[_("Two partitions (75% - 25%)"), "partitionmanager.png"],
										[_("Three partitions (33% - 33% - 33%)"), "partitionmanager.png"],
										[_("Four partitions (25% - 25% - 25% - 25%)"), "partitionmanager.png"],
										[_("Cancel"), "cancel.png"],
										], 1, 5)

	def green(self):
		if len(self.mdisks.disks) > 0:
			self.sindex = self['menu'].getIndex()
			self.session.open(HddInfo, self.mdisks.disks[self.sindex][0], self.mdisks.disks[self.sindex])

	def blue(self):
		if len(self.mdisks.disks) > 0:
			self.sindex = self['menu'].getIndex()
			if len(self.mdisks.disks[self.sindex][5]) == 0:
				self.session.open(MessageBox, _("You need to initialize your storage device first"), MessageBox.TYPE_ERROR)
			else:
				self.session.open(HddPartitions, self.mdisks.disks[self.sindex])

	def quit(self):
		self.close()
