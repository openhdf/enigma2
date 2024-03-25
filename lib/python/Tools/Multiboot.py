from glob import glob
from os import mkdir
from os import path as os_path
from os import remove, rename, rmdir, stat
from shutil import copy2
from subprocess import check_output

from boxbranding import getBoxType, getMachineName

from Components.Console import Console
from Components.SystemInfo import BoxInfo
from Tools.Directories import pathExists

Imagemount = "/tmp/multibootcheck"

def getMBbootdevice():
	if not os_path.isdir(Imagemount):
		mkdir(Imagemount)
	for device in ("/dev/mmcblk0p1", "/dev/mmcblk1p1", "/dev/mmcblk0p3", "/dev/mmcblk0p4", "/dev/mtdblock2", "/dev/block/by-name/bootoptions"):
		if os_path.exists(device):
			Console().ePopen("mount %s %s" % (device, Imagemount))
			if os_path.isfile(os_path.join(Imagemount, "STARTUP")):
				print('[Multiboot] Startupdevice found:', device)
				return device
			Console().ePopen("umount %s" % Imagemount)
	if not os_path.ismount(Imagemount):
		rmdir(Imagemount)


def getparam(line, param):
	return line.replace("userdataroot", "rootuserdata").rsplit('%s=' % param, 1)[1].split(' ', 1)[0]

def getMultibootslots():
	bootslots = {}
	mode12found = False
	if BoxInfo.getItem("MBbootdevice"):
		for _file in glob(os_path.join(Imagemount, 'STARTUP_*')):
			if 'MODE_' in _file:
				mode12found = True
				slotnumber = _file.rsplit('_', 3)[1]
			else:
				slotnumber = _file.rsplit('_', 1)[1]
		if not os_path.isdir(Imagemount):
			mkdir(Imagemount)
		Console().ePopen("/bin/mount %s %s" % (BoxInfo.getItem("MBbootdevice"), Imagemount))
		for _file in glob(os_path.join(Imagemount, "STARTUP_*")):
			if "STARTUP_RECOVERY" in _file:
				BoxInfo.setItem("RecoveryMode", True)
				print("[multiboot] [getMultibootslots] RecoveryMode is set to:%s" % BoxInfo.getItem("RecoveryMode"))
			slotnumber = _file.rsplit("_", 3 if "BOXMODE" in _file else 1)[1]
			if slotnumber.isdigit() and slotnumber not in bootslots:
				slot = {}
				for line in open(_file).readlines():
					# print("Multiboot getMultibootslots readlines = %s " %line)
					if "root=" in line:
						line = line.rstrip("\n")
						device = getparam(line, "root")
						if os_path.exists(device) or device == 'ubi0:ubifs':
							slot["device"] = device
							slot["startupfile"] = os_path.basename(_file)
							if "sda" in line:
								slot["kernel"] = "/dev/sda%s" % line.split("sda", 1)[1].split(" ", 1)[0]
								slot["rootsubdir"] = None
							else:
								try:
									slot["kernel"] = "%sp%s" % (device.split("p")[0], int(device.split("p")[1]) - 1)
								except:
									pass
							if "rootsubdir" in line:
								BoxInfo.setItem("HasRootSubdir", True)
								print("[multiboot] [getMultibootslots] HasRootSubdir is set to:%s" % BoxInfo.getItem("HasRootSubdir"))
								slot["rootsubdir"] = getparam(line, "rootsubdir")
								slot["kernel"] = getparam(line, "kernel")

						break
				if slot:
					bootslots[int(slotnumber)] = slot
		print("[multiboot1] getMultibootslots bootslots = %s" % bootslots)
		Console().ePopen("umount %s" % Imagemount)
		if not os_path.ismount(Imagemount):
			rmdir(Imagemount)
		if not mode12found and BoxInfo.getItem("canMode12"):
			#the boot device has ancient content and does not contain the correct STARTUP files
			for slot in range(1, 5):
				bootslots[slot] = {'device': '/dev/mmcblk0p%s' % (slot * 2 + 1), 'startupfile': None}
	print('[Multiboot] Bootslots found:', bootslots)
	return bootslots


def GetCurrentImage():
	if BoxInfo.getItem("canMultiBoot"):
		slot = [x[-1] for x in open("/sys/firmware/devicetree/base/chosen/bootargs", "r").read().split() if x.startswith("rootsubdir")]
		if slot:
			return int(slot[0])
		else:
			device = getparam(open("/sys/firmware/devicetree/base/chosen/bootargs", "r").read(), "root")
			for slot in list(BoxInfo.getItem("canMultiBoot").keys()):
				if BoxInfo.getItem("canMultiBoot")[slot]["device"] == device:
					return slot


