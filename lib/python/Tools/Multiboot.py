from Components.SystemInfo import BoxInfo
from Components.Console import Console
from Tools.Directories import fileHas, fileExists
import os
import glob
import tempfile
import subprocess

class tmp:
	dir = None


def getMultibootStartupDevice():
	tmp.dir = tempfile.mkdtemp(prefix="Multiboot")
	if BoxInfo.getItem("hasKexec"): # kexec kernel multiboot
		bootList = ("/dev/mmcblk0p4", "/dev/mmcblk0p7", "/dev/mmcblk0p9")
	else: #legacy multiboot
		bootList = ("/dev/mmcblk0p1", "/dev/mmcblk1p1", "/dev/mmcblk0p3", "/dev/mmcblk0p4", "/dev/mtdblock2", "/dev/block/by-name/bootoptions")
	for device in bootList:
		if os.path.exists(device):
			if os.path.exists("/dev/block/by-name/flag"):
				Console().ePopen('mount --bind %s %s' % (device, tmp.dir))
			else:
				Console().ePopen('mount %s %s' % (device, tmp.dir))
			if os.path.isfile(os.path.join(tmp.dir, "STARTUP")):
				print('[Multiboot] Startupdevice found:', device)
				return device
			Console().ePopen('umount %s' % tmp.dir)
	if not os.path.ismount(tmp.dir):
		os.rmdir(tmp.dir)


def getparam(line, param):
	return line.replace("userdataroot", "rootuserdata").rsplit('%s=' % param, 1)[1].split(' ', 1)[0]

def getMultibootslots():
	bootslots = {}
	mode12found = False
	if BoxInfo.getItem("MultibootStartupDevice"):
		for _file in glob.glob(os.path.join(tmp.dir, 'STARTUP_*')):
			if "STARTUP_RECOVERY" in _file:
				BoxInfo.setItem("RecoveryMode", True)
				print("[multiboot] [getMultibootslots] RecoveryMode is set to:%s" % BoxInfo.getItem("RecoveryMode"))
			if 'MODE_' in _file:
				mode12found = True
				slotnumber = _file.rsplit('_', 3)[1]
			else:
				slotnumber = _file.rsplit('_', 1)[1]
			if slotnumber.isdigit() and slotnumber not in bootslots:
				slot = {}
				for line in open(_file).readlines():
					if 'root=' in line:
						device = getparam(line, 'root')
						if "UUID=" in device:
							slotx = str(getUUIDtoSD(device))
							if slotx is not None:
								device = slotx
						if os.path.exists(device) or device == 'ubi0:ubifs':
							slot['device'] = device
							slot['startupfile'] = os.path.basename(_file)
							if "sda" in line:
								slot["kernel"] = "/dev/sda%s" % line.split("sda", 1)[1].split(" ", 1)[0]
								slot["rootsubdir"] = None
							else:
								slot["kernel"] = "%sp%s" % (device.split("p")[0], int(device.split("p")[1]) - 1)
							if 'rootsubdir' in line:
								BoxInfo.setItem("HasRootSubdir", True)
								slot['rootsubdir'] = getparam(line, 'rootsubdir')
								slot["kernel"] = getparam(line, "kernel")
						break
				if slot:
					bootslots[int(slotnumber)] = slot
		Console().ePopen('umount %s' % tmp.dir)
		if not os.path.ismount(tmp.dir):
			os.rmdir(tmp.dir)
		if not mode12found and BoxInfo.getItem("canMode12"):
			#the boot device has ancient content and does not contain the correct STARTUP files
			for slot in range(1, 5):
				bootslots[slot] = {'device': '/dev/mmcblk0p%s' % (slot * 2 + 1), 'startupfile': None}
	print('[Multiboot] Bootslots found:', bootslots)
	return bootslots


def GetCurrentImage():
	if BoxInfo.getItem("canMultiBoot"):
		if BoxInfo.getItem("hasKexec"):	# kexec kernel multiboot
			rootsubdir = [x for x in open('/sys/firmware/devicetree/base/chosen/bootargs', 'r').read().split() if x.startswith("rootsubdir")]
			char = "/" if "/" in rootsubdir[0] else "="
			return int(rootsubdir[0].rsplit(char, 1)[1][11:])
		else: #legacy multiboot
			slot = [x[-1] for x in open('/sys/firmware/devicetree/base/chosen/bootargs', 'r').read().split() if x.startswith('rootsubdir')]
			if slot:
				return int(slot[0])
			else:
				device = getparam(open('/sys/firmware/devicetree/base/chosen/bootargs', 'r').read(), 'root')
				for slot in list(BoxInfo.getItem("canMultiBoot").keys()):
					if BoxInfo.getItem("canMultiBoot")[slot]['device'] == device:
						return slot


