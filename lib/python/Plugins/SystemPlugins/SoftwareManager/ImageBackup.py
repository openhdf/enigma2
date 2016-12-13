#################################################################################
#       FULL BACKUP UYILITY FOR ENIGMA2, SUPPORTS THE MODELS OE-A 3.2     		#
#	                         						                            #
#					MAKES A FULLBACKUP READY FOR FLASHING.						#
#																				#
#################################################################################
import os
from enigma import getEnigmaVersionString
from Screens.Screen import Screen
from Components.Sources.StaticText import StaticText
from Components.Button import Button
from Components.SystemInfo import SystemInfo
from Components.Label import Label
from Components.ActionMap import ActionMap
from Components.About import about
from Components import Harddisk
from Screens.Console import Console
from Screens.MessageBox import MessageBox
from time import time, strftime, localtime
from os import path, system, makedirs, listdir, walk, statvfs, remove
import commands
import datetime
from boxbranding import getBoxType, getMachineBrand, getMachineName, getDriverDate, getImageVersion, getImageBuild, getBrandOEM, getMachineBuild, getImageFolder, getMachineUBINIZE, getMachineMKUBIFS, getMachineMtdKernel, getMachineMtdRoot, getMachineKernelFile, getMachineRootFile, getImageFileSystem

VERSION = "Version 5.5 borrowed from openATV"
HaveGZkernel = True
if getMachineBuild() in ("vusolo4k", "spark", "spark7162", "hd51", "hd52", "sf4008"):
	HaveGZkernel = False

isDreamboxXZ = False
if getBoxType() in "dm7080" "dm820" "dm520" "dm525" "dm900":
	isDreamboxXZ = True
	HaveGZkernel = False

def Freespace(dev):
	statdev = statvfs(dev)
	space = (statdev.f_bavail * statdev.f_frsize) / 1024
	print "[FULL BACKUP] Free space on %s = %i kilobytes" %(dev, space)
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

	def __init__(self, session, args = 0):
		Screen.__init__(self, session)
		self.session = session
		self.selection = 0
		self.list = self.list_files("/boot")
		self.MODEL = getBoxType()
		self.OEM = getBrandOEM()
		self.MACHINEBUILD = getMachineBuild()
		self.MACHINENAME = getMachineName()
		self.MACHINEBRAND = getMachineBrand()
		self.IMAGEFOLDER = getImageFolder()
		self.HDFIMAGEVERSION = getImageVersion()
		self.HDFIMAGEBUILD = getImageBuild()
		self.UBINIZE_ARGS = getMachineUBINIZE()
		self.MKUBIFS_ARGS = getMachineMKUBIFS()
		self.MTDKERNEL = getMachineMtdKernel()
		self.MTDROOTFS = getMachineMtdRoot()
		self.ROOTFSBIN = getMachineRootFile()
		self.KERNELBIN = getMachineKernelFile()
		self.ROOTFSTYPE = getImageFileSystem()
		print "[FULL BACKUP] BOX MACHINEBUILD = >%s<" %self.MACHINEBUILD
		print "[FULL BACKUP] BOX MACHINENAME = >%s<" %self.MACHINENAME
		print "[FULL BACKUP] BOX MACHINEBRAND = >%s<" %self.MACHINEBRAND
		print "[FULL BACKUP] BOX MODEL = >%s<" %self.MODEL
		print "[FULL BACKUP] OEM MODEL = >%s<" %self.OEM
		print "[FULL BACKUP] IMAGEFOLDER = >%s<" %self.IMAGEFOLDER
		print "[FULL BACKUP] UBINIZE = >%s<" %self.UBINIZE_ARGS
		print "[FULL BACKUP] MKUBIFS = >%s<" %self.MKUBIFS_ARGS
		print "[FULL BACKUP] MTDKERNEL = >%s<" %self.MTDKERNEL
		print "[FULL BACKUP] MTDROOTFS = >%s<" %self.MTDROOTFS
		print "[FULL BACKUP] ROOTFSTYPE = >%s<" %self.ROOTFSTYPE
		if isDreamboxXZ:
			self.IMAGEFOLDER = self.MODEL
