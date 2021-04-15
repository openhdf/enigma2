from __future__ import print_function
#################################################################################
#       FULL BACKUP UYILITY FOR ENIGMA2, SUPPORTS THE MODELS OE-A 4.x     		#
#					MAKES A FULLBACKUP READY FOR FLASHING.						#
#################################################################################

from __future__ import absolute_import
from __future__ import division
from enigma import getEnigmaVersionString
from Screens.Screen import Screen
from Components.Button import Button
from Components.SystemInfo import SystemInfo
from Components.Label import Label
from Components.ActionMap import ActionMap
from Components.About import about
from Components import Harddisk
from Screens.Console import Console
from Screens.MessageBox import MessageBox
from time import time, strftime, localtime
from os import listdir, makedirs, path, statvfs, system, walk
import sys
if sys.version_info[0] >= 3:
	import subprocess
else:
	import commands
import datetime
from boxbranding import getBoxType, getMachineBrand, getMachineName, getImageDistro, getDriverDate, getImageVersion, getImageBuild, getBrandOEM, getMachineBuild, getImageFolder, getMachineUBINIZE, getMachineMKUBIFS, getMachineMtdKernel, getMachineMtdRoot, getMachineKernelFile, getMachineRootFile, getImageFileSystem

VERSION = _("Version %s %s.1") %(getImageDistro().upper(), getImageVersion())

HaveGZkernel = True
if SystemInfo["HasRootSubdir"] or getMachineBuild() in ('multibox', 'gbmv200', 'viper4k', 'i55plus', 'osmio4k', 'osmio4kplus', 'osmini4k', 'sf8008', 'cc1', 'dags72604', 'u41', 'u51', 'u52', 'u53', 'u54', 'u55', 'u56', 'h9', 'h9combo', 'u5', 'u5pvr', 'sf5008', 'et1x000', 'hd51', 'hd52', 'sf4008', 'dags7252', 'gb7252', 'vs1500', 'h7', 'xc7439', '8100s', 'dm7080', 'dm820', 'dm520', 'dm525', 'dm900'):
	HaveGZkernel = False

def Freespace(dev):
	statdev = statvfs(dev)
	space = (statdev.f_bavail * statdev.f_frsize) // 1024
	print("[FULL BACKUP] Free space on %s = %i kilobytes" %(dev, space))
	return space

