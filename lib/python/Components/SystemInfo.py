import re
from os import path as os_path

from boxbranding import (getBoxType, getBrandOEM, getDisplayType,
                         getHaveAVJACK, getHaveCI, getHaveDVI, getHaveHDMI,
                         getHaveHDMIinFHD, getHaveHDMIinHD, getHaveMiniTV,
                         getHaveRCA, getHaveSCART, getHaveSCARTYUV,
                         getHaveTranscoding2, getHaveWOL, getHaveWWOL,
                         getHaveYUV, getMachineBuild, getMachineMtdRoot)
from enigma import Misc_Options, eDVBResourceManager

from Tools.Directories import (SCOPE_SKIN, fileCheck, fileExists, fileHas,
                               isPluginInstalled, pathExists, resolveFilename)
from hashlib import md5
from Tools.HardwareInfo import HardwareInfo
from types import MappingProxyType
from ast import literal_eval

SystemInfo = {}
BoxInfo.setItem("HasRootSubdir", False)	# This needs to be here so it can be reset by getMultibootslots!
BoxInfo.setItem("RecoveryMode", False or fileCheck("/proc/stb/fp/boot_mode"))	# This needs to be here so it can be reset by getMultibootslots!
from Tools.Multiboot import (  # This import needs to be here to avoid a SystemInfo load loop!
    getMBbootdevice, getMultibootslots)

#FIXMEE...


class immutableDict(dict):
	def __init__(self, *args, **kws):
		self.immutablelist = []
		self.checkimmutable = False
		dict.__init__(self, *args, **kws)

	def setImmutable(self):
		self.checkimmutable = True

	def __hash__(self):
		return id(self)

	def _immutable(self, *args, **kws):
		raise TypeError('object is immutable')

	def __setitem__(self, key, value):
		if self.checkimmutable and key in self.immutablelist:
			self._immutable()
		if not self.checkimmutable and key not in self.immutablelist:
			self.immutablelist.append(key)
		dict.__setitem__(self, key, value)

	def __delitem__(self, key):
		if self.checkimmutable and key in self.immutablelist:
			self._immutable()
		else:
			dict.__delitem__(self, key)

	clear = _immutable
	update = _immutable
	setdefault = _immutable
	pop = _immutable
	popitem = _immutable


class BoxInformation:
	def __init__(self, root=""):
		self.boxInfo = immutableDict({"machine": "default", "checksum": None}) #add one key to the boxInfoCollector as it always should exist to satisfy the CI test on github and predefine checksum
		checksumcollectionstring = ""
		file = root + "/usr/lib/enigma.info"
		if fileExists(file):
			for line in open(file, 'r').readlines():
				if line.startswith("checksum="):
					self.boxInfo["checksum"] = md5(bytearray(checksumcollectionstring, "UTF-8", errors="ignore")).hexdigest() == line.strip().split('=')[1]
					break
				checksumcollectionstring += line
				if line.startswith("#") or line.strip() == "":
					continue
				if '=' in line:
					item, value = line.split('=', 1)
					self.boxInfo[item.strip()] = self.processValue(value.strip())
			if self.boxInfo["checksum"]:
				print("[SystemInfo] Enigma information file data loaded into BoxInfo.")
			else:
				print("[SystemInfo] Enigma information file data loaded, but checksum failed.")
		else:
			print("[SystemInfo] ERROR: %s is not available!  The system is unlikely to boot or operate correctly." % file)
		self.boxInfo.setImmutable() #make what is derived from enigma.info immutable

	def processValue(self, value):
		try:
			return literal_eval(value)
		except:
			return value

	def getEnigmaInfoList(self):
		return sorted(self.boxInfo.immutablelist)

	def getEnigmaConfList(self):  # not used by us
		return []

	def getItemsList(self):
		return sorted(self.boxInfo.keys())

	def getItem(self, item, default=None):
		return self.boxInfo.get(item, default)

	def setItem(self, item, value, *args, **kws):
		self.boxInfo[item] = value
		return True

	def deleteItem(self, item, *args, **kws):
		del self.boxInfo[item]
		return True


BoxInfo = BoxInformation()


# Parse the boot commandline.
#
with open("/proc/cmdline", "r") as fd:
    cmdline = fd.read()
cmdline = {k: v.strip('"') for k, v in re.findall(r'(\S+)=(".*?"|\S+)', cmdline)}

def getNumVideoDecoders():
	idx = 0
	while fileExists("/dev/dvb/adapter0/video%d" % idx, 'f'):
		idx += 1
	return idx