def GetCurrentImageMode():
	return bool(BoxInfo.getItem("canMultiBoot")) and BoxInfo.getItem("canMode12") and int(open('/sys/firmware/devicetree/base/chosen/bootargs', 'r').read().replace('\0', '').split('=')[-1])


def deleteImage(slot):
	tmp.dir = tempfile.mkdtemp(prefix="Multiboot")
	Console().ePopen('mount %s %s' % (BoxInfo.getItem("canMultiBoot")[slot]['device'], tmp.dir))
	enigma2binaryfile = os.path.join(os.sep.join(filter(None, [tmp.dir, BoxInfo.getItem("canMultiBoot")[slot].get('rootsubdir', '')])), 'usr/bin/enigma2')
	if os.path.exists(enigma2binaryfile):
		os.rename(enigma2binaryfile, '%s.bak' % enigma2binaryfile)
	Console().ePopen('umount %s' % tmp.dir)
	if not os.path.ismount(tmp.dir):
		os.rmdir(tmp.dir)


def restoreImages():
	for slot in BoxInfo.getItem("canMultiBoot"):
		tmp.dir = tempfile.mkdtemp(prefix="Multiboot")
		Console().ePopen('mount %s %s' % (BoxInfo.getItem("canMultiBoot")[slot]['device'], tmp.dir))
		enigma2binaryfile = os.path.join(os.sep.join(filter(None, [tmp.dir, BoxInfo.getItem("canMultiBoot")[slot].get('rootsubdir', '')])), 'usr/bin/enigma2')
		if os.path.exists('%s.bak' % enigma2binaryfile):
			os.rename('%s.bak' % enigma2binaryfile, enigma2binaryfile)
		Console().ePopen('umount %s' % tmp.dir)
		if not os.path.ismount(tmp.dir):
			os.rmdir(tmp.dir)

def getUUIDtoSD(UUID): # returns None on failure
	check = "/sbin/blkid"
	if fileExists(check):
		lines = subprocess.check_output([check]).decode(encoding="utf8", errors="ignore").split("\n")
		for line in lines:
			if UUID in line.replace('"', ''):
				return line.split(":")[0].strip()
	else:
		return None


def GetBoxName():
	box = getBoxType()
	machinename = getMachineName()
	if box in ('uniboxhd1', 'uniboxhd2', 'uniboxhd3'):
		box = "ventonhdx"
	elif box == 'odinm6':
		box = getMachineName().lower()
	elif box == "inihde" and machinename.lower() == "xpeedlx":
		box = "xpeedlx"
	elif box in ('xpeedlx1', 'xpeedlx2'):
		box = "xpeedlx"
	elif box == "inihde" and machinename.lower() == "hd-1000":
		box = "sezam-1000hd"
	elif box == "ventonhdx" and machinename.lower() == "hd-5000":
		box = "sezam-5000hd"
	elif box == "ventonhdx" and machinename.lower() == "premium twin":
		box = "miraclebox-twin"
	elif box == "xp1000" and machinename.lower() == "sf8 hd":
		box = "sf8"
	elif box.startswith('et') and not box in ('et8000', 'et8500', 'et8500s', 'et10000'):
		box = box[0:3] + 'x00'
	elif box == 'odinm9':
		box = 'maram9'
	elif box.startswith('sf8008m'):
		box = "sf8008m"
	elif box.startswith('sf8008'):
		box = "sf8008"
	elif box.startswith('twinboxlcdci'):
		box = "twinboxlcd"
	elif box == "sfx6018":
		box = "sfx6008"
	return box