def GetCurrentKern():
	if BoxInfo.getItem("HasRootSubdir"):
		return BoxInfo.getItem("HasRootSubdir") and (int(open("/sys/firmware/devicetree/base/chosen/bootargs", "r").read()[:-1].split("kernel=/dev/mmcblk0p")[1].split(" ")[0]))


def GetCurrentRoot():
	if BoxInfo.getItem("HasRootSubdir"):
		return BoxInfo.getItem("HasRootSubdir") and (int(open("/sys/firmware/devicetree/base/chosen/bootargs", "r").read()[:-1].split("root=/dev/mmcblk0p")[1].split(" ")[0]))


def GetCurrentImageMode():
	return bool(BoxInfo.getItem("canMultiBoot")) and BoxInfo.getItem("canMode12") and int(open("/sys/firmware/devicetree/base/chosen/bootargs", "r").read().replace("\0", "").split("=")[-1])


def GetSTARTUPFile():
	if BoxInfo.getItem("HAScmdline"):
		return "cmdline.txt"
	else:
		return "STARTUP"


def ReadSTARTUP():
	return BoxInfo.getItem("canMultiBoot") and open('/tmp/startupmount/%s' % GetSTARTUPFile(), 'r').read()


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


class GetImagelist():
	MOUNT = 0
	UNMOUNT = 1

	def __init__(self, callback):
		if BoxInfo.getItem("canMultiBoot"):
			self.slots = sorted(list(BoxInfo.getItem("canMultiBoot").keys()))
			self.callback = callback
			self.imagelist = {}
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
			self.slot = self.slots.pop(0)
			if BoxInfo.getItem("canMultiBoot")[self.slot]['device'] == 'ubi0:ubifs':
				self.container.ePopen("mount -t ubifs %s %s" % (BoxInfo.getItem("canMultiBoot")[self.slot]["device"], Imagemount), self.appClosed)
			else:
				self.container.ePopen("mount %s %s" % (BoxInfo.getItem("canMultiBoot")[self.slot]["device"], Imagemount), self.appClosed)

	def appClosed(self, data="", retval=0, extra_args=None):
		BuildVersion = "  "
		Build = " "  # ViX Openhdf Build No.
		Dev = " "  # ViX Dev No.
		Creator = " "  # Openpli Openvix Openatv Openhdf etc
		Date = " "
		BuildType = " "  # release etc
		if retval:
			self.imagelist[self.slot] = {"imagename": _("Empty slot")}
		if retval == 0 and self.phase == self.MOUNT:
			if BoxInfo.getItem("HasRootSubdir") and BoxInfo.getItem("canMultiBoot")[self.slot]["rootsubdir"] != None:
				imagedir = ('%s/%s' % (Imagemount, BoxInfo.getItem("canMultiBoot")[self.slot]["rootsubdir"]))
			else:
				imagedir = Imagemount
			if os_path.isfile("%s/usr/bin/enigma2" % imagedir):
				Creator = open("%s/etc/issue" % imagedir).readlines()[-2].capitalize().strip()[:-6].replace("-release", " rel")
				if Creator.startswith("Openhdf"):
					reader = boxbranding_reader(imagedir)
					BuildType = reader.getImageType()
					Build = reader.getImageBuild()
					Dev = BuildType != "release" and " %s" % reader.getImageDevBuild() or ''
					BuildVersionHDF = "%s %s %s" % (Creator, BuildType[0:3], Build)
					BuildVersionHDF = BuildVersionHDF.replace("rel", "#")
				if Creator.startswith("Openvix"):
					reader = boxbranding_reader(imagedir)
					BuildType = reader.getImageType()
					Build = reader.getImageBuild()
					Dev = BuildType != "release" and " %s" % reader.getImageDevBuild() or ""
					BuildVersion = "%s %s %s %s" % (Creator, BuildType[0:3], Build, Dev)
				else:
					try:
						from datetime import datetime
						date = datetime.fromtimestamp(stat(os_path.join(imagedir, "var/lib/opkg/status")).st_mtime).strftime("%Y-%m-%d")
						if date.startswith("1970"):
							date = datetime.fromtimestamp(stat(os_path.join(imagedir, "usr/share/bootlogo.mvi")).st_mtime).strftime("%Y-%m-%d")
						date = max(date, datetime.fromtimestamp(stat(os_path.join(imagedir, "usr/bin/enigma2")).st_mtime).strftime("%Y-%m-%d"))
					except Exception:
						date = _("Unknown")
					BuildVersion = "%s (%s)" % (open(os_path.join(imagedir, "etc/issue")).readlines()[-2].capitalize().strip()[:-6], date)
					if Creator.startswith("Openhdf"):
						BuildVersion = _("%s release %s") % (BuildVersionHDF, date)
				self.imagelist[self.slot] = {"imagename": "%s" % BuildVersion}
			else:
				self.imagelist[self.slot] = {"imagename": _("Empty slot")}
			if self.slots and BoxInfo.getItem("canMultiBoot")[self.slot]["device"] == BoxInfo.getItem("canMultiBoot")[self.slots[0]]["device"]:
				self.slot = self.slots.pop(0)
				self.appClosed()
			else:
				self.phase = self.UNMOUNT
				self.run()
		elif self.slots:
			self.phase = self.MOUNT
			self.run()
		else:
			self.container.killAll()
			if not os_path.ismount(Imagemount):
				rmdir(Imagemount)
			self.callback(self.imagelist)