# fix me to xz
			self.ROOTFSTYPE = "tar.gz"
			self.ROOTFSBIN = "root.tar.gz"

		self["key_green"] = Button("USB")
		self["key_red"] = Button("HDD")
		self["key_blue"] = Button(_("Exit"))
		if SystemInfo["HaveMultiBoot"]:
			self["key_yellow"] = Button(_("STARTUP"))
			self["info-multi"] = Label(_("You can select with yellow the OnlineFlash Image\n or select Recovery to create a USB Disk Image for clean Install."))
		else:
			self["key_yellow"] = Button("")
			self["info-multi"] = Label(" ")
		self["info-usb"] = Label(_("USB = Do you want to make a back-up on USB?\nThis will take between 4 and 15 minutes depending on the used filesystem and is fully automatic.\nMake sure you first insert an USB flash drive before you select USB."))
		self["info-hdd"] = Label(_("HDD = Do you want to make an USB-back-up image on HDD? \nThis only takes 2 or 10 minutes and is fully automatic."))
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
		{
			"blue": self.quit,
			"yellow": self.yellow,
			"green": self.green,
			"red": self.red,
			"cancel": self.quit,
		}, -2)

	def check_hdd(self):
		if not path.exists("/media/hdd"):
			self.session.open(MessageBox, _("No /hdd found !!\nPlease make sure you have a HDD mounted.\n"), type = MessageBox.TYPE_ERROR)
			return False
		if Freespace('/media/hdd') < 300000:
			self.session.open(MessageBox, _("Not enough free space on /hdd !!\nYou need at least 300Mb free space.\n"), type = MessageBox.TYPE_ERROR)
			return False
		return True

	def check_usb(self, dev):
		if Freespace(dev) < 300000:
			self.session.open(MessageBox, _("Not enough free space on %s !!\nYou need at least 300Mb free space.\n" % dev), type = MessageBox.TYPE_ERROR)
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
			text = _("No USB-Device found for fullbackup !!\n\n\n")
			text += _("To back-up directly to the USB-stick, the USB-stick MUST\n")
			text += _("contain a file with the name: \n\n")
			text += _("backupstick or backupstick.txt")
			self.session.open(MessageBox, text, type = MessageBox.TYPE_ERROR)
		else:
			if self.check_usb(USB_DEVICE):
				self.doFullBackup(USB_DEVICE)

	def yellow(self):
		if SystemInfo["HaveMultiBoot"]:
			self.selection = self.selection + 1
			if self.selection == len(self.list):
				self.selection = 0
			self["key_yellow"].setText(_(self.list[self.selection]))
			if self.list[self.selection] == "Recovery":
				cmdline = self.read_startup("/boot/STARTUP").split("=",1)[1].split(" ",1)[0]
			else:
				cmdline = self.read_startup("/boot/" + self.list[self.selection]).split("=",1)[1].split(" ",1)[0]
			cmdline = cmdline.lstrip("/dev/")
			self.MTDROOTFS = cmdline
			self.MTDKERNEL = cmdline[:-1] + str(int(cmdline[-1:]) -1)
			print "[FULL BACKUP] Multiboot rootfs ", self.MTDROOTFS
			print "[FULL BACKUP] Multiboot kernel ", self.MTDKERNEL

	def read_startup(self, FILE):
		self.file = FILE
		with open(self.file, 'r') as myfile:
			data=myfile.read().replace('\n', '')
		myfile.close()
		return data

	def list_files(self, PATH):
		files = []
		if SystemInfo["HaveMultiBoot"]:
			self.path = PATH
			for name in listdir(self.path):
				if path.isfile(path.join(self.path, name)):
					cmdline = self.read_startup("/boot/" + name).split("=",1)[1].split(" ",1)[0]
					if cmdline in Harddisk.getextdevices("ext4"):
						files.append(name)
			files.append("Recovery")
		return files

	def SearchUSBcanidate(self):
		for paths, subdirs, files in walk("/media"):
			for dir in subdirs:
				if not dir == 'hdd' and not dir == 'net':
					for file in listdir("/media/" + dir):
						if file.find("backupstick") > -1:
							print "USB-DEVICE found on: /media/%s" % dir
							return "/media/" + dir
			break
		return "XX"

	def doFullBackup(self, DIRECTORY):
		self.DIRECTORY = DIRECTORY
		self.TITLE = _("Full back-up on %s") % (self.DIRECTORY)
		self.START = time()
		self.DATE = strftime("%Y%m%d_%H%M", localtime(self.START))
		self.IMAGEVERSION = self.imageInfo() #strftime("%Y%m%d", localtime(self.START))
		if "ubi" in self.ROOTFSTYPE.split():
			self.MKFS = "/usr/sbin/mkfs.ubifs"
		elif "tar.bz2" in self.ROOTFSTYPE.split() or SystemInfo["HaveMultiBoot"]:
			self.MKFS = "/bin/tar"
			self.BZIP2 = "/usr/bin/bzip2"
		else:
			self.MKFS = "/usr/sbin/mkfs.jffs2"
		self.UBINIZE = "/usr/sbin/ubinize"
		self.NANDDUMP = "/usr/sbin/nanddump"
		self.WORKDIR= "%s/bi" %self.DIRECTORY
		self.TARGET="XX"
		if isDreamboxXZ:
			self.XZ = "/usr/bin/xz"
			self.MKFS = "/bin/tar"

		## TESTING IF ALL THE TOOLS FOR THE BUILDING PROCESS ARE PRESENT
		if isDreamboxXZ:
			if not path.exists(self.XZ):
				text = "%s not found !!" %self.XZ
				self.session.open(MessageBox, _(text), type = MessageBox.TYPE_ERROR)
				return
		else:
			if not path.exists(self.MKFS):
				text = "%s not found !!" %self.MKFS
				self.session.open(MessageBox, _(text), type = MessageBox.TYPE_ERROR)
				return
			if not path.exists(self.NANDDUMP):
				text = "%s not found !!" %self.NANDDUMP
				self.session.open(MessageBox, _(text), type = MessageBox.TYPE_ERROR)
				return

		self.SHOWNAME = "%s %s" %(self.MACHINEBRAND, self.MODEL)
		self.MAINDESTOLD = "%s/%s" %(self.DIRECTORY, self.MODEL)
		self.MAINDEST = "%s/%s" %(self.DIRECTORY,self.IMAGEFOLDER)
		self.EXTRA = "%s/fullbackup_%s_%s/%s_build_%s" % (self.DIRECTORY, self.IMAGEFOLDER, self.HDFIMAGEVERSION, self.DATE, self.HDFIMAGEBUILD)
		self.EXTRAOLD = "%s/fullbackup_%s/%s/%s" % (self.DIRECTORY, self.MODEL, self.DATE, self.MODEL)
		self.message = "echo -e '\n"
		self.message += (_("Back-up Tool for a %s\n" %self.SHOWNAME)).upper()
		self.message += VERSION + '\n'
		self.message += "_________________________________________________\n\n"
		self.message += _("Please be patient, a backup will now be made,\n")
		if self.ROOTFSTYPE == "ubi":
			self.message += _("because of the used filesystem the back-up\n")
			self.message += _("will take about 3-12 minutes for this system\n")
		elif isDreamboxXZ:
			self.message += _("because of the used filesystem the back-up\n")
			self.message += _("will take about 3-12 minutes for this system\n")
		elif SystemInfo["HaveMultiBoot"] and self.list[self.selection] == "Recovery":
			self.message += _("because of the used filesystem the back-up\n")
			self.message += _("will take about 30 minutes for this system\n")
		elif "tar.bz2" in self.ROOTFSTYPE.split() or SystemInfo["HaveMultiBoot"]:
			self.message += _("because of the used filesystem the back-up\n")
			self.message += _("will take about 1-4 minutes for this system\n")
		else:
			self.message += _("this will take between 2 and 9 minutes\n")
		self.message += "\n_________________________________________________\n\n"
		self.message += "'"

		## PREPARING THE BUILDING ENVIRONMENT
		system("rm -rf %s" %self.WORKDIR)
		if not path.exists(self.WORKDIR):
			makedirs(self.WORKDIR)
		if not path.exists("/tmp/bi/root"):
			makedirs("/tmp/bi/root")
		system("sync")
		if SystemInfo["HaveMultiBoot"]:
			system("mount /dev/%s /tmp/bi/root" %self.MTDROOTFS)
		else:
			system("mount --bind / /tmp/bi/root")
		if isDreamboxXZ:
			cmd1 = "(cd /tmp/bi/root && find . -type s) >/tmp/sockets"
