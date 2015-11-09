from enigma import *
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.MenuList import MenuList
from Components.GUIComponent import GUIComponent
from Components.HTMLComponent import HTMLComponent
from Tools.Directories import fileExists, crawlDirectory
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Components.Button import Button
from Components.Label import Label
from ExtrasList import ExtrasList
from Screens.MessageBox import MessageBox
from HddPartitions import HddPartitions
from HddInfo import HddInfo
from Disks import Disks
from ExtraMessageBox import ExtraMessageBox
from ExtraActionBox import ExtraActionBox
from MountPoints import MountPoints
import os
import sys
#from __init__ import _, loadPluginSkin

def DiskEntry(model, size, removable):
	res = [(model, size, removable)]
	if removable:
		picture = '/usr/lib/enigma2/python/Plugins/SystemPlugins/DeviceManager/icons/diskusb.png'
	else:
		picture = '/usr/lib/enigma2/python/Plugins/SystemPlugins/DeviceManager/icons/disk.png'
	if fileExists(picture):
		res.append(MultiContentEntryPixmapAlphaTest(pos=(5, 0), size=(48, 48), png=loadPNG(picture)))
		res.append(MultiContentEntryText(pos=(65, 10), size=(360, 38), font=0, text=model))
		res.append(MultiContentEntryText(pos=(435, 10), size=(125, 38), font=0, text=size))
	return res


class HddSetup(Screen):
	skin = """
	<screen name="HddSetup" position="center,center" size="560,430" title="Hard Drive Setup">
		<ePixmap pixmap="skin_default/buttons/red.png" position="0,0" size="140,40" alphatest="on" />
		<ePixmap pixmap="skin_default/buttons/green.png" position="140,0" size="140,40" alphatest="on" />
		<ePixmap pixmap="skin_default/buttons/yellow.png" position="280,0" size="140,40" alphatest="on" />
		<ePixmap pixmap="skin_default/buttons/blue.png" position="420,0" size="140,40" alphatest="on" />
		<widget name="key_red" position="0,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
		<widget name="key_green" position="140,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
		<widget name="key_yellow" position="280,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" transparent="1" />
		<widget name="key_blue" position="420,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" transparent="1" />
		<widget name="menu" position="20,45" size="520,380" scrollbarMode="showOnDemand" itemHeight="50" transparent="1" />
	</screen>"""

	def __init__(self, session, args = 0):
		self.session = session
		Screen.__init__(self, session)
		self.disks = list()
		self.mdisks = Disks()
		for disk in self.mdisks.disks:
			capacity = '%d MB' % (disk[1] / 1048576)
			self.disks.append(DiskEntry(disk[3], capacity, disk[2]))

		self['menu'] = ExtrasList(self.disks)
		self['key_red'] = Button(_('Exit'))
		self['key_green'] = Button('Info')
		self['key_yellow'] = Button(_('Initialize'))
		self['key_blue'] = Button(_('Partitions'))
		self['actions'] = ActionMap(['OkCancelActions', 'ColorActions'], {'red': self.quit,
			'yellow': self.yellow,
			'green': self.green,
			'blue': self.blue,
			'cancel': self.quit}, -2)
		self.onShown.append(self.setWindowTitle)

	def setWindowTitle(self):
		self.setTitle(_('Device Manager'))

	def mkfs(self):
		self.formatted += 1
		return self.mdisks.mkfs(self.mdisks.disks[self.sindex][0], self.formatted)

	def refresh(self):
		self.disks = list()
		self.mdisks = Disks()
		for disk in self.mdisks.disks:
			capacity = '%d MB' % (disk[1] / 1048576)
			self.disks.append(DiskEntry(disk[3], capacity, disk[2]))

		self['menu'].setList(self.disks)

	def checkDefault(self):
		mp = MountPoints()
		mp.read()
		if not mp.exist('/hdd'):
			mp.add(self.mdisks.disks[self.sindex][0], 1, '/hdd')
			mp.write()
			mp.mount(self.mdisks.disks[self.sindex][0], 1, '/hdd')
			os.system('/bin/mkdir /hdd/movie')
			os.system('/bin/mkdir /hdd/music')
			os.system('/bin/mkdir /hdd/picture')

	def format(self, result):
		if result != 0:
			self.session.open(MessageBox, _('Cannot format partition %d' % self.formatted), MessageBox.TYPE_ERROR)
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
		self.session.openWithCallback(self.format, ExtraActionBox, _('Formatting partition %d') % (self.formatted + 1), 'Initialize disk', self.mkfs)

	def fdiskEnded(self, result):
		if result == 0:
			self.format(0)
		elif result == -1:
			self.session.open(MessageBox, _('Cannot umount device.\nA record in progress, timeshit or some external tools (like samba, swapfile and nfsd) may cause this problem.\nPlease stop this actions/applications and try again'), MessageBox.TYPE_ERROR)
		else:
			self.session.open(MessageBox, _('Partitioning failed!'), MessageBox.TYPE_ERROR)

	def fdisk(self):
		return self.mdisks.fdisk(self.mdisks.disks[self.sindex][0], self.mdisks.disks[self.sindex][1], self.result)

	def initialaze(self, result):
		if result != 5:
			self.result = result
			self.formatted = 0
			mp = MountPoints()
			mp.read()
			mp.deleteDisk(self.mdisks.disks[self.sindex][0])
			mp.write()
			self.session.openWithCallback(self.fdiskEnded, ExtraActionBox, _('Partitioning...'), _('Initialize disk'), self.fdisk)

	def yellow(self):
		if len(self.mdisks.disks) > 0:
			self.sindex = self['menu'].getSelectedIndex()
			self.session.openWithCallback(self.initialaze, ExtraMessageBox, _('Please select your preferred configuration.'), _('HDD Partitioner'), [[_('One partition'), 'partitionmanager.png'],
				[_('Two partitions (50% - 50%)'), 'partitionmanager.png'],
				[_('Two partitions (75% - 25%)'), 'partitionmanager.png'],
				[_('Three partitions (33% - 33% - 33%)'), 'partitionmanager.png'],
				[_('Four partitions (25% - 25% - 25% - 25%)'), 'partitionmanager.png'],
				[_('Cancel'), 'cancel.png']], 1, 5)
				
	def green(self):
		if len(self.mdisks.disks) > 0:
			self.sindex = self['menu'].getSelectedIndex()
			self.session.open(HddInfo, self.mdisks.disks[self.sindex][0])
			
	def blue(self):
		if len(self.mdisks.disks) > 0:
			self.sindex = self['menu'].getSelectedIndex()
			self.session.open(HddPartitions, self.mdisks.disks[self.sindex])
			
	def quit(self):
		self.close()