class boxbranding_reader:  # Many thanks to Huevos for creating this reader - well beyond my skill levels!
	def __init__(self, OsPath):
		if pathExists("%s/usr/lib64" % OsPath):
			self.branding_path = "%s/usr/lib64/enigma2/python/" % OsPath
		else:
			self.branding_path = "%s/usr/lib/enigma2/python/" % OsPath
		self.branding_file = "boxbranding.so"
		self.tmp_path = "/tmp/"
		self.helper_file = "helper.py"

		self.output = {
			"getMachineBuild": "",
			"getMachineProcModel": "",
			"getMachineBrand": "",
			"getMachineName": "",
			"getMachineMtdKernel": "",
			"getMachineKernelFile": "",
			"getMachineMtdRoot": "",
			"getMachineRootFile": "",
			"getMachineMKUBIFS": "",
			"getMachineUBINIZE": "",
			"getBoxType": "",
			"getBrandOEM": "",
			"getOEVersion": "",
			"getDriverDate": "",
			"getImageVersion": "",
			"getImageBuild": "",
			"getImageDistro": "",
			"getImageFolder": "",
			"getImageFileSystem": "",
			"getImageDevBuild": "",
			"getImageType": "",
			"getMachineMake": "",
			"getImageArch": "",
			"getFeedsUrl": "",
		}
		self.createHelperFile()
		self.copyBrandingFile()
		self.readBrandingFile()
		self.removeHelperFile()
		self.removeBrandingFile()
		self.addBrandingMethods()

	def readBrandingFile(self):  # Reads boxbranding.so and updates self.output
		output = eval(check_output(["python", os_path.join(self.tmp_path, self.helper_file)]))
		if output:
			for att in list(self.output.keys()):
				self.output[att] = output[att]

	def addBrandingMethods(self):  # This creates reader.getBoxType(), reader.getImageDevBuild(), etc
		loc = {}
		for att in list(self.output.keys()):
			exec("def %s(self): return self.output[\"%s\"]" % (att, att), None, loc)
		for name, value in list(loc.items()):
			setattr(boxbranding_reader, name, value)

	def createHelperFile(self):
		f = open(os_path.join(self.tmp_path, self.helper_file), "w+")
		f.write(self.helperFileContent())
		f.close()

	def copyBrandingFile(self):
		copy2(os_path.join(self.branding_path, self.branding_file), os_path.join(self.tmp_path, self.branding_file))

	def removeHelperFile(self):
		self.removeFile(os_path.join(self.tmp_path, self.helper_file))

	def removeBrandingFile(self):
		self.removeFile(os_path.join(self.tmp_path, self.branding_file))

	def removeFile(self, toRemove):
		if os_path.isfile(toRemove):
			remove(toRemove)

	def helperFileContent(self):
		out = []
		out.append("try:")
		out.append("\timport boxbranding")
		out.append("\toutput = {")
		for att in list(self.output.keys()):
			out.append("\t\t\"%s\": boxbranding.%s()," % (att, att))
		out.append("\t}")
		out.append("except Exception:")
		out.append("\t\toutput = None")
		out.append("print(output)")
		out.append("")
		return "\n".join(out)


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