#			cmd1 = "%s -cJf %s/root.tar.xz -C /tmp/bi/root ." % (self.MKFS, self.WORKDIR)
			cmd2 = "%s -C /tmp/bi/root -z --exclude-from=/tmp/sockets -cf %s/root.tar.gz ." % (self.MKFS, self.WORKDIR)
			cmd3 = None
		elif "jffs2" in self.ROOTFSTYPE.split():
			cmd1 = "%s --root=/tmp/bi/root --faketime --output=%s/root.jffs2 %s" % (self.MKFS, self.WORKDIR, self.MKUBIFS_ARGS)
			cmd2 = None
			cmd3 = None
		elif "tar.bz2" in self.ROOTFSTYPE.split() or SystemInfo["HaveMultiBoot"]:
			cmd1 = "%s -cf %s/rootfs.tar -C /tmp/bi/root --exclude=/var/nmbd/* ." % (self.MKFS, self.WORKDIR)
			cmd2 = "%s %s/rootfs.tar" % (self.BZIP2, self.WORKDIR)
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
			cmd1 = "%s -r /tmp/bi/root -o %s/root.ubi %s" % (self.MKFS, self.WORKDIR, self.MKUBIFS_ARGS)
			cmd2 = "%s -o %s/root.ubifs %s %s/ubinize.cfg" % (self.UBINIZE, self.WORKDIR, self.UBINIZE_ARGS, self.WORKDIR)
			cmd3 = "mv %s/root.ubifs %s/root.%s" %(self.WORKDIR, self.WORKDIR, self.ROOTFSTYPE)

		cmdlist = []
		cmdlist.append(self.message)
		cmdlist.append('echo "Create: %s\n"' %self.ROOTFSBIN)
		cmdlist.append(cmd1)
		if cmd2:
			cmdlist.append(cmd2)
		if cmd3:
			cmdlist.append(cmd3)
		cmdlist.append("chmod 644 %s/%s" %(self.WORKDIR, self.ROOTFSBIN))
		cmdlist.append('echo " "')
		if isDreamboxXZ:
			self.session.open(Console, title = self.TITLE, cmdlist = cmdlist, finishedCallback = self.doFullBackupCB, closeOnSuccess = True)
		else:
			cmdlist.append('echo "Create: kerneldump"')
 			cmdlist.append('echo " "')
			if SystemInfo["HaveMultiBoot"]:
				cmdlist.append("dd if=/dev/%s of=%s/kernel.bin" % (self.MTDKERNEL ,self.WORKDIR))
			elif self.MTDKERNEL == "mmcblk0p1" or self.MTDKERNEL == "mmcblk0p3":
				cmdlist.append("dd if=/dev/%s of=%s/%s" % (self.MTDKERNEL ,self.WORKDIR, self.KERNELBIN))

			else:
				cmdlist.append("nanddump -a -f %s/vmlinux.gz /dev/%s" % (self.WORKDIR, self.MTDKERNEL))
			cmdlist.append('echo " "')

			if HaveGZkernel:
				cmdlist.append('echo "Check: kerneldump"')
			cmdlist.append("sync")

			if SystemInfo["HaveMultiBoot"] and self.list[self.selection] == "Recovery":
				GPT_OFFSET=0
				GPT_SIZE=1024
				BOOT_PARTITION_OFFSET = int(GPT_OFFSET) + int(GPT_SIZE)
				BOOT_PARTITION_SIZE=3072
				KERNEL_PARTITION_OFFSET = int(BOOT_PARTITION_OFFSET) + int(BOOT_PARTITION_SIZE)
				KERNEL_PARTITION_SIZE=8192
				ROOTFS_PARTITION_OFFSET = int(KERNEL_PARTITION_OFFSET) + int(KERNEL_PARTITION_SIZE)
				ROOTFS_PARTITION_SIZE=1048576
				SECOND_KERNEL_PARTITION_OFFSET = int(ROOTFS_PARTITION_OFFSET) + int(ROOTFS_PARTITION_SIZE)
				SECOND_ROOTFS_PARTITION_OFFSET = int(SECOND_KERNEL_PARTITION_OFFSET) + int(KERNEL_PARTITION_SIZE)
				THRID_KERNEL_PARTITION_OFFSET = int(SECOND_ROOTFS_PARTITION_OFFSET) + int(ROOTFS_PARTITION_SIZE)
				THRID_ROOTFS_PARTITION_OFFSET = int(THRID_KERNEL_PARTITION_OFFSET) + int(KERNEL_PARTITION_SIZE)
				FOURTH_KERNEL_PARTITION_OFFSET = int(THRID_ROOTFS_PARTITION_OFFSET) + int(ROOTFS_PARTITION_SIZE)
				FOURTH_ROOTFS_PARTITION_OFFSET = int(FOURTH_KERNEL_PARTITION_OFFSET) + int(KERNEL_PARTITION_SIZE)
				EMMC_IMAGE = "%s/disk.img"%self.WORKDIR
				EMMC_IMAGE_SIZE=3817472
				IMAGE_ROOTFS_SIZE=196608
				cmdlist.append('echo " "')
				cmdlist.append('echo "Create: Recovery Fullbackup disk.img"')
				cmdlist.append('echo " "')
				cmdlist.append('dd if=/dev/zero of=%s bs=1024 count=0 seek=%s' % (EMMC_IMAGE, EMMC_IMAGE_SIZE))
				cmdlist.append('parted -s %s mklabel gpt' %EMMC_IMAGE)
				PARTED_END_BOOT = int(BOOT_PARTITION_OFFSET) + int(BOOT_PARTITION_SIZE)
				cmdlist.append('parted -s %s unit KiB mkpart boot fat16 %s %s' % (EMMC_IMAGE, BOOT_PARTITION_OFFSET, PARTED_END_BOOT ))
				PARTED_END_KERNEL1 = int(KERNEL_PARTITION_OFFSET) + int(KERNEL_PARTITION_SIZE)
				cmdlist.append('parted -s %s unit KiB mkpart kernel1 %s %s' % (EMMC_IMAGE, KERNEL_PARTITION_OFFSET, PARTED_END_KERNEL1 ))
				PARTED_END_ROOTFS1 = int(ROOTFS_PARTITION_OFFSET) + int(ROOTFS_PARTITION_SIZE)
				cmdlist.append('parted -s %s unit KiB mkpart rootfs1 ext2 %s %s' % (EMMC_IMAGE, ROOTFS_PARTITION_OFFSET, PARTED_END_ROOTFS1 ))
				PARTED_END_KERNEL2 = int(SECOND_KERNEL_PARTITION_OFFSET) + int(KERNEL_PARTITION_SIZE)
				cmdlist.append('parted -s %s unit KiB mkpart kernel2 %s %s' % (EMMC_IMAGE, SECOND_KERNEL_PARTITION_OFFSET, PARTED_END_KERNEL2 ))
				PARTED_END_ROOTFS2 = int(SECOND_ROOTFS_PARTITION_OFFSET) + int(ROOTFS_PARTITION_SIZE)
				cmdlist.append('parted -s %s unit KiB mkpart rootfs2 ext2 %s %s' % (EMMC_IMAGE, SECOND_ROOTFS_PARTITION_OFFSET, PARTED_END_ROOTFS2 ))
				PARTED_END_KERNEL3 = int(THRID_KERNEL_PARTITION_OFFSET) + int(KERNEL_PARTITION_SIZE)
				cmdlist.append('parted -s %s unit KiB mkpart kernel3 %s %s' % (EMMC_IMAGE, THRID_KERNEL_PARTITION_OFFSET, PARTED_END_KERNEL3 ))
				PARTED_END_ROOTFS3 = int(THRID_ROOTFS_PARTITION_OFFSET) + int(ROOTFS_PARTITION_SIZE)
				cmdlist.append('parted -s %s unit KiB mkpart rootfs3 ext2 %s %s' % (EMMC_IMAGE, THRID_ROOTFS_PARTITION_OFFSET, PARTED_END_ROOTFS3 ))
				PARTED_END_KERNEL4 = int(FOURTH_KERNEL_PARTITION_OFFSET) + int(KERNEL_PARTITION_SIZE)
				cmdlist.append('parted -s %s unit KiB mkpart kernel4 %s %s' % (EMMC_IMAGE, FOURTH_KERNEL_PARTITION_OFFSET, PARTED_END_KERNEL4 ))
				PARTED_END_ROOTFS4 = int(EMMC_IMAGE_SIZE) - 1024
				cmdlist.append('parted -s %s unit KiB mkpart rootfs4 ext2 %s %s' % (EMMC_IMAGE, FOURTH_ROOTFS_PARTITION_OFFSET, PARTED_END_ROOTFS4 ))
				cmdlist.append('dd if=/dev/zero of=%s/boot.img bs=1024 count=%s' % (self.WORKDIR, BOOT_PARTITION_SIZE ))
				cmdlist.append('mkfs.msdos -S 512 %s/boot.img' %self.WORKDIR)
				cmdlist.append("echo \"boot emmcflash0.kernel1 \'root=/dev/mmcblk0p3 rw rootwait hd51_4.boxmode=1\'\" > %s/STARTUP" %self.WORKDIR)
				cmdlist.append("echo \"boot emmcflash0.kernel1 \'root=/dev/mmcblk0p3 rw rootwait hd51_4.boxmode=1\'\" > %s/STARTUP_1" %self.WORKDIR)
				cmdlist.append("echo \"boot emmcflash0.kernel2 \'root=/dev/mmcblk0p5 rw rootwait hd51_4.boxmode=1\'\" > %s/STARTUP_2" %self.WORKDIR)
				cmdlist.append("echo \"boot emmcflash0.kernel3 \'root=/dev/mmcblk0p7 rw rootwait hd51_4.boxmode=1\'\" > %s/STARTUP_3" %self.WORKDIR)
				cmdlist.append("echo \"boot emmcflash0.kernel4 \'root=/dev/mmcblk0p9 rw rootwait hd51_4.boxmode=1\'\" > %s/STARTUP_4" %self.WORKDIR)
				cmdlist.append('mcopy -i %s/boot.img -v %s/STARTUP ::' % (self.WORKDIR, self.WORKDIR))
				cmdlist.append('mcopy -i %s/boot.img -v %s/STARTUP_1 ::' % (self.WORKDIR, self.WORKDIR))
				cmdlist.append('mcopy -i %s/boot.img -v %s/STARTUP_2 ::' % (self.WORKDIR, self.WORKDIR))
				cmdlist.append('mcopy -i %s/boot.img -v %s/STARTUP_3 ::' % (self.WORKDIR, self.WORKDIR))
				cmdlist.append('mcopy -i %s/boot.img -v %s/STARTUP_4 ::' % (self.WORKDIR, self.WORKDIR))
				cmdlist.append('dd conv=notrunc if=%s/boot.img of=%s bs=1024 seek=%s' % (self.WORKDIR, EMMC_IMAGE, BOOT_PARTITION_OFFSET ))
				cmdlist.append('dd conv=notrunc if=/dev/%s of=%s bs=1024 seek=%s' % (self.MTDKERNEL, EMMC_IMAGE, KERNEL_PARTITION_OFFSET ))
				cmdlist.append('dd if=/dev/%s of=%s bs=1024 seek=%s' % (self.MTDROOTFS, EMMC_IMAGE, ROOTFS_PARTITION_OFFSET ))
			self.session.open(Console, title = self.TITLE, cmdlist = cmdlist, finishedCallback = self.doFullBackupCB, closeOnSuccess = True)

	def doFullBackupCB(self):
		if HaveGZkernel:
			ret = commands.getoutput(' gzip -d %s/vmlinux.gz -c > /tmp/vmlinux.bin' % self.WORKDIR)
			if ret:
				text = "Kernel dump error\n"
				text += "Please Flash your Kernel new and Backup again"
				system('rm -rf /tmp/vmlinux.bin')
				self.session.open(MessageBox, _(text), type = MessageBox.TYPE_ERROR)
				return

		cmdlist = []
		cmdlist.append(self.message)
		if HaveGZkernel:
			cmdlist.append('echo "Kernel dump OK"')
			cmdlist.append("rm -rf /tmp/vmlinux.bin")
		cmdlist.append('echo "_________________________________________________"')
		cmdlist.append('echo "Almost there... "')
		cmdlist.append('echo "Now building the USB-Image"')
		cmdlist.append('echo "Lets bring up some verbosity"')
		cmdlist.append('echo "ROOTFSBIN: %s WORKDIR:%s MAINDEST:%s DIRECTORY:%s IMAGEFOLDER:%s"' % (self.ROOTFSBIN, self.WORKDIR, self.MAINDEST, self.DIRECTORY, self.IMAGEFOLDER))

		system('rm -rf %s' %self.MAINDEST)
		if not path.exists(self.MAINDEST):
			makedirs(self.MAINDEST)
		if not path.exists(self.EXTRA):
			makedirs(self.EXTRA)

		f = open("%s/imageversion" %self.MAINDEST, "w")
		f.write(self.IMAGEVERSION)
		f.close()

		if self.ROOTFSBIN == "rootfs.tar.bz2":
			system('mv %s/rootfs.tar.bz2 %s/rootfs.tar.bz2' %(self.WORKDIR, self.MAINDEST))
		else:
			system('mv %s/root.%s %s/%s' %(self.WORKDIR, self.ROOTFSTYPE, self.MAINDEST, self.ROOTFSBIN))
		if SystemInfo["HaveMultiBoot"]:
			system('mv %s/kernel.bin %s/kernel.bin' %(self.WORKDIR, self.MAINDEST))
		elif self.MTDKERNEL == "mmcblk0p1" or self.MTDKERNEL == "mmcblk0p3":
			system('mv %s/%s %s/%s' %(self.WORKDIR, self.KERNELBIN, self.MAINDEST, self.KERNELBIN))
		else:
			if not isDreamboxXZ:
				system('mv %s/vmlinux.gz %s/%s' %(self.WORKDIR, self.MAINDEST, self.KERNELBIN))

		if SystemInfo["HaveMultiBoot"] and self.list[self.selection] == "Recovery":
			system('mv %s/disk.img %s/disk.img' %(self.WORKDIR, self.MAINDEST))
		elif self.MODEL in ("vusolo4k", "vuduo2", "vusolo2", "vusolo", "vuduo", "vuultimo", "vuuno"):
			cmdlist.append('echo "This file forces a reboot after the update." > %s/reboot.update' %self.MAINDEST)
		elif self.MODEL in ("vuzero" , "vusolose"):
			cmdlist.append('echo "This file forces the update." > %s/force.update' %self.MAINDEST)
		elif self.MODEL in ("novaip" , "zgemmai55" , "sf98", "xpeedlxpro"):
			cmdlist.append('echo "This file forces the update." > %s/force' %self.MAINDEST)
		else:
			if not isDreamboxXZ:
				cmdlist.append('echo "rename this file to "force" to force an update without confirmation" > %s/noforce' %self.MAINDEST)

		if self.MODEL in ("gbquad", "gbquadplus", "gb800ue", "gb800ueplus", "gbultraue", "twinboxlcd", "twinboxlcdci", "singleboxlcd", "sf208", "sf228"):
			lcdwaitkey = '/usr/share/lcdwaitkey.bin'
			lcdwarning = '/usr/share/lcdwarning.bin'
			if path.exists(lcdwaitkey):
				system('cp %s %s/lcdwaitkey.bin' %(lcdwaitkey, self.MAINDEST))
			if path.exists(lcdwarning):
				system('cp %s %s/lcdwarning.bin' %(lcdwarning, self.MAINDEST))
		if self.MODEL == "gb800solo":
			burnbat = "%s/fullbackup_%s/%s" % (self.DIRECTORY, self.TYPE, self.DATE)
			f = open("%s/burn.bat" % (burnbat), "w")
			f.write("flash -noheader usbdisk0:gigablue/solo/kernel.bin flash0.kernel\n")
			f.write("flash -noheader usbdisk0:gigablue/solo/rootfs.bin flash0.rootfs\n")
			f.write('setenv -p STARTUP "boot -z -elf flash0.kernel: ')
			f.write("'rootfstype=jffs2 bmem=106M@150M root=/dev/mtdblock6 rw '")
			f.write('"\n')
			f.close()

		cmdlist.append('cp -r %s/* %s/' % (self.MAINDEST, self.EXTRA))

		cmdlist.append("sync")
		file_found = True

		if not path.exists("%s/%s" % (self.MAINDEST, self.ROOTFSBIN)):
			print "%s/%s not found" % (self.MAINDEST, self.ROOTFSBIN)
			print 'ROOTFS bin file not found'
			file_found = False

		if not isDreamboxXZ:
			if not path.exists("%s/%s" % (self.MAINDEST, self.KERNELBIN)):
				print 'KERNEL bin file not found'
				file_found = False

			if path.exists("%s/noforce" % self.MAINDEST):
				print 'NOFORCE bin file not found'
				file_found = False

		if SystemInfo["HaveMultiBoot"] and not self.list[self.selection] == "Recovery":
			cmdlist.append('echo "_________________________________________________________\n"')
			cmdlist.append('echo "Multiboot Image created on:" %s' %self.MAINDEST)
			cmdlist.append('echo "and there is made an extra copy on:"')
			cmdlist.append('echo %s' %self.EXTRA)
			cmdlist.append('echo "_________________________________________________________\n"')
			cmdlist.append('echo "\nPlease wait...almost ready! "')
			cmdlist.append('echo " "')
			cmdlist.append('echo "To restore the image: check the manual of the receiver"')
		elif file_found:
			cmdlist.append('echo "_________________________________________________________\n"')
			cmdlist.append('echo "USB Image created on:" %s' %self.MAINDEST)
			cmdlist.append('echo "and there is made an extra copy on:"')
			cmdlist.append('echo %s' %self.EXTRA)
			cmdlist.append('echo "_________________________________________________________\n"')
			cmdlist.append('echo "\nPlease wait...almost ready! "')
			cmdlist.append('echo " "')
			cmdlist.append('echo "To restore the image: check the manual of the receiver"')
		else:
			cmdlist.append('echo "_________________________________________________________\n"')
			cmdlist.append('echo "Image creation failed - "')
			cmdlist.append('echo "Probable causes could be"')
			cmdlist.append('echo "     wrong back-up destination "')
			cmdlist.append('echo "     no space left on back-up device"')
			cmdlist.append('echo "     no writing permission on back-up device"')
			cmdlist.append('echo " "')

		if self.DIRECTORY == "/hdd":
			self.TARGET = self.SearchUSBcanidate()
			print "TARGET = %s" % self.TARGET
			if self.TARGET == 'XX':
				cmdlist.append('echo " "')
			else:
				cmdlist.append('echo "_________________________________________________\n"')
				cmdlist.append('echo " "')
				cmdlist.append('echo "There is a valid USB-flash drive detected in one "')
				cmdlist.append('echo "of the USB-ports, therefor an extra copy of the "')
				cmdlist.append('echo "back-up image will now be copied to that USB- "')
				cmdlist.append('echo "flash drive. "')
				cmdlist.append('echo "This only takes about 1 or 2 minutes"')
				cmdlist.append('echo " "')

				cmdlist.append('mkdir -p %s/%s' % (self.TARGET, self.IMAGEFOLDER))
				cmdlist.append('cp -r %s %s/' % (self.MAINDEST, self.TARGET))


				cmdlist.append("sync")
				cmdlist.append('echo "Backup finished and copied to your USB-flash drive"')

		cmdlist.append("umount /tmp/bi/root")
		cmdlist.append("rmdir /tmp/bi/root")
		cmdlist.append("rmdir /tmp/bi")
		cmdlist.append("rm -rf %s" % self.WORKDIR)
		cmdlist.append("sleep 5")
		END = time()
		DIFF = int(END - self.START)
		TIMELAP = str(datetime.timedelta(seconds=DIFF))
		cmdlist.append('echo " Time required for this process: %s"' %TIMELAP)

		self.session.open(Console, title = self.TITLE, cmdlist = cmdlist, closeOnSuccess = False)

	def imageInfo(self):
		AboutText = _("OpenHDF Full-Image Backupscript\n")
		AboutText += _("Support at") + " www.hdfreaks.cc\n\n"
		AboutText += _("[Image Info's]\n")
		AboutText += _("Model: %s %s\n") % (getMachineBrand(), getMachineName())
		AboutText += _("Backup Date: %s\n") % strftime("%Y-%m-%d", localtime(self.START))

		if path.exists('/proc/stb/info/chipset'):
			AboutText += _("Chipset: BCM%s") % about.getChipSetString().lower().replace('\n','').replace('bcm','') + "\n"

		#AboutText += _("CPU: %s") % about.getCPUString() + "\n"
		AboutText += _("Cores: %s") % about.getCpuCoresString() + "\n"
		AboutText += _("Version: %s") % getImageVersion() + "\n"
		AboutText += _("Build: %s") % getImageBuild() + "\n"
		AboutText += _("Kernel: %s") % about.getKernelVersionString() + "\n"

		string = getDriverDate()
		year = string[0:4]
		month = string[4:6]
		day = string[6:8]
		driversdate = '-'.join((year, month, day))

		AboutText += _("Drivers:\t%s") % driversdate + "\n"
		AboutText += _("Last update:\t%s") % getEnigmaVersionString() + "\n\n"
		AboutText += _("[Enigma2 Settings]\n")
		AboutText += commands.getoutput("cat /etc/enigma2/settings")
		AboutText += _("\n[Installed Plugins]\n")
		AboutText += commands.getoutput("opkg list_installed | grep enigma2-plugin-")

		return AboutText
