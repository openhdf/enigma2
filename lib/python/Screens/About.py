from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.config import config
from Components.Sources.StaticText import StaticText
from Components.Harddisk import Harddisk
from Components.NimManager import nimmanager
from Components.About import about
from Components.ScrollLabel import ScrollLabel
from Components.SystemInfo import SystemInfo
from Components.config import config
from enigma import eTimer, getEnigmaVersionString, getDesktop, eGetEnigmaDebugLvl
from boxbranding import getBoxType, getMachineBuild, getMachineBrand, getMachineName, getImageVersion, getImageBuild, getDriverDate

from Components.Pixmap import MultiPixmap
from Components.Network import iNetwork

from Components.Label import Label
from Components.ProgressBar import ProgressBar

from Tools.StbHardware import getFPVersion
from Tools.Directories import fileCheck

import os
import re
from os import path, popen, system
from re import search
from six.moves import range
import six

SIGN = '°' if six.PY3 else str('\xc2\xb0')

def find_rootfssubdir(file):
	startup_content = read_startup("/boot/" + file)
	rootsubdir = startup_content[startup_content.find("rootsubdir=")+11:].split()[0]
	if rootsubdir.startswith("linuxrootfs"):
		return rootsubdir
	return

def read_startup(FILE):
	file = FILE
	try:
		with open(file, 'r') as myfile:
			data=myfile.read().replace('\n', '')
		myfile.close()
	except IOError:
		print("[ERROR] failed to open file %s" % filename)
	return ret

def parseLines(filename):
	ret = ["N/A"]
	try:
		f = open(filename, "rb")
		ret = f.readlines()
		f.close()
	except IOError:
		print("[ERROR] failed to open file %s" % filename)
	return ret

def MyDateConverter(StringDate):
	## StringDate must be a string "YYYY-MM-DD" or "YYYYMMDD"
	try:
		if len(StringDate) == 8:
			year = StringDate[0:4]
			month = StringDate[4:6]
			day = StringDate[6:8]
			StringDate = ' '.join((year, month, day))
		else:
			StringDate = StringDate.replace("-", " ")
		StringDate = time.strftime(config.usage.date.full.value, time.strptime(StringDate, "%Y %m %d"))
		return StringDate
	except:
		return _("unknown")

def getAboutText():
	AboutText = ""
	AboutText += _("Model:\t\t%s %s\n") % (getMachineBrand(), getMachineName())
	AboutText += _("OEM Model:\t\t%s\n") % getMachineBuild()

	bootloader = ""
	if path.exists('/sys/firmware/devicetree/base/bolt/tag'):
		f = open('/sys/firmware/devicetree/base/bolt/tag', 'r')
		bootloader = f.readline().replace('\x00', '').replace('\n', '')
		f.close()
		AboutText += _("Bootloader:\t\t%s\n") % (bootloader)

	if path.exists('/proc/stb/info/chipset'):
		AboutText += _("Chipset:\t\t%s") % about.getChipSetString() + "\n"

	AboutText += _("CPU:\t\t%s  (%s)  %s cores") % (about.getCPUString(), about.getCPUSpeedString(), about.getCpuCoresString()) + "\n"

	imagestarted = ""
	bootname = ''
	if path.exists('/boot/bootname'):
		f = open('/boot/bootname', 'r')
		bootname = f.readline().split('=')[1]
		f.close()
	if SystemInfo["canMultiBoot"]:
		slot = image = GetCurrentImage()
		bootmode = ""
		part = _("eMMC slot %s") %slot
		if SystemInfo["canMode12"]:
			bootmode = _(" bootmode = %s") %GetCurrentImageMode()
		if SystemInfo["HasHiSi"] and "sda" in SystemInfo["canMultiBoot"][slot]['device']:
			if slot > 4:
				image -=4
			else:
				image -=1
			part = "SDcard slot %s (%s) " %(image, SystemInfo["canMultiBoot"][slot]['device'])
		AboutText += _("Selected Image:\t\t%s") % _("STARTUP_") + str(slot) + "  (" + part + bootmode + ")\n"

	AboutText += _("Version / Build:\t\t%s  (%s)") % (getImageVersion(), MyDateConverter(getImageBuild())) + "\n"
	AboutText += _("Kernel:\t\t%s") % about.getKernelVersionString() + "\n"
	AboutText += _("Drivers:\t\t%s") % MyDateConverter(getDriverDate()) + "\n"

	skinWidth = getDesktop(0).size().width()
	skinHeight = getDesktop(0).size().height()

	AboutText += _("Skin:\t\t%s") % config.skin.primary_skin.value.split("/")[0] + _("  (%s x %s)") % (skinWidth, skinHeight) + "\n"

	AboutText += _("GStreamer:\t\t%s") % about.getGStreamerVersionString() + "\n"
	AboutText += _("Python:\t\t%s") % about.getPythonVersionString() + "\n"

	MyFlashDate = about.getFlashDateString()
	if MyFlashDate != _("unknown"):
		AboutText += _("Installed:\t\t%s") % MyDateConverter(MyFlashDate) + "\n"

	AboutText += _("Last E2 update:\t\t%s") % MyDateConverter(getEnigmaVersionString()) + "\n"
	AboutText += _("Enigma2 debug level:\t%d") % eGetEnigmaDebugLvl() + "\n"

	fp_version = getFPVersion()
	if fp_version is None:
		fp_version = ""
	elif fp_version != 0:
		fp_version = _("Frontprocessor version:\t%s") % fp_version
		AboutText += fp_version + "\n"

	tempinfo = ""
	if path.exists('/proc/stb/sensors/temp0/value'):
		f = open('/proc/stb/sensors/temp0/value', 'r')
		tempinfo = f.read()
		f.close()
	elif path.exists('/proc/stb/fp/temp_sensor'):
		f = open('/proc/stb/fp/temp_sensor', 'r')
		tempinfo = f.read()
		f.close()
	elif path.exists('/proc/stb/sensors/temp/value'):
		f = open('/proc/stb/sensors/temp/value', 'r')
		tempinfo = f.read()
		f.close()
	if tempinfo and int(tempinfo.replace('\n', '')) > 0:
		AboutText += _("System temperature:\t%s") % tempinfo.replace('\n', '').replace(' ', '') + SIGN + "C\n"

	tempinfo = ""
	if path.exists('/proc/stb/fp/temp_sensor_avs'):
		f = open('/proc/stb/fp/temp_sensor_avs', 'r')
		tempinfo = f.read()
		f.close()
	elif path.exists('/proc/stb/power/avs'):
		f = open('/proc/stb/power/avs', 'r')
		tempinfo = f.read()
		f.close()
	elif path.exists('/sys/devices/virtual/thermal/thermal_zone0/temp'):
		try:
			f = open('/sys/devices/virtual/thermal/thermal_zone0/temp', 'r')
			tempinfo = f.read()
			tempinfo = tempinfo[:-4]
			f.close()
		except:
			tempinfo = ""
	elif path.exists('/proc/hisi/msp/pm_cpu'):
		try:
			for line in open('/proc/hisi/msp/pm_cpu').readlines():
				line = [x.strip() for x in line.strip().split(":")]
				if line[0] in ("Tsensor"):
					temp = line[1].split("=")
					temp = line[1].split(" ")
					tempinfo = temp[2]
					if getMachineBuild() in ('u41', 'u42', 'u43'):
						tempinfo = str(int(tempinfo) - 15)
		except:
			tempinfo = ""
	if tempinfo and int(tempinfo.replace('\n', '')) > 0:
		AboutText += _("Processor temperature:\t%s") % tempinfo.replace('\n', '').replace(' ', '') + SIGN + "C\n"
	AboutLcdText = AboutText.replace('\t', ' ')

	return AboutText, AboutLcdText