def GetImagelist():
	imagelist = {}
	if BoxInfo.getItem("canMultiBoot"):
		tmp.dir = tempfile.mkdtemp(prefix="Multiboot")
		for slot in sorted(BoxInfo.getItem("canMultiBoot").keys()):
			if BoxInfo.getItem("canMultiBoot")[slot]['device'] == 'ubi0:ubifs':
				Console().ePopen('mount -t ubifs %s %s' % (BoxInfo.getItem("canMultiBoot")[slot]['device'], tmp.dir))
			else:
				Console().ePopen('mount %s %s' % (BoxInfo.getItem("canMultiBoot")[slot]['device'], tmp.dir))
			imagedir = os.sep.join(filter(None, [tmp.dir, BoxInfo.getItem("canMultiBoot")[slot].get('rootsubdir', '')]))
			if os.path.isfile(os.path.join(imagedir, 'usr/bin/enigma2')):
				try:
					from datetime import datetime
					date = datetime.fromtimestamp(os.stat(os.path.join(imagedir, "var/lib/opkg/status")).st_mtime).strftime('%Y-%m-%d')
					if date.startswith("1970"):
						date = datetime.fromtimestamp(os.stat(os.path.join(imagedir, "usr/share/bootlogo.mvi")).st_mtime).strftime('%Y-%m-%d')
					date = max(date, datetime.fromtimestamp(os.stat(os.path.join(imagedir, "usr/bin/enigma2")).st_mtime).strftime('%Y-%m-%d'))
				except:
					date = _("Unknown")
				imagelist[slot] = {'imagename': "%s (%s)" % (open(os.path.join(imagedir, "etc/issue")).readlines()[-2].capitalize().strip()[:-6], date)}
				if os.path.exists(os.path.join(imagedir, "etc/image-version")):
					with open(os.path.join(imagedir, "etc/image-version"), 'r') as fp:
						lines = fp.readlines()
						for row in lines:
							word = 'imagetype'
							if row.find(word) != -1:
								imagetype=row.split('=')[1]
								imagelist[slot] = {'imagename': "%s - %s (%s)" % (open(os.path.join(imagedir, "etc/issue")).readlines()[-2].capitalize().strip()[:-6], imagetype.strip(), date)}
								break
			elif os.path.isfile(os.path.join(imagedir, 'usr/bin/enigma2.bak')):
				imagelist[slot] = {'imagename': _("Deleted image")}
			else:
				imagelist[slot] = {'imagename': _("Empty slot")}
			Console().ePopen('umount %s' % tmp.dir)
		if not os.path.ismount(tmp.dir):
			os.rmdir(tmp.dir)
	return imagelist

class EmptySlot():
	MOUNT = 0
	UNMOUNT = 1

	def __init__(self, Contents, callback):
		if BoxInfo.getItem("canMultiBoot"):
			self.slots = sorted(list(BoxInfo.getItem("canMultiBoot").keys()))
			self.callback = callback
			self.imagelist = {}
			self.slot = Contents
			if not os_path.isdir(Imagemount):
				mkdir(Imagemount)
			self.container = Console()
			self.phase = self.MOUNT
			self.run()
		else:
			callback({})

	def run(self):
		if self.phase == self.UNMOUNT:
			self.container.ePopen("umount %s" % Imagemount, self.appClosed)
		else:
			if BoxInfo.getItem("canMultiBoot")[self.slot]['device'] == 'ubi0:ubifs':
				self.container.ePopen("mount -t ubifs %s %s" % (BoxInfo.getItem("canMultiBoot")[self.slot]["device"], Imagemount), self.appClosed)
			else:
				self.container.ePopen("mount %s %s" % (BoxInfo.getItem("canMultiBoot")[self.slot]["device"], Imagemount), self.appClosed)


	def appClosed(self, data="", retval=0, extra_args=None):
		if retval == 0 and self.phase == self.MOUNT:
			if BoxInfo.getItem("HasRootSubdir") and BoxInfo.getItem("canMultiBoot")[self.slot]["rootsubdir"] != None:
				imagedir = ('%s/%s' % (Imagemount, BoxInfo.getItem("canMultiBoot")[self.slot]["rootsubdir"]))
			else:
				imagedir = Imagemount
			if os_path.isfile("%s/usr/bin/enigma2" % imagedir):
				rename("%s/usr/bin/enigma2" % imagedir, "%s/usr/bin/enigmax.bin" % imagedir)
				rename("%s/etc" % imagedir, "%s/etcx" % imagedir)
			self.phase = self.UNMOUNT
			self.run()
		else:
			self.container.killAll()
			if not os_path.ismount(Imagemount):
				rmdir(Imagemount)
			self.callback()