BoxInfo.setItem("NumVideoDecoders", getNumVideoDecoders())
BoxInfo.setItem("PIPAvailable", BoxInfo.getItem("NumVideoDecoders") > 1)
BoxInfo.setItem("CanMeasureFrontendInputPower", eDVBResourceManager.getInstance().canMeasureFrontendInputPower())


def countFrontpanelLEDs():
	leds = 0
	if fileExists("/proc/stb/fp/led_set_pattern"):
		leds += 1

	while fileExists("/proc/stb/fp/led%d_pattern" % leds):
		leds += 1

	return leds


def setBoxInfoItems():
	model = getBoxType()
	#BoxInfo.setItem("canMode12", "_4.boxmode" % model in cmdline and cmdline["_4.boxmode" % model] in ("1", "12") and "192M")
	#BoxInfo.setItem("canMode12", fileHas("/proc/cmdline", "_4.boxmode=1 ") and '192M' or fileHas("/proc/cmdline", "_4.boxmode=12") and '192M')
	BoxInfo.setItem("canMode12", getMachineBuild() in ("hd51", "vs1500", "h7") and ("brcm_cma=440M@328M brcm_cma=192M@768M", "brcm_cma=520M@248M brcm_cma=200M@768M"))
	BoxInfo.setItem("12V_Output", Misc_Options.getInstance().detected_12V_output())
	BoxInfo.setItem("ZapMode", fileCheck("/proc/stb/video/zapmode") or fileCheck("/proc/stb/video/zapping_mode"))
	BoxInfo.setItem("NumFrontpanelLEDs", countFrontpanelLEDs())
	BoxInfo.setItem("FrontpanelDisplay", fileExists("/dev/dbox/oled0") or fileExists("/dev/dbox/lcd0"))
	BoxInfo.setItem("OledDisplay", fileExists("/dev/dbox/oled0") or fileExists(resolveFilename(SCOPE_SKIN, 'display/lcd_skin/skin_display.xml')) or fileExists(resolveFilename(SCOPE_SKIN, 'vfd_skin/skin_display_no_picon.xml')) or getBoxType() in ('osminiplus'))
	BoxInfo.setItem("LcdDisplay", fileExists("/dev/dbox/lcd0"))
	BoxInfo.setItem("DeepstandbySupport", HardwareInfo().has_deepstandby())
	BoxInfo.setItem("Fan", fileExists("/proc/stb/fp/fan"))
	BoxInfo.setItem("FanPWM", BoxInfo.getItem("Fan") and fileExists("/proc/stb/fp/fan_pwm"))
	BoxInfo.setItem("PowerLed", fileExists("/proc/stb/power/powerled"))
	BoxInfo.setItem("PowerLed2", fileExists("/proc/stb/power/powerled2"))
	BoxInfo.setItem("StandbyLED", fileExists("/proc/stb/power/standbyled"))
	BoxInfo.setItem("StandbyPowerLed", fileExists("/proc/stb/power/standbyled"))
	BoxInfo.setItem("SuspendPowerLed", fileExists("/proc/stb/power/suspendled"))
	BoxInfo.setItem("LedPowerColor", fileExists("/proc/stb/fp/ledpowercolor"))
	BoxInfo.setItem("LedStandbyColor", fileExists("/proc/stb/fp/ledstandbycolor"))
	BoxInfo.setItem("LedSuspendColor", fileExists("/proc/stb/fp/ledsuspendledcolor"))
	BoxInfo.setItem("Power4x7On", fileExists("/proc/stb/fp/power4x7on"))
	BoxInfo.setItem("Power4x7Standby", fileExists("/proc/stb/fp/power4x7standby"))
	BoxInfo.setItem("Power4x7Suspend", fileExists("/proc/stb/fp/power4x7suspend"))
	BoxInfo.setItem("FBLCDDisplay", fileCheck("/proc/stb/fb/sd_detach"))
	BoxInfo.setItem("lxbuttons", getBrandOEM() == "ini")
	BoxInfo.setItem("homebutton", getBoxType().startswith('ixuss'))
	BoxInfo.setItem("endbutton", getBoxType().startswith('ixuss'))
	BoxInfo.setItem("3FunctionButtons", getBoxType() == "et8000" or getBoxType() == "et6x00" or getBoxType() == "et10000" or getBoxType().startswith('gb'))
	BoxInfo.setItem("4FunctionButtons", getBoxType().startswith('gb'))
	BoxInfo.setItem("WakeOnLAN", fileCheck("/proc/stb/fp/wol") or fileCheck("/proc/stb/power/wol"))
	BoxInfo.setItem("HDMICEC", (fileExists("/dev/hdmi_cec") or fileExists("/dev/misc/hdmi_cec0")) and isPluginInstalled("HdmiCEC"))
	BoxInfo.setItem("SABSetup", isPluginInstalled("SABnzbd"))
	BoxInfo.setItem("SeekStatePlay", False)
	BoxInfo.setItem("StatePlayPause", False)
	BoxInfo.setItem("StandbyState", False)
	BoxInfo.setItem("GraphicLCD", getBoxType() in ('vuultimo', 'xpeedlx3', 'et10000', 'mutant2400', 'quadbox2400', 'sezammarvel', 'atemionemesis', 'mbultra', 'beyonwizt4'))
	BoxInfo.setItem("Blindscan", isPluginInstalled("Blindscan"))
	BoxInfo.setItem("Satfinder", isPluginInstalled("Satfinder"))
	BoxInfo.setItem("HasExternalPIP", getMachineBuild() not in ('et9x00', 'et6x00', 'et5x00') and fileCheck("/proc/stb/vmpeg/1/external"))
	BoxInfo.setItem("hasPIPVisibleProc", fileCheck("/proc/stb/vmpeg/1/visible"))
	BoxInfo.setItem("VideoDestinationConfigurable", fileExists("/proc/stb/vmpeg/0/dst_left"))
	BoxInfo.setItem("GBWOL", fileExists("/usr/bin/gigablue_wol"))
	BoxInfo.setItem("LCDSKINSetup", os_path.exists("/usr/share/enigma2/display"))
	BoxInfo.setItem("7segment", getDisplayType() in ('7segment'))
	BoxInfo.setItem("CIHelper", fileExists("/usr/bin/cihelper"))
	BoxInfo.setItem("3DMode", fileCheck("/proc/stb/fb/3dmode") or fileCheck("/proc/stb/fb/primary/3d"))
	BoxInfo.setItem("3DZNorm", fileCheck("/proc/stb/fb/znorm") or fileCheck("/proc/stb/fb/primary/zoffset"))
	BoxInfo.setItem("RcTypeChangable", not (getBoxType().startswith("et8500") or getBoxType().startswith("et7")) and pathExists("/proc/stb/ir/rc/type"))
	BoxInfo.setItem("CanUse3DModeChoices", fileExists('/proc/stb/fb/3dmode_choices') and True or False)
	BoxInfo.setItem("need_dsw", getBoxType() not in ('osminiplus', 'osmega'))
	BoxInfo.setItem("HaveCISSL", fileCheck("/etc/ssl/certs/customer.pem") and fileCheck("/etc/ssl/certs/device.pem"))
	BoxInfo.setItem("HasMultichannelPCM", fileCheck("/proc/stb/audio/multichannel_pcm"))
	BoxInfo.setItem("HaveTouchSensor", getBoxType() in ('dm520', 'dm525', 'dm900'))
	BoxInfo.setItem("DefaultDisplayBrightness", getBoxType() == 'dm900' and 8 or 5)
	BoxInfo.setItem("LCDMiniTV", fileExists("/proc/stb/lcd/mode"))
	BoxInfo.setItem("LcdLiveTV", fileCheck("/proc/stb/fb/sd_detach"))
	BoxInfo.setItem("MiniTV", fileCheck("/proc/stb/fb/sd_detach") or fileCheck("/proc/stb/lcd/live_enable"))
	BoxInfo.setItem("FastChannelChange", False)
	BoxInfo.setItem("LCDMiniTVPiP", BoxInfo.getItem("LCDMiniTV") and getBoxType() not in ('gb800ueplus', 'gbquad4k', 'gbue4k'))
	BoxInfo.setItem("LCDsymbol_circle", fileCheck("/proc/stb/lcd/symbol_circle"))
	BoxInfo.setItem("ForceLNBPowerChanged", fileCheck("/proc/stb/frontend/fbc/force_lnbon"))
	BoxInfo.setItem("ForceToneBurstChanged", fileCheck("/proc/stb/frontend/fbc/force_toneburst"))
	BoxInfo.setItem("USETunersetup", BoxInfo.getItem("ForceLNBPowerChanged") or BoxInfo.getItem("ForceToneBurstChanged"))
	BoxInfo.setItem("HDMIin", getHaveHDMIinHD() or getHaveHDMIinFHD())
	BoxInfo.setItem("HDMIinFHD", getHaveHDMIinFHD())
	BoxInfo.setItem("HaveRCA", getHaveRCA())
	BoxInfo.setItem("HaveDVI", getHaveDVI())
	BoxInfo.setItem("HaveAVJACK", getHaveAVJACK())
	BoxInfo.setItem("HaveSCART", getHaveSCART())
	BoxInfo.setItem("HaveSCARTYUV", getHaveSCARTYUV())
	BoxInfo.setItem("HaveYUV", getHaveYUV())
	BoxInfo.setItem("HaveHDMI", getHaveHDMI())
	BoxInfo.setItem("HaveMiniTV", getHaveMiniTV())
	BoxInfo.setItem("HaveWOL", getHaveWOL())
	BoxInfo.setItem("HaveWWOL", getHaveWWOL())
	BoxInfo.setItem("HaveTranscoding2", getHaveTranscoding2())
	BoxInfo.setItem("HaveCI", getHaveCI())
	BoxInfo.setItem("HaveMultiBoot", (fileCheck("/boot/STARTUP") or fileCheck("/boot/cmdline.txt")))
	BoxInfo.setItem("HaveMultiBootHD", fileCheck("/boot/STARTUP") and getMachineBuild() in ('hd51', 'vs1500', 'h7', 'ceryon7252'))
	BoxInfo.setItem("HaveMultiBootXC", fileCheck("/boot/cmdline.txt"))
	BoxInfo.setItem("HaveMultiBootGB", fileCheck("/boot/STARTUP") and getMachineBuild() in ('gb7252'))
	BoxInfo.setItem("HaveMultiBootCY", fileCheck("/boot/STARTUP") and getMachineBuild() in ('8100s'))
	BoxInfo.setItem("HaveMultiBootOS", fileCheck("/boot/STARTUP") and getMachineBuild() in ('osmio4k', 'osmio4kplus', 'osmini4k'))
	BoxInfo.setItem("HaveMultiBootDS", fileCheck("/boot/STARTUP") and getMachineBuild() in ('cc1', 'sf8008', 'sf8008s', 'sf8008t', 'ustym4kpro', 'viper4k') and fileCheck("/dev/sda"))
	BoxInfo.setItem("HasMMC", fileHas("/proc/cmdline", "root=/dev/mmcblk") or "mmcblk" in getMachineMtdRoot())
	BoxInfo.setItem("CanProc", BoxInfo.getItem("HasMMC") and getBrandOEM() != "vuplus")
	BoxInfo.setItem("HasHiSi", pathExists("/proc/hisi"))
	BoxInfo.setItem("MBbootdevice", getMBbootdevice())
	BoxInfo.setItem("canMultiBoot", getMultibootslots())
	BoxInfo.setItem("HAScmdline", fileCheck("/boot/cmdline.txt"))
	BoxInfo.setItem("HasMMC", fileHas("/proc/cmdline", "root=/dev/mmcblk") or BoxInfo.getItem("canMultiBoot") and fileHas("/proc/cmdline", "root=/dev/sda"))
	BoxInfo.setItem("HasSDmmc", BoxInfo.getItem("canMultiBoot") and "sd" in BoxInfo.getItem("canMultiBoot")[2] and "mmcblk" in getMachineMtdRoot())
	BoxInfo.setItem("HasSDswap", getMachineBuild() in ("h9", "i55plus") and pathExists("/dev/mmcblk0p1"))
	BoxInfo.setItem("HasFullHDSkinSupport", getBoxType() not in ("et4000", "et5000", "sh1", "hd500c", "hd1100", "xp1000", "lc"))
	BoxInfo.setItem("CanProc", BoxInfo.getItem("HasMMC") and getBrandOEM() != "vuplus")
	BoxInfo.setItem("canRecovery", getMachineBuild() in ("hd51", "vs1500", "h7", "8100s") and ("disk.img", "mmcblk0p1") or getMachineBuild() in ("xc7439", "osmio4k", "osmio4kplus", "osmini4k") and ("emmc.img", "mmcblk1p1") or getMachineBuild() in ("gbmv200", "cc1", "sf8008", "sf8008m", "sx988", "ip8", "ustym4kpro", "beyonwizv2", "viper4k", "sx88v2") and ("usb_update.bin", "none"))


setBoxInfoItems()