class About(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		Screen.setTitle(self, _("Image Information"))
		self.skinName = "AboutOE"
		self.populate()

		self["key_green"] = Button(_("Translations"))
		self["actions"] = ActionMap(["SetupActions", "ColorActions", "TimerEditActions"],
			{
				"cancel": self.close,
				"ok": self.close,
				"log": self.showAboutReleaseNotes,
				"blue": self.showMemoryInfo,
				"up": self["AboutScrollLabel"].pageUp,
				"down": self["AboutScrollLabel"].pageDown,
				"green": self.showTranslationInfo,
			})

	def populate(self):
		def netspeed():
			netspeed=""
			for line in popen('ethtool eth0 |grep Speed', 'r'):
				line = line.strip().split(":")
				line =line[1].replace(' ', '')
				netspeed += line
				return str(netspeed)
		def netspeed_eth1():
			netspeed=""
			for line in popen('ethtool eth1 |grep Speed', 'r'):
				line = line.strip().split(":")
				line =line[1].replace(' ', '')
				netspeed += line
				return str(netspeed)
		def netspeed_ra0():
			netspeed=""
			for line in popen('iwconfig ra0 | grep Bit | cut -c 20-30', 'r'):
				line = line.strip()
				netspeed += line
				return str(netspeed)
		def netspeed_wlan0():
			netspeed=""
			for line in popen('iwconfig wlan0 | grep Bit | cut -c 20-30', 'r'):
				line = line.strip()
				netspeed += line
				return str(netspeed)
		def netspeed_wlan1():
			netspeed=""
			for line in popen('iwconfig wlan1 | grep Bit | cut -c 20-30', 'r'):
				line = line.strip()
				netspeed += line
				return str(netspeed)
		def freeflash():
			freeflash=""
			for line in popen("df -mh / | grep -v '^Filesystem' | awk '{print $4}'", 'r'):
				line = line.strip()
				freeflash += line
				return str(freeflash)
		self["lab1"] = StaticText(_("openHDF"))
		self["lab2"] = StaticText(_("Support at") + " www.HDFreaks.cc")
		model = None
		AboutText = ""
		self["lab2"] = StaticText(_("Support @") + " www.hdfreaks.cc")
		AboutText += _("Model:\t%s %s - OEM Model: %s\n") % (getMachineBrand(), getMachineName(), getBrandOEM())

		if path.exists('/proc/stb/info/chipset'):
			AboutText += _("Chipset:\t%s") % about.getChipSetString() + "\n"

		cmd = 'cat /proc/cpuinfo | grep "cpu MHz" -m 1 | awk -F ": " ' + "'{print $2}'"
		cmd2 = 'cat /proc/cpuinfo | grep "BogoMIPS" -m 1 | awk -F ": " ' + "'{print $2}'"
		try:
			res = popen(cmd).read()
			res2 = popen(cmd2).read()
		except:
			res = ""
			res2 = ""
		cpuMHz = ""

		bootloader = ""
		if path.exists('/sys/firmware/devicetree/base/bolt/tag'):
			f = open('/sys/firmware/devicetree/base/bolt/tag', 'r')
			bootloader = f.readline().replace('\x00', '').replace('\n', '')
			f.close()
		BootLoaderVersion = 0
		try:
			if bootloader:
				AboutText += _("Bootloader:\t%s\n") % (bootloader)
				BootLoaderVersion = int(bootloader[1:])
		except:
			BootLoaderVersion = 0

		if getMachineBuild() in ('vusolo4k', 'gbx34k'):
			cpuMHz = "   (1,5 GHz)"
		elif getMachineBuild() in ('u41', 'u42'):
			cpuMHz = "   (1,0 GHz)"
		elif getMachineBuild() in ('vuuno4k', 'dm900', 'gb7252', 'dags7252'):
			cpuMHz = "   (1,7 GHz)"
		elif getMachineBuild() in ('formuler1tc', 'formuler1', 'triplex'):
			cpuMHz = "   (1,3 GHz)"
		elif getMachineBuild() in ('u5', 'u51', 'u52', 'u53', 'u5pvr', 'h9', 'sf8008', 'sf8008s', 'sf8008t', 'hd60', "hd61", 'i55plus'):
			cpuMHz = "   (1,6 GHz)"
		elif getMachineBuild() in ('sf5008', 'et13000', 'et1x000', 'hd52', 'hd51', 'sf4008', 'vs1500', 'h7', 'osmio4k', 'osmio4kplus', 'osmini4k'):
			try:
				import binascii
				f = open('/sys/firmware/devicetree/base/cpus/cpu@0/clock-frequency', 'rb')
				clockfrequency = f.read()
				f.close()
				cpuMHz = "%s MHz" % str(round(int(binascii.hexlify(clockfrequency), 16)//1000000, 1))
			except:
				cpuMHz = "1,7 GHz"
		else:
			if path.exists('/proc/cpuinfo'):
				f = open('/proc/cpuinfo', 'r')
				temp = f.readlines()
				f.close()
				try:
					for lines in temp:
						lisp = lines.split(': ')
						if lisp[0].startswith('cpu MHz'):
							#cpuMHz = "   (" +  lisp[1].replace('\n', '') + " MHz)"
							cpuMHz = "   (" +  str(int(float(lisp[1].replace('\n', '')))) + " MHz)"
							break
				except:
					pass

		bogoMIPS = ""
		if res:
			cpuMHz = "" + res.replace("\n", "") + " MHz"
		if res2:
			bogoMIPS = "" + res2.replace("\n", "")

		if getMachineBuild() in ('vusolo4k', 'hd51', 'hd52', 'sf4008', 'dm900', 'h7', 'gb7252', '8100s'):
			AboutText += _("CPU:\t%s") % about.getCPUString() + cpuMHz + "\n"
		else:
			AboutText += _("CPU:\t%s") % about.getCPUString() + " " + cpuMHz + "\n"
		dMIPS = 0
		if getMachineBuild() in ('vusolo4k'):
			dMIPS = "10.500"
		elif getMachineBuild() in ('hd52', 'hd51', 'sf4008', 'dm900', 'h7', 'gb7252', '8100s'):
			dMIPS = "12.000"
		if getMachineBuild() in ('vusolo4k', 'hd51', 'hd52', 'sf4008', 'dm900', 'h7', 'gb7252', '8100s'):
			AboutText += _("DMIPS:\t") + dMIPS + "\n"
		else:
			AboutText += _("BogoMIPS:\t%s") % bogoMIPS + "\n"

		tempinfo = ""
		if path.exists('/proc/stb/sensors/temp0/value'):
			f = open('/proc/stb/sensors/temp0/value', 'r')
			tempinfo = f.read()
			f.close()
		elif path.exists('/proc/stb/fp/temp_sensor'):
			f = open('/proc/stb/fp/temp_sensor', 'r')
			tempinfo = f.read()
			f.close()
		elif path.exists('/proc/stb/sensors/temp/value'):
			f = open('/proc/stb/sensors/temp/value', 'r')
			tempinfo = f.read()
			f.close()
		elif path.exists('/sys/devices/virtual/thermal/thermal_zone0/temp'):
			try:
				f = open('/sys/devices/virtual/thermal/thermal_zone0/temp', 'r')
				tempinfo = f.read()
				tempinfo = tempinfo[:-4]
				f.close()
			except:
				tempinfo = ""

		if tempinfo and int(tempinfo.replace('\n', '')) > 0:
			mark = str('\xc2\xb0')
			AboutText += _("System Temp:\t%s") % tempinfo.replace('\n', '').replace(' ', '') + mark + "C\n"

		tempinfo = ""
		if path.exists('/proc/stb/fp/temp_sensor_avs'):
			f = open('/proc/stb/fp/temp_sensor_avs', 'r')
			tempinfo = f.read()
			f.close()
		elif path.exists('/proc/stb/power/avs'):
			f = open('/proc/stb/power/avs', 'r')
			tempinfo = f.read()
			f.close()
		elif path.exists('/sys/devices/virtual/thermal/thermal_zone0/temp'):
			try:
				f = open('/sys/devices/virtual/thermal/thermal_zone0/temp', 'r')
				tempinfo = f.read()
				tempinfo = tempinfo[:-4]
				f.close()
			except:
				tempinfo = ""
		elif path.exists('/proc/hisi/msp/pm_cpu'):
			try:
				for line in open('/proc/hisi/msp/pm_cpu').readlines():
					line = [x.strip() for x in line.strip().split(":")]
					if line[0] in ("Tsensor"):
						temp = line[1].split("=")
						temp = line[1].split(" ")
						tempinfo = temp[2]
			except:
				tempinfo = ""
		if tempinfo and int(tempinfo.replace('\n', '')) > 0:
			mark = str('\xc2\xb0')
			AboutText += _("CPU Temp:\t%s") % tempinfo.replace('\n', '').replace(' ', '') + mark + "C\n"

		AboutText += _("Cores:\t%s") % about.getCpuCoresString() + "\n"
		AboutText += _("HDF Version:\tV%s") % getImageVersion() + " Build #" + getImageBuild() + " based on " + getOEVersion() + "\n"
		AboutText += _("Kernel (Box):\t%s") % about.getKernelVersionString() + " (" + getBoxType() + ")" + "\n"

		if path.isfile("/etc/issue"):
			version = open("/etc/issue").readlines()[-2].upper().strip()[:-6]
			if path.isfile("/etc/image-version"):
				build = self.searchString("/etc/image-version", "^build=")
				version = "%s #%s" % (version, build)
			AboutText += _("Image:\t%s") % version + "\n"

		imagestarted = ""
		bootname = ''
		if path.exists('/boot/bootname'):
			f = open('/boot/bootname', 'r')
			bootname = f.readline().split('=')[1]
			f.close()
		if SystemInfo["HasRootSubdir"]:
			image = find_rootfssubdir("STARTUP")
			AboutText += _("Selected Image:\t%s") % "STARTUP_" + image[-1:] + bootname + "\n"
		elif getMachineBuild() in ('gbmv200', 'cc1', 'sf8008', 'ustym4kpro', 'beyonwizv2', "viper4k"):
			if path.exists('/boot/STARTUP'):
				f = open('/boot/STARTUP', 'r')
				f.seek(5)
				image = f.read(4)
				if image == "emmc":
					image = "1"
				elif image == "usb0":
					f.seek(13)
					image = f.read(1)
					if image == "1":
						image = "2"
					elif image == "3":
						image = "3"
					elif image == "5":
						image = "4"
					elif image == "7":
						image = "5"
				f.close()
				if bootname: bootname = "   (%s)" %bootname 
				AboutText += _("Partition:\t%s") % "STARTUP_" + image + bootname + "\n"
			else:
				f = open('/boot/STARTUP', 'r')
				f.seek(22)
				image = f.read(1)
				f.close()
				if bootname: bootname = "   (%s)" %bootname
				AboutText += _("Partition:\t%s") % "STARTUP_" + image + bootname + "\n"

		if SystemInfo["HaveMultiBoot"]:
			MyFlashDate = about.getFlashDateString()
			if path.isfile("/etc/filesystems"):
				AboutText += _("Flashed:\t%s") % MyFlashDate + "\n"
				#AboutText += _("Flashed:\tMultiboot active\n")
		else:
			AboutText += _("Flashed:\t%s\n") % about.getFlashDateString()

		string = getDriverDate()
		year = string[0:4]
		month = string[4:6]
		day = string[6:8]
		driversdate = '-'.join((year, month, day))
		gstcmd = 'opkg list-installed | grep "gstreamer1.0 -" | cut -c 16-32'
		gstcmd2 = os.system(gstcmd)
		#return (gstcmd2)
		AboutText += _("Drivers:\t%s") % driversdate + "\n"
		AboutText += _("GStreamer:\t%s") % about.getGStreamerVersionString() + "\n"
		AboutText += _("Python:\t%s\n") % about.getPythonVersionString()
		AboutText += _("Free Flash:\t%s\n") % freeflash()
		AboutText += _("Skin:\t%s (%s x %s)\n") % (config.skin.primary_skin.value.split('/')[0], getDesktop(0).size().width(), getDesktop(0).size().height())
		AboutText += _("Last update:\t%s") % getEnigmaVersionString() + " to Build #" + getImageBuild() + "\n"
		AboutText += _("E2 (re)starts:\t%s\n") % config.misc.startCounter.value
		AboutText += _("Uptime") + ":\t" + about.getBoxUptime() + "\n"
		if SystemInfo["WakeOnLAN"]:
			if fileCheck("/proc/stb/power/wol"):
				WOLmode = open("/proc/stb/power/wol").read()[:-1]
			if fileCheck("/proc/stb/fp/wol"):
				WOLmode = open("/proc/stb/fp/wol").read()[:-1]
			AboutText += _("WakeOnLAN:\t%s\n") % WOLmode
		AboutText += _("Network:")
		eth0 = about.getIfConfig('eth0')
		eth1 = about.getIfConfig('eth1')
		ra0 = about.getIfConfig('ra0')
		wlan0 = about.getIfConfig('wlan0')
		wlan1 = about.getIfConfig('wlan1')
		if 'addr' in eth0:
			for x in about.GetIPsFromNetworkInterfaces():
				AboutText += "\t" + x[0] + ": " + x[1] + " (" + netspeed() + ")\n"
		elif 'addr' in eth1:
			for x in about.GetIPsFromNetworkInterfaces():
				AboutText += "\t" + x[0] + ": " + x[1] + " (" + netspeed_eth1() + ")\n"
		elif 'addr' in ra0:
			for x in about.GetIPsFromNetworkInterfaces():
				AboutText += "\t" + x[0] + ": " + x[1] + " (~" + netspeed_ra0() + ")\n"
		elif 'addr' in wlan0:
			for x in about.GetIPsFromNetworkInterfaces():
				AboutText += "\t" + x[0] + ": " + x[1] + " (~" + netspeed_wlan0() + ")\n"
		elif 'addr' in wlan1:
			for x in about.GetIPsFromNetworkInterfaces():
				AboutText += "\t" + x[0] + ": " + x[1] + " (~" + netspeed_wlan1() + ")\n"
		else:
			for x in about.GetIPsFromNetworkInterfaces():
				AboutText += "\t" + x[0] + ": " + x[1] + "\n"

		fp_version = getFPVersion()
		if fp_version is None:
			fp_version = ""
		elif fp_version != 0:
			fp_version = _("Frontprocessor:\tVersion %s") % fp_version
			AboutText += fp_version + "\n"

		AboutLcdText = AboutText.replace('\t', ' ')

		self["AboutScrollLabel"] = ScrollLabel(AboutText)

	def searchString(self, file, search):
		f = open(file)
		for line in f:
			if re.match(search, line):
				return line.split("=")[1].replace('\n', '')
		f.close()

	def showTranslationInfo(self):
		self.session.open(TranslationInfo)

	def showMemoryInfo(self):
		self.session.open(MemoryInfo)

	def showAboutReleaseNotes(self):
		self.session.open(ViewGitLog)

	def createSummary(self):
		return AboutSummary

class Devices(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		Screen.setTitle(self, _("Device Information"))
		self["TunerHeader"] = StaticText(_("Detected NIMs:"))
		self["HDDHeader"] = StaticText(_("Detected Devices:"))
		self["MountsHeader"] = StaticText(_("Network Servers:"))
		self["nims"] = StaticText()
		self["hdd"] = StaticText()
		self["mounts"] = StaticText()
		self.list = []
		self.activityTimer = eTimer()
		self.activityTimer.timeout.get().append(self.populate2)
		self["actions"] = ActionMap(["SetupActions", "ColorActions", "TimerEditActions"],
			{
				"cancel": self.close,
				"ok": self.close,
			})
		self.onLayoutFinish.append(self.populate)

	def populate(self):
		self.mountinfo = ''
		self["actions"].setEnabled(False)
		scanning = _("Wait please while scanning for devices...")
		self["nims"].setText(scanning)
		self["hdd"].setText(scanning)
		self['mounts'].setText(scanning)
		self.activityTimer.start(1)

	def populate2(self):
		self.activityTimer.stop()
		self.Console = Console()
		niminfo = ""
		nims = nimmanager.nimList()
		for count in range(len(nims)):
			if niminfo:
				niminfo += "\n"
			niminfo += nims[count]
		self["nims"].setText(niminfo)

		self.list = []
		list2 = []
		f = open('/proc/partitions', 'r')
		for line in f.readlines():
			parts = line.strip().split()
			if not parts:
				continue
			device = parts[3]
			if not search('sd[a-z][1-9]', device):
				continue
			if device in list2:
				continue

			mount = '/dev/' + device
			f = open('/proc/mounts', 'r')
			for line in f.readlines():
				if device in line:
					parts = line.strip().split()
					mount = str(parts[1])
					break
			f.close()

			if not mount.startswith('/dev/'):
				size = Harddisk(device).diskSize()
				free = Harddisk(device).free()

				if ((float(size) // 1024) // 1024) >= 1:
					sizeline = _("Size: ") + str(round(((float(size) // 1024) // 1024), 2)) + " " + _("TB")
				elif (size // 1024) >= 1:
					sizeline = _("Size: ") + str(round((float(size) // 1024), 2)) +  " " + _("GB")
				elif size >= 1:
					sizeline = _("Size: ") + str(size) +  " " + _("MB")
				else:
					sizeline = _("Size: ") + _("unavailable")

				if ((float(free) // 1024) // 1024) >= 1:
					freeline = _("Free: ") + str(round(((float(free) // 1024) // 1024), 2)) +  " " + _("TB")
				elif (free // 1024) >= 1:
					freeline = _("Free: ") + str(round((float(free) // 1024), 2)) +  " " + _("GB")
				elif free >= 1:
					freeline = _("Free: ") + str(free) +  " " + _("MB")
				else:
					freeline = _("Free: ") + _("full")
				self.list.append(mount + '\t' + sizeline + ' \t' + freeline)
			else:
				self.list.append(mount + '\t' + _('Not mounted'))

			list2.append(device)
		self.list = '\n'.join(self.list)
		self["hdd"].setText(self.list)

		self.Console.ePopen("df -mh | grep -v '^Filesystem'", self.Stage1Complete)

	def Stage1Complete(self, result, retval, extra_args=None):
		result = six.ensure_str(result)
		result = result.replace('\n                        ', ' ').split('\n')
		self.mountinfo = ""
		for line in result:
			self.parts = line.split()
			if line and self.parts[0] and (self.parts[0].startswith('192') or self.parts[0].startswith('//192')):
				line = line.split()
				try:
					ipaddress = line[0]
				except:
					ipaddress = ""
				try:
					mounttotal = line[1]
				except:
					mounttotal = ""
				try:
					mountfree = line[3]
				except:
					mountfree = ""
				if self.mountinfo:
					self.mountinfo += "\n"
				self.mountinfo += "%s (%sB, %sB %s)" % (ipaddress, mounttotal, mountfree, _("free"))

		if self.mountinfo:
			self["mounts"].setText(self.mountinfo)
		else:
			self["mounts"].setText(_('none'))
		self["actions"].setEnabled(True)

	def createSummary(self):
		return AboutSummary

class SystemMemoryInfo(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		Screen.setTitle(self, _("Memory Information"))
		self.skinName = ["SystemMemoryInfo", "About"]
		self["lab1"] = StaticText(_("OpenHDF"))
		self["AboutScrollLabel"] = ScrollLabel()
		self["actions"] = ActionMap(["SetupActions", "ColorActions"],
			{
				"cancel": self.close,
				"ok": self.close,
				"blue": self.showMemoryInfo,
				"up": self["AboutScrollLabel"].pageUp,
				"down": self["AboutScrollLabel"].pageDown,
			})

		out_lines = open("/proc/meminfo").readlines()
		self.AboutText = _("RAM") + '\n\n'
		RamTotal = "-"
		RamFree = "-"
		for lidx in range(len(out_lines) - 1):
			tstLine = out_lines[lidx].split()
			if "MemTotal:" in tstLine:
				MemTotal = out_lines[lidx].split()
				self.AboutText += _("Total Memory:") + "\t" + MemTotal[1] + "\n"
			if "MemFree:" in tstLine:
				MemFree = out_lines[lidx].split()
				self.AboutText += _("Free Memory:") + "\t" + MemFree[1] + "\n"
			if "Buffers:" in tstLine:
				Buffers = out_lines[lidx].split()
				self.AboutText += _("Buffers:") + "\t" + Buffers[1] + "\n"
			if "Cached:" in tstLine:
				Cached = out_lines[lidx].split()
				self.AboutText += _("Cached:") + "\t" + Cached[1] + "\n"
			if "SwapTotal:" in tstLine:
				SwapTotal = out_lines[lidx].split()
				self.AboutText += _("Total Swap:") + "\t" + SwapTotal[1] + "\n"
			if "SwapFree:" in tstLine:
				SwapFree = out_lines[lidx].split()
				self.AboutText += _("Free Swap:") + "\t" + SwapFree[1] + "\n\n"

		self["actions"].setEnabled(False)
		self.Console = Console()
		self.Console.ePopen("df -mh / | grep -v '^Filesystem'", self.Stage1Complete)

	def MySize(self, RamText):
		RamText_End = RamText[len(RamText)-1]
		RamText_End2 = RamText_End
		if RamText_End == "G":
			RamText_End = _("GB")
		elif RamText_End == "M":
			RamText_End = _("MB")
		elif RamText_End == "K":
			RamText_End = _("KB")
		if RamText_End != RamText_End2:
			RamText = RamText[0:len(RamText)-1] + " " + RamText_End
		return RamText

	def Stage1Complete(self, result, retval, extra_args=None):
		result = six.ensure_str(result)
		flash = str(result).replace('\n', '')
		flash = flash.split()
		RamTotal = self.MySize(flash[1])
		RamFree = self.MySize(flash[3])

		self.AboutText += _("FLASH") + '\n\n'
		self.AboutText += _("Total:") + "\t" + RamTotal + "\n"
		self.AboutText += _("Free:") + "\t" + RamFree + "\n\n"

		self["AboutScrollLabel"].setText(self.AboutText)
		self["actions"].setEnabled(True)

	def createSummary(self):
		return AboutSummary

	def showMemoryInfo(self):
		self.session.open(MemoryInfo)

class SystemNetworkInfo(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		Screen.setTitle(self, _("Network Information"))
		self.skinName = ["SystemNetworkInfo", "WlanStatus"]
		self["LabelBSSID"] = StaticText()
		self["LabelESSID"] = StaticText()
		self["LabelQuality"] = StaticText()
		self["LabelSignal"] = StaticText()
		self["LabelBitrate"] = StaticText()
		self["LabelEnc"] = StaticText()
		self["BSSID"] = StaticText()
		self["ESSID"] = StaticText()
		self["quality"] = StaticText()
		self["signal"] = StaticText()
		self["bitrate"] = StaticText()
		self["enc"] = StaticText()

		self["IFtext"] = StaticText()
		self["IF"] = StaticText()
		self["Statustext"] = StaticText()
		self["statuspic"] = MultiPixmap()
		self["statuspic"].setPixmapNum(1)
		self["statuspic"].show()

		self.iface = None
		self.createscreen()
		self.iStatus = None

		if iNetwork.isWirelessInterface(self.iface):
			try:
				from Plugins.SystemPlugins.WirelessLan.Wlan import iStatus
				self.iStatus = iStatus
			except:
				pass
			self.resetList()
			self.onClose.append(self.cleanup)
		self.updateStatusbar()

		self["key_red"] = StaticText(_("Close"))

		self["actions"] = ActionMap(["SetupActions", "ColorActions", "DirectionActions"],
			{
				"cancel": self.close,
				"ok": self.close,
				"up": self["AboutScrollLabel"].pageUp,
				"down": self["AboutScrollLabel"].pageDown
			})

	def createscreen(self):
		def netspeed():
			netspeed=""
			for line in popen('ethtool eth0 |grep Speed', 'r'):
				line = line.strip().split(":")
				line =line[1].replace(' ', '')
				netspeed += line
				return str(netspeed)
		def netspeed_eth1():
			netspeed=""
			for line in popen('ethtool eth1 |grep Speed', 'r'):
				line = line.strip().split(":")
				line =line[1].replace(' ', '')
				netspeed += line
				return str(netspeed)
		self.AboutText = ""
		self.iface = "eth0"
		eth0 = about.getIfConfig('eth0')
		if 'addr' in eth0:
			self.AboutText += _("IP:") + "\t\t" + eth0['addr'] + "\n"
			if 'netmask' in eth0:
				self.AboutText += _("Netmask:") + "\t\t" + eth0['netmask'] + "\n"
			if 'hwaddr' in eth0:
				self.AboutText += _("MAC:") + "\t\t" + eth0['hwaddr'] + "\n"
			self.AboutText += _("Network Speed:") + "\t\t" + netspeed() + "\n"
			self.iface = 'eth0'

		eth1 = about.getIfConfig('eth1')
		if 'addr' in eth1:
			self.AboutText += _("IP:") + "\t\t" + eth1['addr'] + "\n"
			if 'netmask' in eth1:
				self.AboutText += _("Netmask:") + "\t\t" + eth1['netmask'] + "\n"
			if 'hwaddr' in eth1:
				self.AboutText += _("MAC:") + "\t\t" + eth1['hwaddr'] + "\n"
			self.AboutText += _("Network Speed:") + "\t\t" + netspeed_eth1() + "\n"
			self.iface = 'eth1'

		ra0 = about.getIfConfig('ra0')
		if 'addr' in ra0:
			self.AboutText += _("IP:") + "\t\t" + ra0['addr'] + "\n"
			if 'netmask' in ra0:
				self.AboutText += _("Netmask:") + "\t\t" + ra0['netmask'] + "\n"
			if 'hwaddr' in ra0:
				self.AboutText += _("MAC:") + "\t\t" + ra0['hwaddr'] + "\n"
			self.iface = 'ra0'

		wlan0 = about.getIfConfig('wlan0')
		if 'addr' in wlan0:
			self.AboutText += _("IP:") + "\t\t" + wlan0['addr'] + "\n"
			if 'netmask' in wlan0:
				self.AboutText += _("Netmask:") + "\t\t" + wlan0['netmask'] + "\n"
			if 'hwaddr' in wlan0:
				self.AboutText += _("MAC:") + "\t\t" + wlan0['hwaddr'] + "\n"
			self.iface = 'wlan0'

		wlan1 = about.getIfConfig('wlan1')
		if 'addr' in wlan1:
			self.AboutText += _("IP:") + "\t\t" + wlan1['addr'] + "\n"
			if 'netmask' in wlan1:
				self.AboutText += _("Netmask:") + "\t\t" + wlan1['netmask'] + "\n"
			if 'hwaddr' in wlan1:
				self.AboutText += _("MAC:") + "\t\t" + wlan1['hwaddr'] + "\n"
			self.iface = 'wlan1'

		rx_bytes, tx_bytes = about.getIfTransferredData(self.iface)
		self.AboutText += "\n" + _("Bytes received:") + "\t" + rx_bytes + "\n"
		self.AboutText += _("Bytes sent:") + "\t\t" + tx_bytes + "\n"

		hostname = open('/proc/sys/kernel/hostname').read()
		self.AboutText += "\n" + _("Hostname:") + "\t\t" + hostname + "\n"
		self["AboutScrollLabel"] = ScrollLabel(self.AboutText)

	def cleanup(self):
		if self.iStatus:
			self.iStatus.stopWlanConsole()

	def resetList(self):
		if self.iStatus:
			self.iStatus.getDataForInterface(self.iface, self.getInfoCB)

	def getInfoCB(self, data, status):
		self.LinkState = None
		if data is not None:
			if data is True:
				if status is not None:
					if self.iface == 'wlan0' or self.iface == 'wlan1' or self.iface == 'ra0':
						if status[self.iface]["essid"] == "off":
							essid = _("No Connection")
						else:
							essid = str(status[self.iface]["essid"])
						if status[self.iface]["accesspoint"] == "Not-Associated":
							accesspoint = _("Not-Associated")
							essid = _("No Connection")
						else:
							accesspoint = str(status[self.iface]["accesspoint"])
						if "BSSID" in self:
							self.AboutText += _('Accesspoint:') + '\t\t' + accesspoint + '\n'
						if "ESSID" in self:
							self.AboutText += _('SSID:') + '\t\t' + essid + '\n'

						quality = str(status[self.iface]["quality"])
						if "quality" in self:
							self.AboutText += _('Link Quality:') + '\t' + quality + '\n'

						if status[self.iface]["bitrate"] == '0':
							bitrate = _("Unsupported")
						else:
							bitrate = str(status[self.iface]["bitrate"]) + " Mb/s"
						if "bitrate" in self:
							self.AboutText += _('Bitrate:') + '\t\t' + bitrate + '\n'

						signal = str(status[self.iface]["signal"])
						if "signal" in self:
							self.AboutText += _('Signal Strength:') + '\t\t' + signal + '\n'

						if status[self.iface]["encryption"] == "off":
							if accesspoint == "Not-Associated":
								encryption = _("Disabled")
							else:
								encryption = _("Unsupported")
						else:
							encryption = _("Enabled")
						if "enc" in self:
							self.AboutText += _('Encryption:') + '\t\t' + encryption + '\n'

						if status[self.iface]["essid"] == "off" or status[self.iface]["accesspoint"] == "Not-Associated" or status[self.iface]["accesspoint"] is False:
							self.LinkState = False
							self["statuspic"].setPixmapNum(1)
							self["statuspic"].show()
						else:
							self.LinkState = True
							iNetwork.checkNetworkState(self.checkNetworkCB)
						self["AboutScrollLabel"].setText(self.AboutText)

	def exit(self):
		self.close(True)

	def updateStatusbar(self):
		self["IFtext"].setText(_("Network:"))
		self["IF"].setText(iNetwork.getFriendlyAdapterName(self.iface))
		self["Statustext"].setText(_("Link:"))
		if iNetwork.isWirelessInterface(self.iface):
			try:
				self.iStatus.getDataForInterface(self.iface, self.getInfoCB)
			except:
				self["statuspic"].setPixmapNum(1)
				self["statuspic"].show()
		else:
			iNetwork.getLinkState(self.iface, self.dataAvail)

	def dataAvail(self, data):
		data = six.ensure_str(data)
		self.LinkState = None
		for line in data.splitlines():
			line = line.strip()
			if 'Link detected:' in line:
				if "yes" in line:
					self.LinkState = True
				else:
					self.LinkState = False
		if self.LinkState:
			iNetwork.checkNetworkState(self.checkNetworkCB)
		else:
			self["statuspic"].setPixmapNum(1)
			self["statuspic"].show()

	def checkNetworkCB(self, data):
		try:
			if iNetwork.getAdapterAttribute(self.iface, "up") is True:
				if self.LinkState is True:
					if data <= 2:
						self["statuspic"].setPixmapNum(0)
					else:
						self["statuspic"].setPixmapNum(1)
					self["statuspic"].show()
				else:
					self["statuspic"].setPixmapNum(1)
					self["statuspic"].show()
			else:
				self["statuspic"].setPixmapNum(1)
				self["statuspic"].show()
		except:
			pass

	def createSummary(self):
		return AboutSummary

class AboutSummary(Screen):
	def __init__(self, session, parent):
		Screen.__init__(self, session, parent = parent)
		self["selected"] = StaticText("HDF:" + getImageVersion())

		AboutText = _("Model: %s %s\n") % (getMachineBrand(), getMachineName())

		if path.exists('/proc/stb/info/chipset'):
			chipset = open('/proc/stb/info/chipset', 'r').read()
			AboutText += _("Chipset: %s") % chipset.replace('\n', '') + "\n"

		AboutText += _("Version: %s") % getImageVersion() + "\n"
		AboutText += _("Build: %s") % getImageVersion() + "\n"
		AboutText += _("Kernel: %s") % about.getKernelVersionString() + "\n"

		string = getDriverDate()
		year = string[0:4]
		month = string[4:6]
		day = string[6:8]
		driversdate = '-'.join((year, month, day))
		AboutText += _("Drivers: %s") % driversdate + "\n"
		AboutText += _("Last update: %s") % getEnigmaVersionString()

		tempinfo = ""
		if path.exists('/proc/stb/sensors/temp0/value'):
			tempinfo = open('/proc/stb/sensors/temp0/value', 'r').read()
		elif path.exists('/proc/stb/fp/temp_sensor'):
			tempinfo = open('/proc/stb/fp/temp_sensor', 'r').read()
		if tempinfo and int(tempinfo.replace('\n', '')) > 0:
			mark = str('\xc2\xb0')
			AboutText += _("Temperature: %s") % tempinfo.replace('\n', '') + mark + "C"

		self["AboutText"] = StaticText(AboutText)

class ViewGitLog(Screen):
	def __init__(self, session, args=None):
		Screen.__init__(self, session)
		self.skinName = "SoftwareUpdateChanges"
		self.setTitle(_("OpenHDF E2 Changes"))
		self.logtype = 'e2'
		self["text"] = ScrollLabel()
		self['title_summary'] = StaticText()
		self['text_summary'] = StaticText()
		self["key_red"] = Button(_("Close"))
		self["key_green"] = Button(_("OK"))
		self["key_yellow"] = Button(_("Last Image Updates"))
		self["myactions"] = ActionMap(['ColorActions', 'OkCancelActions', 'DirectionActions'],
		{
			'cancel': self.closeRecursive,
			'green': self.closeRecursive,
			"red": self.closeRecursive,
			"blue": self.showMemoryInfo,
			"yellow": self.changelogtype,
			"left": self.pageUp,
			"right": self.pageDown,
			"down": self.pageDown,
			"up": self.pageUp
		}, -1)
		self.onLayoutFinish.append(self.getlog)

	def changelogtype(self):
		if self.logtype == 'e2':
			self["key_yellow"].setText(_("Show OE-A Log"))
			self.setTitle(_("Last Image Updates"))
			self.logtype = 'last-upgrades'
		elif self.logtype == 'last-upgrades':
			self["key_yellow"].setText(_("Show OpenHDF Log"))
			self.setTitle(_("OE-A Changes"))
			self.logtype = 'oe'
		elif self.logtype == 'oe':
			self["key_yellow"].setText(_("Show Last Updates"))
			self.setTitle(_("OpenHDF E2 Changes"))
			self.logtype = 'e2'
		self.getlog()

	def pageUp(self):
		self["text"].pageUp()

	def pageDown(self):
		self["text"].pageDown()

	def getlog(self):
		try:
			fd = open('/etc/' + self.logtype + '-git.log', 'r')
			releasenotes = fd.read()
			fd.close()
			releasenotes = releasenotes.replace('\nopenvix: build', "\n\n")
			self["text"].setText(releasenotes)
			summarytext = releasenotes
		except:
			print("there is a problem with reading log file")
		try:
			self['title_summary'].setText(summarytext[0] + ':')
			self['text_summary'].setText(summarytext[1])
		except:
			self['title_summary'].setText("")
			self['text_summary'].setText("")

	def showMemoryInfo(self):
		self.session.open(MemoryInfo)

	def unattendedupdate(self):
		self.close((_("Unattended upgrade without GUI and reboot system"), "cold"))

	def closeRecursive(self):
		self.close((_("Cancel"), ""))

class TranslationInfo(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		Screen.setTitle(self, _("Translation Information"))
		# don't remove the string out of the _(), or it can't be "translated" anymore.

		# TRANSLATORS: Add here whatever should be shown in the "translator" about screen, up to 6 lines (use \n for newline)
		info = _("TRANSLATOR_INFO")

		if info == "TRANSLATOR_INFO":
			info = ""

		infolines = _("").split("\n")
		infomap = {}
		for x in infolines:
			l = x.split(': ')
			if len(l) != 2:
				continue
			(type, value) = l
			infomap[type] = value
		print(infomap)

		self["TranslationInfo"] = StaticText(info)

		translator_name = infomap.get("Language-Team", "none")
		if translator_name == "none":
			translator_name = infomap.get("Last-Translator", "")

		self["TranslatorName"] = StaticText(translator_name)

		self["actions"] = ActionMap(["SetupActions"],
			{
				"cancel": self.close,
				"ok": self.close,
			})

class MemoryInfo(Screen):

	skin = """<screen name="MemoryInfo" position="center,60" zPosition="2" size="540,490" title="Memory Info">
			<ePixmap pixmap="skin_default/buttons/red.png" position="0,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/green.png" position="135,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/yellow.png" position="270,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/blue.png" position="405,0" size="140,40" alphatest="on" />
			<widget name="key_red" position="0,0" zPosition="1" size="135,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
			<widget name="key_green" position="135,0" zPosition="1" size="135,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
			<widget name="key_blue" position="405,0" zPosition="1" size="135,40" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" transparent="1" />

			<widget name="lmemtext" position="10,40" size="120,450" font="Regular;16" zPosition="1" halign="left" transparent="1" />
			<widget name="lmemvalue" position="120,40" size="90,450" font="Regular;16" zPosition="1" halign="right" transparent="1" />
			<widget name="rmemtext" position="330,40" size="120,450" font="Regular;16" zPosition="1" halign="left" transparent="1" />
			<widget name="rmemvalue" position="440,40" size="90,450" font="Regular;16" zPosition="1" halign="right" transparent="1" />

			<widget name="info" position="330,405" size="200,100" font="Regular;14" zPosition="1" halign="center" foregroundColor="#909090" transparent="1" />
		</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)

		self["actions"] = ActionMap(["SetupActions", "ColorActions"],
			{
				"cancel": self.close,
				"ok": self.getMemoryInfo,
				"green": self.getMemoryInfo,
				"blue": self.clearMemory,
			})

		self["key_red"] = Label(_("Cancel"))
		self["key_green"] = Label(_("Refresh"))
		self["key_blue"] = Label(_("Clear"))

		self['lmemtext'] = Label()
		self['lmemvalue'] = Label()
		self['rmemtext'] = Label()
		self['rmemvalue'] = Label()

		self['pfree'] = Label()
		self['pused'] = Label()
		self["slide"] = ProgressBar()
		self["slide"].setValue(100)

		self['info'] = Label(_("This info is for developers only.\nFor a normal users it is not important."))

		self.setTitle(_("Memory Info"))
		self.onLayoutFinish.append(self.getMemoryInfo)

	def getMemoryInfo(self):
		try:
			ltext = rtext = ""
			lvalue = rvalue = ""
			mem = 0
			free = 0
			i = 0
			for line in open('/proc/meminfo', 'r'):
				( name, size, units ) = line.strip().split()
				if name.find("MemTotal") != -1:
					mem = int(size)
				if name.find("MemFree") != -1:
					free = int(size)
				if i < 28:
					ltext += "".join((name, "\n"))
					lvalue += "".join((size, " ", units, "\n"))
				else:
					rtext += "".join((name, "\n"))
					rvalue += "".join((size, " ", units, "\n"))
				i += 1
			self['lmemtext'].setText(ltext)
			self['lmemvalue'].setText(lvalue)
			self['rmemtext'].setText(rtext)
			self['rmemvalue'].setText(rvalue)

			self["slide"].setValue(int(100.0*(mem-free)//mem+0.25))
			self['pfree'].setText("%.1f %s" % (100.*free//mem, '%'))
			self['pused'].setText("%.1f %s" % (100.*(mem-free)//mem, '%'))

		except Exception as e:
			print("[About] getMemoryInfo FAIL:", e)

	def clearMemory(self):
		from os import system
		system("sync")
		system("echo 3 > /proc/sys/vm/drop_caches")
		self.getMemoryInfo()
