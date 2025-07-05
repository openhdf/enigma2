# for localized messages
from . import _
from enigma import *
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Sources.List import List
from Tools.Directories import resolveFilename, SCOPE_CURRENT_PLUGIN
from Tools.LoadPixmap import LoadPixmap
from Components.Button import Button
from Components.Label import Label
from Screens.MessageBox import MessageBox

from .Disks import Disks
from .ExtraActionBox import ExtraActionBox
from .ExtraMessageBox import ExtraMessageBox
from .MountPoints import MountPoints
from .HddMount import HddMount
import os

FULLHD = False
if getDesktop(0).size().width() >= 1920:
	FULLHD = True

sfdisk = os.path.exists('/usr/sbin/sfdisk')


def PartitionEntry(description, size):
	picture = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_PLUGIN, "SystemPlugins/DeviceManager/icons/partitionmanager.png"))

	return (picture, description, size)


class HddPartitions(Screen):
	if FULLHD:
		skin = """
		<screen name="HddPartitions" position="center,center" size="560,430" title="Hard Drive Partitions">
			<ePixmap pixmap="skin_default/buttons/red.png" position="0,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/green.png" position="140,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/yellow.png" position="280,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/blue.png" position="420,0" size="140,40" alphatest="on" />
			<widget name="key_red" position="0,0" zPosition="1" size="140,40" font="Regular;18" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
			<widget name="key_green" position="140,0" zPosition="1" size="140,40" font="Regular;18" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
			<widget name="key_yellow" position="280,0" zPosition="1" size="140,40" font="Regular;18" halign="center" valign="center" backgroundColor="#a08500" transparent="1" />
			<widget name="key_blue" position="420,0" zPosition="1" size="140,40" font="Regular;18" halign="center" valign="center" backgroundColor="#18188b" transparent="1" />
			<widget name="label_disk" position="20,45" font="Regular;20" halign="center" size="520,25" valign="center" />
			<widget source="menu" render="Listbox" position="10,75" size="540,350" scrollbarMode="showOnDemand">
				<convert type="TemplatedMultiContent">
					{"template": [
						MultiContentEntryPixmapAlphaTest(pos = (5, 0), size = (48, 48), png = 0),
						MultiContentEntryText(pos = (65, 10), size = (375, 38), font=0, flags = RT_HALIGN_LEFT|RT_VALIGN_TOP, text = 1),
						MultiContentEntryText(pos = (435, 10), size = (125, 38), font=0, flags = RT_HALIGN_LEFT|RT_VALIGN_TOP, text = 2),
						],
						"fonts": [gFont("Regular", 18)],
						"itemHeight": 50
					}
				</convert>
			</widget>
		</screen>"""
	else:
		skin = """
		<screen name="HddPartitions" position="center,center" size="560,430" title="Hard Drive Partitions">
			<ePixmap pixmap="skin_default/buttons/red.png" position="0,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/green.png" position="140,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/yellow.png" position="280,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/blue.png" position="420,0" size="140,40" alphatest="on" />
			<widget name="key_red" position="0,0" zPosition="1" size="140,40" font="Regular;18" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
			<widget name="key_green" position="140,0" zPosition="1" size="140,40" font="Regular;18" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
			<widget name="key_yellow" position="280,0" zPosition="1" size="140,40" font="Regular;18" halign="center" valign="center" backgroundColor="#a08500" transparent="1" />
			<widget name="key_blue" position="420,0" zPosition="1" size="140,40" font="Regular;18" halign="center" valign="center" backgroundColor="#18188b" transparent="1" />
			<widget name="label_disk" position="20,45" font="Regular;20" halign="center" size="520,25" valign="center" />
			<widget source="menu" render="Listbox" position="20,75" size="520,350" scrollbarMode="showOnDemand">
				<convert type="TemplatedMultiContent">
					{"template": [
						MultiContentEntryPixmapAlphaTest(pos = (5, 0), size = (48, 48), png = 0),
						MultiContentEntryText(pos = (65, 10), size = (360, 38), font=0, flags = RT_HALIGN_LEFT|RT_VALIGN_TOP, text = 1),
						MultiContentEntryText(pos = (430, 10), size = (125, 38), font=0, flags = RT_HALIGN_LEFT|RT_VALIGN_TOP, text = 2),
						],
						"fonts": [gFont("Regular", 18)],
						"itemHeight": 50
					}
				</convert>
			</widget>
		</screen>"""

	def __init__(self, session, disk):
		self.session = session

		Screen.__init__(self, session)
		self.disk = disk
		self.disk1 = self.disk[0]
		if "mmcblk" in self.disk[0]:
			self.disk1 = self.disk[0] + "p"
		self.refreshMP(False)

		self["menu"] = List(self.partitions)
		self["menu"].onSelectionChanged.append(self.selectionChanged)
		self["key_red"] = Button(_("Exit"))
		self["key_green"] = Button("")
		self["key_yellow"] = Button("")
		self["key_blue"] = Button("")
		if disk[4] and disk[3]:
			fullname = disk[4] + " (" + disk[3] + ")"
		elif disk[4]:
			fullname = disk[4]
		elif disk[3]:
			fullname = disk[3]
		else:
			fullname = "'-?-'"
		self["label_disk"] = Label("%s - %s" % (self.disk[0], fullname))
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
		{
			"red": self.quit,
			"yellow": self.yellow,
			"green": self.green,
			"blue": self.blue,
			"cancel": self.quit,
		}, -2)

		self.onShown.append(self.setWindowTitle)
		if len(self.disk[5]) > 0: 
			if self.disk[5][0][3] == "83" or self.disk[5][0][3] == "7" or self.disk[5][0][3] == "b" or self.disk[5][0][3] == "c":
				self["key_green"].setText(_("Check"))
				if sfdisk:
					self["key_yellow"].setText(_("Format"))
				mp = self.mountpoints.get(self.disk1, 1)
				rmp = self.mountpoints.getRealMount(self.disk1, 1)
				if len(mp) > 0 or len(rmp) > 0:
					self.mounted = True
					self["key_blue"].setText(_("Unmount"))
				else:
					self.mounted = False
					self["key_blue"].setText(_("Mount"))

	def setWindowTitle(self):
		self.setTitle(_("Partitions"))

	def selectionChanged(self):
		self["key_green"].setText("")
		self["key_yellow"].setText("")
		self["key_blue"].setText("")

		if len(self.disk[5]) > 0:
			index = self["menu"].getIndex()
			if self.disk[5][index][3] == "83" or self.disk[5][index][3] == "7" or self.disk[5][index][3] == "b" or self.disk[5][index][3] == "c":
				self["key_green"].setText(_("Check"))
				if sfdisk:
					self["key_yellow"].setText(_("Format"))
				mp = self.mountpoints.get(self.disk1, index + 1)
				rmp = self.mountpoints.getRealMount(self.disk1, index + 1)
				if len(mp) > 0 or len(rmp) > 0:
					self.mounted = True
					self["key_blue"].setText(_("Unmount"))
				else:
					self.mounted = False
					self["key_blue"].setText(_("Mount"))

	def chkfs(self):
		disks = Disks()
		disk1 = self.disk[5][self.index][0][:3]
		if "mmc" in disk1:
			disk1 = self.disk1
		ret = disks.chkfs(disk1, self.index + 1, self.fstype)
		if ret == 0:
			self.session.open(MessageBox, _("Check disk finished with success"), MessageBox.TYPE_INFO)
		elif ret == -1:
			self.session.open(MessageBox, _("Cannot umount current drive.\nA record in progress, timeshift or some external tools (like samba, swapfile and nfsd) may cause this problem.\nPlease stop this actions/applications and try again"), MessageBox.TYPE_ERROR)
		else:
			self.session.open(MessageBox, _("Error checking disk. The disk may be damaged"), MessageBox.TYPE_ERROR)

	def mkfs(self):
		disks = Disks()
		disk1 = self.disk[5][self.index][0][:3]
		if "mmc" in disk1:
			disk1 = self.disk1
		ret = disks.mkfs(disk1, self.index + 1, self.fstype)
		if ret == 0:
			self.session.open(MessageBox, _("Format finished with success"), MessageBox.TYPE_INFO)
		elif ret == -2:
			self.session.open(MessageBox, _("Cannot format current drive.\nA record in progress, timeshift or some external tools (like samba, swapfile and nfsd) may cause this problem.\nPlease stop this actions/applications and try again"), MessageBox.TYPE_ERROR)
		else:
			self.session.open(MessageBox, _("Error formatting disk. The disk may be damaged"), MessageBox.TYPE_ERROR)

	def isExt4Supported(self):
		return "ext4" in open("/proc/filesystems").read()

	def domkfs(self, result):
		if self.disk[5][self.index][3] == "83":
			if self.isExt4Supported():
				if result < 3:
					self.fstype = result
					self.session.open(ExtraActionBox, _("Formatting disk %s") % self.disk[5][self.index][0], _("Formatting disk"), self.mkfs)
			else:
				if result < 2:
					self.fstype = result == 0 and 1 or 2
					self.session.open(ExtraActionBox, _("Formatting disk %s") % self.disk[5][self.index][0], _("Formatting disk"), self.mkfs)
		elif self.disk[5][self.index][3] == "7":
			if result < 2:
				self.fstype = result == 0 and 3 or 4
				self.session.open(ExtraActionBox, _("Formatting disk %s") % self.disk[5][self.index][0], _("Formatting disk"), self.mkfs)
		elif self.disk[5][self.index][3] == "b" or self.disk[5][self.index][3] == "c":
			if result < 1:
				self.fstype = 5
				self.session.open(ExtraActionBox, _("Formatting disk %s") % self.disk[5][self.index][0], _("Formatting disk"), self.mkfs)

	def green(self):
		if len(self.disk[5]) > 0:
			index = self["menu"].getIndex()
			if self.disk[5][index][3] == "83" or self.disk[5][index][3] == "7" or self.disk[5][index][3] == "b" or self.disk[5][index][3] == "c":
				self.index = index
				if self.disk[5][index][3] == "83":
					self.fstype = 0
				elif self.disk[5][index][3] == "7":
					self.fstype = 2
				elif self.disk[5][index][3] == "b" or self.disk[5][index][3] == "c":
					self.fstype = 3
				self.session.open(ExtraActionBox, _("Checking disk %s") % self.disk[5][index][0], _("Checking disk"), self.chkfs)

	def yellow(self):
		if sfdisk and len(self.disk[5]) > 0:
			self.index = self["menu"].getIndex()
			if self.disk[5][self.index][3] == "83":
				if self.isExt4Supported():
					self.session.openWithCallback(self.domkfs, ExtraMessageBox, _("Format as"), _("Partitioner"),
												[["Ext4", "partitionmanager.png"],
												["Ext3", "partitionmanager.png"],
												["Ext2", "partitionmanager.png"],
												[_("Cancel"), "cancel.png"],
												], 1, 3)
				else:
					self.session.openWithCallback(self.domkfs, ExtraMessageBox, _("Format as"), _("Partitioner"),
												[["Ext3", "partitionmanager.png"],
												["Ext2", "partitionmanager.png"],
												[_("Cancel"), "cancel.png"],
												], 1, 2)
			elif self.disk[5][self.index][3] == "7":
				self.session.openWithCallback(self.domkfs, ExtraMessageBox, _("Format as"), _("Partitioner"),
											[["NTFS", "partitionmanager.png"],
											["exFAT", "partitionmanager.png"],
											[_("Cancel"), "cancel.png"],
											], 1, 2)
			elif self.disk[5][self.index][3] == "b" or self.disk[5][self.index][3] == "c":
				self.session.openWithCallback(self.domkfs, ExtraMessageBox, _("Format as"), _("Partitioner"),
											[["Fat32", "partitionmanager.png"],
											[_("Cancel"), "cancel.png"],
											], 1, 1)

	def refreshMP(self, uirefresh=True):
		self.partitions = []
		self.mountpoints = MountPoints()
		self.mountpoints.read()
		count = 1
		for part in self.disk[5]:
			size = int(part[1] / 1024)
			if (((float(size) / 1024) / 1024) / 1024) > 1:
				capacity = "%d %s" % (int(round((((float(size) / 1024) / 1024) / 1024), 2)), "TB")
			elif ((size / 1024) / 1024) > 1:
				capacity = "%d %s" % (int(round(((float(size) / 1024) / 1024), 2)), "GB")
			else:
				capacity = "%d %s" % (int(round((float(size) / 1024), 2)), "MB")
			mp = self.mountpoints.get(self.disk1, count)
			rmp = self.mountpoints.getRealMount(self.disk1, count)
			if len(mp) > 0:
				self.partitions.append(PartitionEntry(_("P. %d - %s (Fixed: %s)") % (count, part[2], mp), capacity))
			elif len(rmp) > 0:
				self.partitions.append(PartitionEntry(_("P. %d - %s (Fast: %s)") % (count, part[2], rmp), capacity))
			else:
				self.partitions.append(PartitionEntry("P. %d - %s" % (count, part[2]), capacity))
			count += 1

		if uirefresh:
			self["menu"].setList(self.partitions)
			self.selectionChanged()

	def blue(self):
		if len(self.disk[5]) > 0:
			index = self["menu"].getIndex()
			if self.disk[5][index][3] != "83" and self.disk[5][index][3] != "7" and self.disk[5][index][3] != "b" and self.disk[5][index][3] != "c":
				return

		if len(self.partitions) > 0:
			self.sindex = self['menu'].getIndex()
			if self.mounted:
				mp = self.mountpoints.get(self.disk1, self.sindex + 1)
				rmp = self.mountpoints.getRealMount(self.disk1, self.sindex + 1)
				if len(mp) > 0:
					if self.mountpoints.isMounted(mp):
						if self.mountpoints.umount(mp):
							self.mountpoints.delete(mp)
							self.mountpoints.write()
						else:
							self.session.open(MessageBox, _("Cannot umount current device.\nA record in progress, timeshift or some external tools (like samba, swapfile and nfsd) may cause this problem.\nPlease stop this actions/applications and try again"), MessageBox.TYPE_ERROR)
					else:
						self.mountpoints.delete(mp)
						self.mountpoints.write()
				elif len(rmp) > 0:
					self.mountpoints.umount(rmp)
				self.refreshMP()
			else:
				self.session.openWithCallback(self.refreshMP, HddMount, self.disk1, self.sindex + 1)

	def quit(self):
		self.close()