class ImageBackup(Screen):
	skin = """
	<screen position="center,center" size="560,400" title="Image Backup">
		<ePixmap position="0,360"   zPosition="1" size="140,40" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on" />
		<ePixmap position="140,360" zPosition="1" size="140,40" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="on" />
		<ePixmap position="280,360" zPosition="1" size="140,40" pixmap="skin_default/buttons/yellow.png" transparent="1" alphatest="on" />
		<ePixmap position="420,360" zPosition="1" size="140,40" pixmap="skin_default/buttons/blue.png" transparent="1" alphatest="on" />
		<widget name="key_red" position="0,360" zPosition="2" size="140,40" valign="center" halign="center" font="Regular;21" transparent="1" shadowColor="black" shadowOffset="-1,-1" />
		<widget name="key_green" position="140,360" zPosition="2" size="140,40" valign="center" halign="center" font="Regular;21" transparent="1" shadowColor="black" shadowOffset="-1,-1" />
		<widget name="key_yellow" position="280,360" zPosition="2" size="140,40" valign="center" halign="center" font="Regular;21" transparent="1" shadowColor="black" shadowOffset="-1,-1" />
		<widget name="key_blue" position="420,360" zPosition="2" size="140,40" valign="center" halign="center" font="Regular;21" transparent="1" shadowColor="black" shadowOffset="-1,-1" />
		<widget name="info-hdd" position="10,30" zPosition="1" size="450,100" font="Regular;20" halign="left" valign="top" transparent="1" />
		<widget name="info-usb" position="10,150" zPosition="1" size="450,200" font="Regular;20" halign="left" valign="top" transparent="1" />
		<widget name="info-yellow" position="10,290" zPosition="1" size="550,200" font="Regular;20" halign="left" valign="top" transparent="1" />
	</screen>"""

	def __init__(self, session, args=0):
		Screen.__init__(self, session)
		self.session = session
		self.selection = 0
		self.MODEL = getBoxType()
		self.OEM = getBrandOEM()
		self.MACHINEBUILD = getMachineBuild()
		self.MACHINENAME = getMachineName()
		self.MACHINEBRAND = getMachineBrand()
		self.IMAGEFOLDER = getImageFolder()
		self.HDFIMAGEVERSION = getImageVersion()
		self.HDFIMAGEBUILD = getImageBuild()
		self.HDFIMAGENAME = getImageDistro()
		self.UBINIZE_ARGS = getMachineUBINIZE()
		self.MKUBIFS_ARGS = getMachineMKUBIFS()
		self.MTDKERNEL = getMachineMtdKernel()
		self.MTDROOTFS = getMachineMtdRoot()
		self.ROOTFSSUBDIR = "linuxrootfs1"
		self.ROOTFSBIN = getMachineRootFile()
		self.KERNELBIN = getMachineKernelFile()
		self.ROOTFSTYPE = getImageFileSystem().strip()
		self.IMAGEDISTRO = getImageDistro()
		self.DISTROVERSION = getImageVersion()
		self.selectionmultiboot = getImageDistro()

		if SystemInfo["canRecovery"]:
			self.EMMCIMG = SystemInfo["canRecovery"][0]
			self.MTDBOOT = SystemInfo["canRecovery"][1]
		else:
			self.MTDBOOT = "none"
			self.EMMCIMG = "none"

		if self.MACHINEBUILD in ("hd51", "vs1500", "h7", "8100s"):
			self.MTDBOOT = "mmcblk0p1"
			self.EMMCIMG = "disk.img"

		if self.MACHINEBUILD in ("xc7439", "osmio4k", "osmio4kplus", "osmini4k"):
			self.MTDBOOT = "mmcblk1p1"
			self.EMMCIMG = "emmc.img"

		if self.MACHINEBUILD in ("gbmv200", "cc1", "sf8008", "ustym4kpr"):
			self.MTDBOOT = "none"
			self.EMMCIMG = "usb_update.bin"

		print("[FULL BACKUP] BOX MACHINEBUILD = >%s<" %self.MACHINEBUILD)
		print("[FULL BACKUP] BOX MACHINENAME = >%s<" %self.MACHINENAME)
		print("[FULL BACKUP] BOX MACHINEBRAND = >%s<" %self.MACHINEBRAND)
		print("[FULL BACKUP] BOX MODEL = >%s<" %self.MODEL)
		print("[FULL BACKUP] OEM MODEL = >%s<" %self.OEM)
		print("[FULL BACKUP] IMAGEFOLDER = >%s<" %self.IMAGEFOLDER)
		print("[FULL BACKUP] UBINIZE = >%s<" %self.UBINIZE_ARGS)
		print("[FULL BACKUP] MKUBIFS = >%s<" %self.MKUBIFS_ARGS)
		print("[FULL BACKUP] MTDBOOT = >%s<" %self.MTDBOOT)
		print("[FULL BACKUP] MTDKERNEL = >%s<" %self.MTDKERNEL)
		print("[FULL BACKUP] MTDROOTFS = >%s<" %self.MTDROOTFS)
		print("[FULL BACKUP] ROOTFSBIN = >%s<" %self.ROOTFSBIN)
		print("[FULL BACKUP] KERNELBIN = >%s<" %self.KERNELBIN)
		print("[FULL BACKUP] ROOTFSTYPE = >%s<" %self.ROOTFSTYPE)
		print("[FULL BACKUP] EMMCIMG = >%s<" %self.EMMCIMG)
		print("[FULL BACKUP] IMAGEDISTRO = >%s<" %self.IMAGEDISTRO)
		print("[FULL BACKUP] DISTROVERSION = >%s<" %self.DISTROVERSION)

		self.error_files = ''
		self.list = self.list_files("/boot")
		self["key_green"] = Button("USB")
		self["key_red"] = Button("HDD")
		self["key_blue"] = Button(_("Exit"))
		if SystemInfo["HaveMultiBoot"]:
			self["key_yellow"] = Button(_("Current Startup"))
			self["info-multi"] = Label(_("You can switch between the startups with yellow button.\nIf no selection is made, the current startup is automatically taken."))
			self.read_current_multiboot()
		else:
			self["key_yellow"] = Button("")
			self["info-multi"] = Label(" ")
		self["info-usb"] = Label(_("USB = Do you want to make a back-up on USB?\nThis will take between 4 and 15 minutes depending on the used filesystem and is fully automatic.\nMake sure you first insert an USB flash drive before you select USB.\nThis USB drive must contain a file with the name\nbackupstick or backupstick.txt."))
		self["info-hdd"] = Label(_("HDD = Do you want to make an USB-back-up image on HDD? \nThis only takes 2 or 10 minutes and is fully automatic."))
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
		{
			"blue": self.quit,
			"yellow": self.yellow,
			"green": self.green,
			"red": self.red,
			"cancel": self.quit,
		}, -2)
		self.onShown.append(self.show_Errors)

	def show_Errors(self):
		if self.error_files:
			self.session.open(MessageBox, _('Index Error in the following files: %s') %self.error_files[:-2], type=MessageBox.TYPE_ERROR)
			self.error_files = ''

	def check_hdd(self):
		if not path.exists("/media/hdd"):
			self.session.open(MessageBox, _("No /hdd found !!\nPlease make sure you have a HDD mounted.\n"), type=MessageBox.TYPE_ERROR)
			return False
		if Freespace('/media/hdd') < 300000:
			self.session.open(MessageBox, _("Not enough free space on /hdd !!\nYou need at least 300Mb free space.\n"), type=MessageBox.TYPE_ERROR)
			return False
		return True

	def check_usb(self, dev):
		if Freespace(dev) < 300000:
			self.session.open(MessageBox, _("Not enough free space on %s !!\nYou need at least 300Mb free space.\n" % dev), type=MessageBox.TYPE_ERROR)
			return False
		return True

	def quit(self):
		self.close()

	def red(self):
		if self.check_hdd():
			self.doFullBackup("/hdd")

	def green(self):
		USB_DEVICE = self.SearchUSBcanidate()
		if USB_DEVICE == 'XX':
			text = _("No USB-Device found for fullbackup !!\n\n")
			text += _("To back-up directly to the USB-stick, the USB-stick MUST\n")
			text += _("contain a file with the name: \n\n")
			text += _("backupstick or backupstick.txt")
			self.session.open(MessageBox, text, type=MessageBox.TYPE_ERROR)
		else:
			if self.check_usb(USB_DEVICE):
				self.doFullBackup(USB_DEVICE)

	def yellow(self):
		if SystemInfo["HaveMultiBoot"]:
			self.selection = self.selection + 1
			if self.selection == len(self.list):
				self.selection = 0
			self["key_yellow"].setText(_(self.list[self.selection]))
			self.read_current_multiboot()
			self.selectionmultiboot1 = self.list[self.selection]
			self.selectionmultiboot = self.selectionmultiboot1.replace(" ", "").replace(".", "").lower()

	def read_current_multiboot(self):
		if SystemInfo["HasRootSubdir"]:
			self.MTDROOTFS = self.find_rootfs_dev(self.list[self.selection])
			self.MTDKERNEL = self.find_kernel_dev(self.list[self.selection])
			self.ROOTFSSUBDIR = self.find_rootfssubdir(self.list[self.selection])
		else:
			if self.MACHINEBUILD in ("hd51", "vs1500", "h7"):
				if self.list[self.selection] == "Recovery":
					cmdline = self.read_startup("/boot/STARTUP").split("=", 3)[3].split(" ", 1)[0]
				else:
					cmdline = self.read_startup("/boot/" + self.list[self.selection]).split("=", 3)[3].split(" ", 1)[0]
			elif self.MACHINEBUILD in ("8100s"):
				if self.list[self.selection] == "Recovery":
					cmdline = self.read_startup("/boot/STARTUP").split("=", 4)[4].split(" ", 1)[0]
				else:
					cmdline = self.read_startup("/boot/" + self.list[self.selection]).split("=", 4)[4].split(" ", 1)[0]
			elif self.MACHINEBUILD in ("gbmv200", "cc1", "sf8008", "ustym4kpro", "beyonwizv2", "viper4k"):
				if self.list[self.selection] == "Recovery":
					cmdline = self.read_startup("/boot/STARTUP").split("=", 1)[1].split(" ", 1)[0]
				else:
					cmdline = self.read_startup("/boot/" + self.list[self.selection]).split("=", 1)[1].split(" ", 1)[0]
			elif self.MACHINEBUILD in ("osmio4k", "osmio4kplus", "osmini4k"):
				if self.list[self.selection] == "Recovery":
					cmdline = self.read_startup("/boot/STARTUP").split("=", 1)[1].split(" ", 1)[0]
				else:
					cmdline = self.read_startup("/boot/" + self.list[self.selection]).split("=", 1)[1].split(" ", 1)[0]
			else:
				if self.list[self.selection] == "Recovery":
					cmdline = self.read_startup("/boot/cmdline.txt").split("=", 1)[1].split(" ", 1)[0]
				else:
					cmdline = self.read_startup("/boot/" + self.list[self.selection]).split("=", 1)[1].split(" ", 1)[0]
			cmdline = cmdline.lstrip("/dev/")
			self.MTDROOTFS = cmdline
			self.MTDKERNEL = cmdline[:-1] + str(int(cmdline[-1:]) -1)
		print("[FULL BACKUP] Multiboot rootfs ", self.MTDROOTFS)
		print("[FULL BACKUP] Multiboot kernel ", self.MTDKERNEL)
		print("[FULL BACKUP] rootfssubdir: ", self.ROOTFSSUBDIR)

	def read_startup(self, FILE):
		self.file = FILE
		try:
			with open(self.file, 'r') as myfile:
				data=myfile.read().replace('\n', '')
			myfile.close()
		except IOError:
			print("[ERROR] failed to open file %s" % file)
			data = " "
		return data

	def find_rootfs_dev(self, file):
		startup_content = self.read_startup("/boot/" + file)
		return startup_content[startup_content.find("root=")+5:].split()[0]

	def find_kernel_dev(self, file):
		startup_content = self.read_startup("/boot/" + file)
		return startup_content[startup_content.find("kernel=")+7:].split()[0]

	def find_rootfssubdir(self, file):
		startup_content = self.read_startup("/boot/" + file)
		rootsubdir = startup_content[startup_content.find("rootsubdir=")+11:].split()[0]
		if rootsubdir.startswith("linuxrootfs"):
			return rootsubdir
		return

	def list_files(self, PATH):
		files = []
		if SystemInfo["HaveMultiBoot"]:
			self.path = PATH
			if SystemInfo["HasRootSubdir"]:
				for name in listdir(self.path):
					if path.isfile(path.join(self.path, name)):
						try:
							cmdline = self.find_rootfssubdir(name)
							if cmdline == None:
								continue
						except IndexError:
							continue
						cmdline_startup = self.find_rootfssubdir("STARTUP")
						if (cmdline != cmdline_startup) and (name != "STARTUP"):
							files.append(name)
				files.insert(0, "STARTUP")
			else:
				for name in listdir(self.path):
					if path.isfile(path.join(self.path, name)):
						try:
							if self.MACHINEBUILD in ("hd51", "vs1500", "h7"):
								cmdline = self.read_startup("/boot/" + name).split("=", 3)[3].split(" ", 1)[0]
							elif self.MACHINEBUILD in ("8100s"):
								cmdline = self.read_startup("/boot/" + name).split("=", 4)[4].split(" ", 1)[0]
							else:
								cmdline = self.read_startup("/boot/" + name).split("=", 1)[1].split(" ", 1)[0]
							if cmdline in Harddisk.getextdevices("ext4"):
								files.append(name)
						except IndexError:
							print('[ImageBackup] - IndexError in file: %s' %name)
							self.error_files += '/boot/' + name + ', '
				if getMachineBuild() not in ("gb7252"):
					files.append("Recovery")
		else:
			files = "None"
		return files

	def SearchUSBcanidate(self):
		for paths, subdirs, files in walk("/media"):
			for _dir in subdirs:
				if not _dir == 'hdd' and not _dir == 'net':
					for _file in listdir("/media/" + _dir):
						if _file.find("backupstick") > -1:
							print("USB-DEVICE found on: /media/%s" % _dir)
							return "/media/" + _dir
			break
		return "XX"

	def doFullBackup(self, DIRECTORY):
		self.DIRECTORY = DIRECTORY
		self.TITLE = _("Full backup on %s") % (self.DIRECTORY)
		self.START = time()
		self.DATE = strftime("%Y%m%d_%H%M", localtime(self.START))
		self.IMAGEVERSION = self.imageInfo()
		if "ubi" in self.ROOTFSTYPE.split():
			self.MKFS = "/usr/sbin/mkfs.ubifs"
		elif "tar.bz2" in self.ROOTFSTYPE.split() or "tar.xz" in self.ROOTFSTYPE.split() or SystemInfo["HaveMultiBoot"] or SystemInfo["HasRootSubdir"] or self.MACHINEBUILD in ("gbmv200", "u51", "u52", "u53", "u54", "u56", "u5", "u5pvr", "cc1", "sf8008", "ustym4kpro", "beyonwizv2", "viper4k", "v8plus", "multibox", "h9combo", "hd60", "hd61"):
			self.MKFS = "/bin/tar"
			self.BZIP2 = "/usr/bin/bzip2"
		else:
			self.MKFS = "/usr/sbin/mkfs.jffs2"
		self.UBINIZE = "/usr/sbin/ubinize"
		self.NANDDUMP = "/usr/sbin/nanddump"
		self.FASTBOOT = "/usr/bin/ext2simg"
		self.EXTRAROOT = "%s/fullbackup_%s/%s" % (self.DIRECTORY, self.MODEL, self.DATE)
		self.WORKDIR= "%s/bi" %self.DIRECTORY
		self.TARGET="XX"

		if not path.exists(self.MKFS):
			text = "%s not found !!" %self.MKFS
			self.session.open(MessageBox, _(text), type=MessageBox.TYPE_ERROR)
			return

		if not path.exists(self.NANDDUMP):
			text = "%s not found !!" %self.NANDDUMP
			self.session.open(MessageBox, _(text), type=MessageBox.TYPE_ERROR)
			return

		self.SHOWNAME = "%s %s" %(self.MACHINEBRAND, self.MODEL)
		self.MAINDEST = "%s/fullbackup_%s/%s/%s" % (self.DIRECTORY, self.MODEL, self.DATE, self.IMAGEFOLDER)
		self.MAINDESTROOT = "%s/fullbackup_%s/%s" % (self.DIRECTORY, self.MODEL, self.DATE)

		self.message = "echo -e '"
		if getMachineBrand().startswith('A') or getMachineBrand().startswith('E') or getMachineBrand().startswith('I') or getMachineBrand().startswith('O') or getMachineBrand().startswith('U') or getMachineBrand().startswith('Xt'):
			self.message += _("Backup Tool for an") + ' %s' %self.SHOWNAME.upper() + " - " + VERSION + '\n'
		else:
			self.message += _("Backup Tool for") + ' %s' %self.SHOWNAME.upper() + " - " + VERSION + '\n'
		self.message += "________________________________________________________________________________\n\n"
		self.message += _("Please be patient, a backup will now be made,\n")
		if self.ROOTFSTYPE == "ubi":
			self.message += _("because of the used filesystem the back-up ")
			self.message += _("will take about 3-12 minutes for this system\n")
		elif SystemInfo["HaveMultiBoot"] and self.list[self.selection] == "Recovery":
			self.message += _("because of the used filesystem the back-up ")
			self.message += _("will take about 30 minutes for this system\n")
		elif "tar.bz2" in self.ROOTFSTYPE.split() or "tar.xz" in self.ROOTFSTYPE.split() or SystemInfo["HaveMultiBoot"]:
			self.message += _("because of the used filesystem the back-up ")
			self.message += _("will take about 2-10 minutes for this system\n")
		else:
			self.message += _("because of the used filesystem the back-up ")
			self.message += _("this will take between 2 and 9 minutes\n")
		self.message += "________________________________________________________________________________\n"
		self.message += "'"

		## PREPARING THE BUILDING ENVIRONMENT
		system("rm -rf %s" %self.WORKDIR)
		self.backuproot = "/tmp/bi/root"
		if SystemInfo["HaveMultiBoot"]:
			self.backuproot = "/tmp/bi/RootSubdir/"
		if not path.exists(self.WORKDIR):
			makedirs(self.WORKDIR)
		if not path.exists(self.backuproot):
			makedirs(self.backuproot)
		system("sync")
		if SystemInfo["HaveMultiBoot"]:
			if SystemInfo["HasRootSubdir"]:
				system("mount %s /tmp/bi/RootSubdir" %self.MTDROOTFS)
				self.backuproot = self.backuproot + self.ROOTFSSUBDIR
			else:
				system("mount /dev/%s %s" %(self.MTDROOTFS, self.backuproot))
		else:
			system("mount --bind / %s" %(self.backuproot))
		if "jffs2" in self.ROOTFSTYPE.split():
			cmd1 = "%s --root=%s --faketime --output=%s/root.jffs2 %s" % (self.MKFS,  self.backuproot, self.WORKDIR, self.MKUBIFS_ARGS)
			cmd2 = None
			cmd3 = None
		elif "tar.bz2" in self.ROOTFSTYPE.split() or SystemInfo["HaveMultiBoot"] or SystemInfo["HasRootSubdir"] or self.MACHINEBUILD in ("gbmv200", "u51", "u52", "u53", "u54", "u56", "u5", "u5pvr", "cc1", "sf8008", "ustym4kpro", "beyonwizv2", "viper4k", "v8plus", "multibox", "h9combo", "hd60", "hd61"):
			cmd1 = "%s -cf %s/rootfs.tar -C %s --exclude ./var/nmbd --exclude ./run --exclude ./var/lib/samba/private/msg.sock --exclude ./var/lib/samba/msg.sock ." % (self.MKFS, self.WORKDIR, self.backuproot)
			cmd2 = "%s %s/rootfs.tar" % (self.BZIP2, self.WORKDIR)
			cmd3 = None
		elif "tar.xz" in self.ROOTFSTYPE.split():
			cmd1 = "%s -cJf %s/rootfs.tar.xz -C %s --exclude ./var/nmbd --exclude ./run --exclude ./var/lib/samba/private/msg.sock --exclude ./var/lib/samba/msg.sock ." % (self.MKFS, self.WORKDIR, self.backuproot)
			cmd2 = None
			cmd3 = None
		else:
			f = open("%s/ubinize.cfg" %self.WORKDIR, "w")
			f.write("[ubifs]\n")
			f.write("mode=ubi\n")
			f.write("image=%s/root.ubi\n" %self.WORKDIR)
			f.write("vol_id=0\n")
			f.write("vol_type=dynamic\n")
			f.write("vol_name=rootfs\n")
			f.write("vol_flags=autoresize\n")
			f.close()
			ff = open("%s/root.ubi" %self.WORKDIR, "w")
			ff.close()
			cmd1 = "%s -r %s -o %s/root.ubi %s" % (self.MKFS,  self.backuproot, self.WORKDIR, self.MKUBIFS_ARGS)
			cmd2 = "%s -o %s/root.ubifs %s %s/ubinize.cfg" % (self.UBINIZE, self.WORKDIR, self.UBINIZE_ARGS, self.WORKDIR)
			cmd3 = "mv %s/root.ubifs %s/root.%s" %(self.WORKDIR, self.WORKDIR, self.ROOTFSTYPE)

		cmdlist = []
		cmdlist.append(self.message)
		cmdlist.append('echo "' + _("Create:") + ' %s\n"' %self.ROOTFSBIN)
		cmdlist.append(cmd1)
		if cmd2:
			cmdlist.append(cmd2)
		if cmd3:
			cmdlist.append(cmd3)
		#cmdlist.append("chmod 644 %s/%s" %(self.WORKDIR, self.ROOTFSBIN))

		if self.MODEL in ("gbquad4k", "gbue4k", "gbx34k"):
			cmdlist.append('echo " "')
			cmdlist.append('echo "' + _("Create:") + ' boot dump"')
			cmdlist.append("dd if=/dev/mmcblk0p1 of=%s/boot.bin" % self.WORKDIR)
			cmdlist.append('echo "' + _("Create:") + ' rescue dump"')
			cmdlist.append("dd if=/dev/mmcblk0p3 of=%s/rescue.bin" % self.WORKDIR)

		if self.MACHINEBUILD  in ("h9", "i55plus"):
			cmdlist.append('echo " "')
			cmdlist.append('echo "' + _("Create:") + ' fastboot dump"')
			cmdlist.append("dd if=/dev/mtd0 of=%s/fastboot.bin" % self.WORKDIR)
			cmdlist.append('echo "' + _("Create:") + ' bootargs dump"')
			cmdlist.append("dd if=/dev/mtd1 of=%s/bootargs.bin" % self.WORKDIR)
			cmdlist.append('echo "' + _("Create:") + ' baseparam dump"')
			cmdlist.append("dd if=/dev/mtd2 of=%s/baseparam.bin" % self.WORKDIR)
			cmdlist.append('echo "' + _("Create:") + ' pq_param dump"')
			cmdlist.append("dd if=/dev/mtd3 of=%s/pq_param.bin" % self.WORKDIR)
			cmdlist.append('echo "' + _("Create:") + ' logo dump"')
			cmdlist.append("dd if=/dev/mtd4 of=%s/logo.bin" % self.WORKDIR)

		if self.EMMCIMG == "usb_update.bin" and self.list[self.selection] == "Recovery":
			SEEK_CONT = (Harddisk.getFolderSize(self.backuproot)// 1024) + 100000
			cmdlist.append('echo "' + _("Create:") + " fastboot dump" + '"')
			cmdlist.append('cp -f /usr/share/fastboot.bin %s/fastboot.bin' %(self.WORKDIR))
			cmdlist.append('echo "' + _("Create:") + " bootargs dump" + '"')
			cmdlist.append('cp -f /usr/share/bootargs.bin %s/bootargs.bin' %(self.WORKDIR))
			cmdlist.append('echo "' + _("Create:") + " boot dump" + '"')
			cmdlist.append("dd if=/dev/mmcblk0p3 of=%s/boot.img" % self.WORKDIR)
			cmdlist.append('echo "' + _("Create:") + " baseparam dump" + '"')
			cmdlist.append("dd if=/dev/mmcblk0p4 of=%s/baseparam.img" % self.WORKDIR)
			cmdlist.append('echo "' + _("Create:") + " pq_param dump" + '"')
			cmdlist.append("dd if=/dev/mmcblk0p5 of=%s/pq_param.bin" % self.WORKDIR)
			cmdlist.append('echo "' + _("Create:") + " logo dump" + '"')
			cmdlist.append("dd if=/dev/mmcblk0p6 of=%s/logo.img" % self.WORKDIR)
			cmdlist.append('echo "' + _("Create:") + " deviceinfo dump" + '"')
			cmdlist.append("dd if=/dev/mmcblk0p7 of=%s/deviceinfo.bin" % self.WORKDIR)
			cmdlist.append('echo "' + _("Create:") + " apploader dump" + '"')
			cmdlist.append('cp -f /usr/share/apploader.bin %s/apploader.bin' %(self.WORKDIR))
			cmdlist.append('echo "' + _("Create:") + " rootfs dump" + '"')
			cmdlist.append("dd if=/dev/zero of=%s/rootfs.ext4 seek=%s count=60 bs=1024" % (self.WORKDIR, SEEK_CONT))
			cmdlist.append("mkfs.ext4 -F -i 4096 %s/rootfs.ext4" % (self.WORKDIR))
			cmdlist.append("mkdir -p %s/userdata" % self.WORKDIR)
			cmdlist.append("mount %s/rootfs.ext4 %s/userdata" %(self.WORKDIR, self.WORKDIR))
			cmdlist.append("mkdir -p %s/userdata/linuxrootfs1" % self.WORKDIR)
			cmdlist.append("mkdir -p %s/userdata/linuxrootfs2" % self.WORKDIR)
			cmdlist.append("mkdir -p %s/userdata/linuxrootfs3" % self.WORKDIR)
			cmdlist.append("mkdir -p %s/userdata/linuxrootfs4" % self.WORKDIR)
			cmdlist.append("rsync -aAX %s/ %s/userdata/linuxrootfs1/" % (self.backuproot, self.WORKDIR))
			cmdlist.append("umount %s/userdata" %(self.WORKDIR))

		cmdlist.append('echo " "')
		cmdlist.append('echo "' + _("Create:") + ' kerneldump"')
		cmdlist.append('echo " "')

		if SystemInfo["HaveMultiBoot"]:
			if SystemInfo["HasRootSubdir"]:
				cmdlist.append("dd if=%s of=%s/%s" % (self.MTDKERNEL, self.WORKDIR, self.KERNELBIN))
			else:
				cmdlist.append("dd if=/dev/%s of=%s/kernel.bin" % (self.MTDKERNEL, self.WORKDIR))
		elif self.MTDKERNEL.startswith('mmcblk0'):
			cmdlist.append("dd if=/dev/%s of=%s/%s" % (self.MTDKERNEL, self.WORKDIR, self.KERNELBIN))
		else:
			cmdlist.append("nanddump -a -f %s/vmlinux.gz /dev/%s" % (self.WORKDIR, self.MTDKERNEL))
		cmdlist.append('echo " "')

		if HaveGZkernel:
			cmdlist.append('echo "' + _("Check:") + ' kerneldump"')
		cmdlist.append("sync")

		if SystemInfo["HaveMultiBoot"] and self.list[self.selection] == "Recovery":
			BLOCK_SIZE=512
			BLOCK_SECTOR=2
			IMAGE_ROOTFS_ALIGNMENT=1024
			BOOT_PARTITION_SIZE=3072
			KERNEL_PARTITION_OFFSET = int(IMAGE_ROOTFS_ALIGNMENT) + int(BOOT_PARTITION_SIZE)
			KERNEL_PARTITION_SIZE=8192
			ROOTFS_PARTITION_OFFSET = int(KERNEL_PARTITION_OFFSET) + int(KERNEL_PARTITION_SIZE)
			ROOTFS_PARTITION_SIZE=819200
			SECOND_KERNEL_PARTITION_OFFSET = int(ROOTFS_PARTITION_OFFSET) + int(ROOTFS_PARTITION_SIZE)
			SECOND_ROOTFS_PARTITION_OFFSET = int(SECOND_KERNEL_PARTITION_OFFSET) + int(KERNEL_PARTITION_SIZE)
			THRID_KERNEL_PARTITION_OFFSET = int(SECOND_ROOTFS_PARTITION_OFFSET) + int(ROOTFS_PARTITION_SIZE)
			THRID_ROOTFS_PARTITION_OFFSET = int(THRID_KERNEL_PARTITION_OFFSET) + int(KERNEL_PARTITION_SIZE)
			FOURTH_KERNEL_PARTITION_OFFSET = int(THRID_ROOTFS_PARTITION_OFFSET) + int(ROOTFS_PARTITION_SIZE)
			FOURTH_ROOTFS_PARTITION_OFFSET = int(FOURTH_KERNEL_PARTITION_OFFSET) + int(KERNEL_PARTITION_SIZE)
			SWAP_PARTITION_OFFSET = int(FOURTH_ROOTFS_PARTITION_OFFSET) + int(ROOTFS_PARTITION_SIZE)
			EMMC_IMAGE = "%s/%s"% (self.WORKDIR, self.EMMCIMG)
			EMMC_IMAGE_SIZE=3817472
			EMMC_IMAGE_SEEK = int(EMMC_IMAGE_SIZE) * int(BLOCK_SECTOR)
			cmdlist.append('echo " "')
			cmdlist.append('echo "' + _("Create:") + ' Recovery Fullbackup %s"'% (self.EMMCIMG))
			cmdlist.append('echo " "')
			cmdlist.append('dd if=/dev/zero of=%s bs=%s count=0 seek=%s' % (EMMC_IMAGE, BLOCK_SIZE, EMMC_IMAGE_SEEK))
			cmdlist.append('parted -s %s mklabel gpt' %EMMC_IMAGE)
			PARTED_END_BOOT = int(IMAGE_ROOTFS_ALIGNMENT) + int(BOOT_PARTITION_SIZE)
			cmdlist.append('parted -s %s unit KiB mkpart boot fat16 %s %s' % (EMMC_IMAGE, IMAGE_ROOTFS_ALIGNMENT, PARTED_END_BOOT))
			PARTED_END_KERNEL1 = int(KERNEL_PARTITION_OFFSET) + int(KERNEL_PARTITION_SIZE)
			cmdlist.append('parted -s %s unit KiB mkpart kernel1 %s %s' % (EMMC_IMAGE, KERNEL_PARTITION_OFFSET, PARTED_END_KERNEL1))
			PARTED_END_ROOTFS1 = int(ROOTFS_PARTITION_OFFSET) + int(ROOTFS_PARTITION_SIZE)
			cmdlist.append('parted -s %s unit KiB mkpart rootfs1 ext4 %s %s' % (EMMC_IMAGE, ROOTFS_PARTITION_OFFSET, PARTED_END_ROOTFS1))
			PARTED_END_KERNEL2 = int(SECOND_KERNEL_PARTITION_OFFSET) + int(KERNEL_PARTITION_SIZE)
			cmdlist.append('parted -s %s unit KiB mkpart kernel2 %s %s' % (EMMC_IMAGE, SECOND_KERNEL_PARTITION_OFFSET, PARTED_END_KERNEL2))
			PARTED_END_ROOTFS2 = int(SECOND_ROOTFS_PARTITION_OFFSET) + int(ROOTFS_PARTITION_SIZE)
			cmdlist.append('parted -s %s unit KiB mkpart rootfs2 ext4 %s %s' % (EMMC_IMAGE, SECOND_ROOTFS_PARTITION_OFFSET, PARTED_END_ROOTFS2))
			PARTED_END_KERNEL3 = int(THRID_KERNEL_PARTITION_OFFSET) + int(KERNEL_PARTITION_SIZE)
			cmdlist.append('parted -s %s unit KiB mkpart kernel3 %s %s' % (EMMC_IMAGE, THRID_KERNEL_PARTITION_OFFSET, PARTED_END_KERNEL3))
			PARTED_END_ROOTFS3 = int(THRID_ROOTFS_PARTITION_OFFSET) + int(ROOTFS_PARTITION_SIZE)
			cmdlist.append('parted -s %s unit KiB mkpart rootfs3 ext4 %s %s' % (EMMC_IMAGE, THRID_ROOTFS_PARTITION_OFFSET, PARTED_END_ROOTFS3))
			PARTED_END_KERNEL4 = int(FOURTH_KERNEL_PARTITION_OFFSET) + int(KERNEL_PARTITION_SIZE)
			cmdlist.append('parted -s %s unit KiB mkpart kernel4 %s %s' % (EMMC_IMAGE, FOURTH_KERNEL_PARTITION_OFFSET, PARTED_END_KERNEL4))
			PARTED_END_ROOTFS4 = int(FOURTH_ROOTFS_PARTITION_OFFSET) + int(ROOTFS_PARTITION_SIZE)
			cmdlist.append('parted -s %s unit KiB mkpart rootfs4 ext4 %s %s' % (EMMC_IMAGE, FOURTH_ROOTFS_PARTITION_OFFSET, PARTED_END_ROOTFS4))
			cmdlist.append('parted -s %s unit KiB mkpart swap linux-swap %s 100%%' % (EMMC_IMAGE, SWAP_PARTITION_OFFSET))
			BOOT_IMAGE_SEEK = int(IMAGE_ROOTFS_ALIGNMENT) * int(BLOCK_SECTOR)
			cmdlist.append('dd if=/dev/%s of=%s seek=%s' % (self.MTDBOOT, EMMC_IMAGE, BOOT_IMAGE_SEEK))
			KERNAL_IMAGE_SEEK = int(KERNEL_PARTITION_OFFSET) * int(BLOCK_SECTOR)
			cmdlist.append('dd if=/dev/%s of=%s seek=%s' % (self.MTDKERNEL, EMMC_IMAGE, KERNAL_IMAGE_SEEK))
			ROOTFS_IMAGE_SEEK = int(ROOTFS_PARTITION_OFFSET) * int(BLOCK_SECTOR)
			cmdlist.append('dd if=/dev/%s of=%s seek=%s ' % (self.MTDROOTFS, EMMC_IMAGE, ROOTFS_IMAGE_SEEK))
		elif SystemInfo["HaveMultiBootDS"] and self.list[self.selection] == "Recovery":
			cmdlist.append('echo " "')
			cmdlist.append('echo "' + _("Create:") + ' Recovery Fullbackup %s"'% (self.EMMCIMG))
			cmdlist.append('echo " "')
			f = open("%s/emmc_partitions.xml" %self.WORKDIR, "w")
			f.write('<?xml version="1.0" encoding="GB2312" ?>\n')
			f.write('<Partition_Info>\n')
			f.write('<Part Sel="1" PartitionName="fastboot" FlashType="emmc" FileSystem="none" Start="0" Length="1M" SelectFile="fastboot.bin"/>\n')
			f.write('<Part Sel="1" PartitionName="bootargs" FlashType="emmc" FileSystem="none" Start="1M" Length="1M" SelectFile="bootargs.bin"/>\n')
			f.write('<Part Sel="1" PartitionName="bootoptions" FlashType="emmc" FileSystem="none" Start="2M" Length="1M" SelectFile="boot.img"/>\n')
			f.write('<Part Sel="1" PartitionName="baseparam" FlashType="emmc" FileSystem="none" Start="3M" Length="3M" SelectFile="baseparam.img"/>\n')
			f.write('<Part Sel="1" PartitionName="pqparam" FlashType="emmc" FileSystem="none" Start="6M" Length="4M" SelectFile="pq_param.bin"/>\n')
			f.write('<Part Sel="1" PartitionName="logo" FlashType="emmc" FileSystem="none" Start="10M" Length="4M" SelectFile="logo.img"/>\n')
			f.write('<Part Sel="1" PartitionName="deviceinfo" FlashType="emmc" FileSystem="none" Start="14M" Length="4M" SelectFile="deviceinfo.bin"/>\n')
			f.write('<Part Sel="1" PartitionName="loader" FlashType="emmc" FileSystem="none" Start="26M" Length="32M" SelectFile="apploader.bin"/>\n')
			f.write('<Part Sel="1" PartitionName="linuxkernel1" FlashType="emmc" FileSystem="none" Start="66M" Length="16M" SelectFile="kernel.bin"/>\n')
			if self.MACHINENAME in ("sf8008m"):
				f.write('<Part Sel="1" PartitionName="userdata" FlashType="emmc" FileSystem="ext3/4" Start="130M" Length="3580M" SelectFile="rootfs.ext4"/>\n')
			else:
				f.write('<Part Sel="1" PartitionName="userdata" FlashType="emmc" FileSystem="ext3/4" Start="130M" Length="7000M" SelectFile="rootfs.ext4"/>\n')
			f.write('</Partition_Info>\n')
			f.close()
			cmdlist.append('mkupdate -s 00000003-00000001-01010101 -f %s/emmc_partitions.xml -d %s/%s' % (self.WORKDIR, self.WORKDIR, self.EMMCIMG))
		elif self.MACHINEBUILD  in ("v8plus", "multibox", "h9combo", "hd60", "hd61"):
			cmdlist.append('echo " "')
			cmdlist.append('echo "' + _("Create: Recovery Fullbackup %s")% (self.EMMCIMG) + '"')
			cmdlist.append('echo " "')
			cmdlist.append('%s -zv %s/rootfs.ext4 %s/%s' % (self.FASTBOOT, self.WORKDIR, self.WORKDIR, self.EMMCIMG))
		print(cmdlist)
		self.session.open(Console, title=self.TITLE, cmdlist=cmdlist, finishedCallback=self.doFullBackupCB, closeOnSuccess=True)

	def doFullBackupCB(self):
		if HaveGZkernel:
			ret = commands.getoutput(' gzip -d %s/vmlinux.gz -c > /tmp/vmlinux.bin' % self.WORKDIR)
			if ret:
				text = "Kernel dump error\n"
				text += "Please Flash your Kernel new and Backup again"
				system('rm -rf /tmp/vmlinux.bin')
				self.session.open(MessageBox, _(text), type=MessageBox.TYPE_ERROR)
				return

		cmdlist = []
		cmdlist.append(self.message)
		if HaveGZkernel:
			cmdlist.append('echo "Kernel dump OK"')
			cmdlist.append("rm -rf /tmp/vmlinux.bin")
		cmdlist.append('echo "' + _("Almost there... ") + '"')
		cmdlist.append('echo "' + _("Now building the Backup Image") + '"')

		system('rm -rf %s' %self.MAINDEST)
		if not path.exists(self.MAINDEST):
			makedirs(self.MAINDEST)
		f = open("%s/imageversion" %self.MAINDEST, "w")
		f.write(self.IMAGEVERSION)
		f.close()

		if self.ROOTFSBIN == "rootfs.tar.bz2":
			system('mv %s/rootfs.tar.bz2 %s/rootfs.tar.bz2' %(self.WORKDIR, self.MAINDEST))
		else:
			system('mv %s/root.%s %s/%s' %(self.WORKDIR, self.ROOTFSTYPE, self.MAINDEST, self.ROOTFSBIN))
		if SystemInfo["canMultiBoot"] or self.MTDKERNEL.startswith('mmcblk0'):
			system('mv %s/%s %s/%s' %(self.WORKDIR, self.KERNELBIN, self.MAINDEST, self.KERNELBIN))
		else:
			system('mv %s/vmlinux.gz %s/%s' %(self.WORKDIR, self.MAINDEST, self.KERNELBIN))

		if self.ROOTFSBIN == "rootfs.tar.bz2":
			system('mv %s/rootfs.tar.bz2 %s/rootfs.tar.bz2' %(self.WORKDIR, self.MAINDEST))
		elif self.ROOTFSBIN == "rootfs.tar.xz":
			system('mv %s/rootfs.tar.xz %s/rootfs.tar.xz' %(self.WORKDIR, self.MAINDEST))
		else:
			system('mv %s/root.%s %s/%s' %(self.WORKDIR, self.ROOTFSTYPE, self.MAINDEST, self.ROOTFSBIN))
		if SystemInfo["HaveMultiBoot"]:
			system('mv %s/kernel.bin %s/kernel.bin' %(self.WORKDIR, self.MAINDEST))
		elif self.MTDKERNEL.startswith('mmcblk0'):
			system('mv %s/%s %s/%s' %(self.WORKDIR, self.KERNELBIN, self.MAINDEST, self.KERNELBIN))
		else:
			system('mv %s/vmlinux.gz %s/%s' %(self.WORKDIR, self.MAINDEST, self.KERNELBIN))

		if SystemInfo["HaveMultiBoot"] and self.list[self.selection] == "Recovery" or self.MACHINEBUILD  in ("v8plus", "multibox", "h9combo", "hd60", "hd61"):
			system('mv %s/%s %s/%s' %(self.WORKDIR, self.EMMCIMG, self.MAINDEST, self.EMMCIMG))
		elif self.MODEL in ("vuultimo4k", "vusolo4k", "vuduo2", "vusolo2", "vusolo", "vuduo", "vuultimo", "vuuno"):
			cmdlist.append('echo "This file forces a reboot after the update." > %s/reboot.update' %self.MAINDEST)
		elif self.MODEL in ("vuzero", "vusolose", "vuuno4k"):
			cmdlist.append('echo "This file forces the update." > %s/force.update' %self.MAINDEST)
		elif self.MODEL in ("novaip", "zgemmai55", "sf98", "xpeedlxpro", 'evoslim'):
			cmdlist.append('echo "This file forces the update." > %s/force' %self.MAINDEST)
		elif SystemInfo["HasRootSubdir"]:
			cmdlist.append('echo "Rename the unforce_%s.txt to force_%s.txt and move it to the root of your usb-stick" > %s/force_%s_READ.ME' %(self.MACHINEBUILD, self.MACHINEBUILD, self.MAINDEST, self.MACHINEBUILD))
			cmdlist.append('echo "When you enter the recovery menu then it will force to install the image in the linux1 selection" >> %s/force_%s_READ.ME' %(self.MAINDEST, self.MACHINEBUILD))
		else:
			cmdlist.append('echo "rename this file to "force" to force an update without confirmation" > %s/noforce' %self.MAINDEST)

		if self.MODEL in ("gbquad4k", "gbue4k", "gbx34k"):
			system('mv %s/boot.bin %s/boot.bin' %(self.WORKDIR, self.MAINDEST))
			system('mv %s/rescue.bin %s/rescue.bin' %(self.WORKDIR, self.MAINDEST))
			system('cp -f /usr/share/gpt.bin %s/gpt.bin' %(self.MAINDEST))

		if self.MACHINEBUILD in ("h9", "i55plus"):
			system('mv %s/fastboot.bin %s/fastboot.bin' %(self.WORKDIR, self.MAINDEST))
			system('mv %s/pq_param.bin %s/pq_param.bin' %(self.WORKDIR, self.MAINDEST))
			system('mv %s/bootargs.bin %s/bootargs.bin' %(self.WORKDIR, self.MAINDEST))
			system('mv %s/baseparam.bin %s/baseparam.bin' %(self.WORKDIR, self.MAINDEST))
			system('mv %s/logo.bin %s/logo.bin' %(self.WORKDIR, self.MAINDEST))

		if self.MACHINEBUILD in ("h9combo", "v8plus", "multibox", "hd60", "hd61"):
			system('mv %s/baseparam.bin %s/bootoptions.bin' %(self.WORKDIR, self.MAINDEST))
			system('mv %s/uImage %s/uImage' %(self.WORKDIR, self.MAINDEST))

		if self.MODEL in ("gbquad", "gbquadplus", "gb800ue", "gb800ueplus", "gbultraue", "gbultraueh", "twinboxlcd", "twinboxlcdci", "singleboxlcd", "sf208", "sf228"):
			lcdwaitkey = '/usr/share/lcdwaitkey.bin'
			lcdwarning = '/usr/share/lcdwarning.bin'
			if path.exists(lcdwaitkey):
				system('cp %s %s/lcdwaitkey.bin' %(lcdwaitkey, self.MAINDEST))
			if path.exists(lcdwarning):
				system('cp %s %s/lcdwarning.bin' %(lcdwarning, self.MAINDEST))

		if self.MODEL in ("e4hdultra", "protek4k"):
			lcdwarning = '/usr/share/lcdflashing.bmp'
			if path.exists(lcdwarning):
				system('cp %s %s/lcdflashing.bmp' %(lcdwarning, self.MAINDEST))

		if self.MODEL == "gb800solo":
			f = open("%s/burn.bat" % (self.MAINDESTROOT), "w")
			f.write("flash -noheader usbdisk0:gigablue/solo/kernel.bin flash0.kernel\n")
			f.write("flash -noheader usbdisk0:gigablue/solo/rootfs.bin flash0.rootfs\n")
			f.write('setenv -p STARTUP "boot -z -elf flash0.kernel: ')
			f.write("'rootfstype=jffs2 bmem=106M@150M root=/dev/mtdblock6 rw '")
			f.write('"\n')
			f.close()

		if self.MACHINEBUILD in ("h9", "i55plus"):
			cmdlist.append('cp -f /usr/share/fastboot.bin %s/fastboot.bin' %(self.MAINDESTROOT))
			cmdlist.append('cp -f /usr/share/bootargs.bin %s/bootargs.bin' %(self.MAINDESTROOT))

	#	if SystemInfo["canRecovery"] and self.list[self.selection] == "Recovery":
	#		cmdlist.append('7za a -r -bt -bd %s/%s-%s-%s-backup-%s_recovery.zip %s/*' %(self.DIRECTORY, self.IMAGEDISTRO, self.DISTROVERSION, self.MODEL, self.DATE, self.MAINDESTROOT))

		if SystemInfo["canRecovery"] and self.list[self.selection] == "Recovery":
			cmdlist.append('7za a -r -bt -bd %s/%s-%s-%s-backup-%s_recovery_emmc.zip %s/*' %(self.DIRECTORY, self.IMAGEDISTRO, self.DISTROVERSION, self.MODEL, self.DATE, self.MAINDESTROOT))
#		elif SystemInfo["HasRootSubdir"]:
#			cmdlist.append('echo "rename this file to "force" to force an update without confirmation" > %s/unforce_%s.txt' %(self.MAINDESTROOT, self.MACHINEBUILD))
#			cmdlist.append('7za a -r -bt -bd %s/%s-%s-%s-backup-%s_mmc.zip %s/*' %(self.DIRECTORY, self.IMAGEDISTRO, self.DISTROVERSION, self.MODEL, self.DATE, self.MAINDESTROOT))
#		else:
#			cmdlist.append('7za a -r -bt -bd %s/%s-%s-%s-backup-%s_usb.zip %s/*' %(self.DIRECTORY, self.IMAGEDISTRO, self.DISTROVERSION, self.MODEL, self.DATE, self.MAINDESTROOT))

		if SystemInfo["HaveMultiBoot"] and not SystemInfo["HasRootSubdir"]:
			imageversionfile = "/tmp/bi/RootSubdir/etc/image-version"
			if path.exists(imageversionfile) is True:
				system("less /tmp/bi/RootSubdir/etc/image-version | grep build= | cut -d= -f2 > /tmp/.imagebuild")
				brand = open("/tmp/.imagebuild", "r")
				self.backupbuild = brand.readline().replace('\n', '').lower()
				brand.close()
			else:
				self.backupbuild = "-"
			print("self.backupbuild: %s" %self.backupbuild)
			print("selectionmultiboot: %s" %self.selectionmultiboot)
			cmdlist.append('opkg install p7zip > /dev/null 2>&1')
			cmdlist.append('7za a -r -bt -bd -bb0 %s/full_backups/%s-%s-%s-%s-backup-%s_backup.zip %s/*' %(self.DIRECTORY, self.IMAGEDISTRO, self.DISTROVERSION, self.HDFIMAGEBUILD, self.MODEL, self.DATE, self.MAINDESTROOT))
		elif SystemInfo["HasRootSubdir"]:
			cmdlist.append('echo "rename this file to "force" to force an update without confirmation" > %s/unforce_%s.txt' %(self.MAINDESTROOT, self.MACHINEBUILD))
			cmdlist.append('7za a -r -bt -bd -bb0 %s/full_backups/%s-%s-%s-%s-backup-%s_mmc.zip %s/*' %(self.DIRECTORY, self.IMAGEDISTRO, self.DISTROVERSION, self.HDFIMAGEBUILD, self.MODEL, self.DATE, self.MAINDESTROOT))
		else:
			cmdlist.append('opkg install p7zip > /dev/null 2>&1')
			cmdlist.append('7za a -r -bt -bd -bb0 %s/full_backups/%s-%s-%s-%s-backup-%s.zip %s/*' %(self.DIRECTORY, self.IMAGEDISTRO, self.DISTROVERSION, self.HDFIMAGEBUILD, self.MODEL, self.DATE, self.MAINDESTROOT))

		cmdlist.append("sync")
		file_found = True

		if self.EMMCIMG == "usb_update.bin" and self.list[self.selection] == "Recovery":
			if not path.isfile("%s/%s" % (self.MAINDESTROOT, self.EMMCIMG)):
				print("[Image Backup] %s file not found" %(self.EMMCIMG))
				file_found = False
		else:
			if not path.isfile("%s/%s" % (self.MAINDEST, self.ROOTFSBIN)):
				print("[Image Backup] %s file not found" %(self.ROOTFSBIN))
				file_found = False

			if not path.isfile("%s/%s" % (self.MAINDEST, self.KERNELBIN)):
				print("[Image Backup] %s file not found" %(self.KERNELBIN))
				file_found = False

		if SystemInfo["HaveMultiBoot"] and not self.list[self.selection] == "Recovery":
			cmdlist.append('echo "________________________________________________________________________________\n"')
			if SystemInfo["HasRootSubdir"]:
				cmdlist.append('echo -e "' + _("Image created on:\n%s/full_backups/%s-%s-%s-%s-backup-%s_mmc.zip") %(self.DIRECTORY, self.IMAGEDISTRO, self.DISTROVERSION, self.HDFIMAGEBUILD, self.MODEL, self.DATE) + '"')
			else:
				cmdlist.append('echo -e "' + _("Image created on:\n%s/full_backups/%s-%s-%s-%s-backup-%s_backup.zip") %(self.DIRECTORY, self.IMAGEDISTRO, self.DISTROVERSION, self.HDFIMAGEBUILD, self.MODEL, self.DATE) + '"')
			cmdlist.append('echo "________________________________________________________________________________\n"')
			cmdlist.append('echo "' + _("To restore the image:") + '"')
			cmdlist.append('echo "' + _("Use OnlineFlash in SoftwareManager") + '"')
		elif file_found:
			cmdlist.append('echo "________________________________________________________________________________\n"')
			#if SystemInfo["canRecovery"]:
			#	cmdlist.append('echo "' + _("Image created on: %s/%s-%s-%s-backup-%s_recovery.zip") %(self.DIRECTORY, self.IMAGEDISTRO, self.DISTROVERSION, self.MODEL, self.DATE) + '"')
			cmdlist.append('echo -e "' + _("Image created on:\n%s/full_backups/%s-%s-%s-%s-backup-%s.zip") %(self.DIRECTORY, self.IMAGEDISTRO, self.DISTROVERSION, self.HDFIMAGEBUILD, self.MODEL, self.DATE) + '"')
			cmdlist.append('echo "________________________________________________________________________________\n"')
			cmdlist.append('echo "' + _("To restore the image:") + '"')
			cmdlist.append('echo "' + _("Please check the manual of the receiver") + '"')
			cmdlist.append('echo "' + _("on how to restore the image") + '"')
		else:
			cmdlist.append('echo "________________________________________________________________________________\n"')
			cmdlist.append('echo "' + _("Image creation failed - ") + '"')
			cmdlist.append('echo "' + _("Probable causes could be") + ':"')
			cmdlist.append('echo "' + _("     wrong back-up destination ") + '"')
			cmdlist.append('echo "' + _("     no space left on back-up device") + '"')
			cmdlist.append('echo "' + _("     no writing permission on back-up device") + '"')
			cmdlist.append('echo " "')

		cmdlist.append("rm -rf %s/fullbackup_%s" %(self.DIRECTORY, self.MODEL))

		if SystemInfo["HasRootSubdir"] or SystemInfo["HaveMultiBoot"]:
			cmdlist.append("umount /tmp/bi/RootSubdir > /dev/null 2>&1")
			cmdlist.append("rmdir /tmp/bi/RootSubdir > /dev/null 2>&1")
		else:
			cmdlist.append("umount /tmp/bi/root")
			cmdlist.append("rmdir /tmp/bi/root")
		cmdlist.append("rmdir /tmp/bi")
		cmdlist.append("rm -rf %s" % self.WORKDIR)
		cmdlist.append("sleep 5")
		END = time()
		DIFF = int(END - self.START)
		TIMELAP = str(datetime.timedelta(seconds=DIFF))
		cmdlist.append('echo "' + _("Time required for this process: %s") %TIMELAP + '\n"')

		self.session.open(Console, title=self.TITLE, cmdlist=cmdlist, closeOnSuccess=False)

	def imageInfo(self):
		AboutText = _("OpenHDF Full-Image Backupscript\n")
		AboutText += _("Support at") + " www.hdfreaks.cc\n\n"
		AboutText += _("[Image Info's]\n")
		AboutText += _("Model: %s %s\n") % (getMachineBrand(), getMachineName())
		AboutText += _("Backup Date: %s\n") % strftime("%Y-%m-%d", localtime(self.START))

		if path.exists('/proc/stb/info/chipset'):
			AboutText += _("Chipset: BCM%s") % about.getChipSetString().lower().replace('\n', '').replace('bcm', '') + "\n"

		AboutText += _("CPU: %s") % about.getCPUString() + "\n"
		AboutText += _("Cores: %s") % about.getCpuCoresString() + "\n"
		AboutText += _("Version: %s") % getImageVersion() + "\n"
		AboutText += _("HDF Build: %s") % getImageBuild() + "\n"
		AboutText += _("Kernel: %s") % about.getKernelVersionString() + "\n"

		string = getDriverDate()
		year = string[0:4]
		month = string[4:6]
		day = string[6:8]
		driversdate = '-'.join((year, month, day))

		AboutText += _("Drivers:\t%s") % driversdate + "\n"
		AboutText += _("Last update:\t%s") % getEnigmaVersionString() + "\n\n"
		AboutText += _("[Enigma2 Settings]\n")
		if sys.version_info[0] >= 3:
			AboutText += subprocess.getoutput("cat /etc/enigma2/settings")
		else:
			AboutText += commands.getoutput("cat /etc/enigma2/settings")
		AboutText += _("\n[Installed Plugins]\n")
		if sys.version_info[0] >= 3:
			AboutText += subprocess.getoutput("opkg list_installed | grep enigma2-plugin-")
		else:
			AboutText += commands.getoutput("opkg list_installed | grep enigma2-plugin-")

		return AboutText
