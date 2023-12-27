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

SystemInfo = {}
SystemInfo["HasRootSubdir"] = False	# This needs to be here so it can be reset by getMultibootslots!
SystemInfo["RecoveryMode"] = False or fileCheck("/proc/stb/fp/boot_mode")	# This needs to be here so it can be reset by getMultibootslots!
from Tools.Multiboot import (  # This import needs to be here to avoid a SystemInfo load loop!
    getMBbootdevice, getMultibootslots)

#FIXMEE...


class BoxInformation:
	def __init__(self, root=""):
		boxInfoCollector = {}
		self.boxInfoMutable = {}
		boxInfoCollector["checksum"] = None
		checksumcollectionstring = ""
		file = root + "/usr/lib/enigma.info"
		if fileExists(file):
			for line in open(file, 'r').readlines():
				if line.startswith("checksum="):
					boxInfoCollector["checksum"] = md5(bytearray(checksumcollectionstring, "UTF-8", errors="ignore")).hexdigest() == line.strip().split('=')[1]
					break
				checksumcollectionstring += line
				if line.startswith("#") or line.strip() == "":
					continue
				if '=' in line:
					item, value = [x.strip() for x in line.split('=')]
					boxInfoCollector[item] = self.processValue(value)
			if boxInfoCollector["checksum"]:
				print("[SystemInfo] Enigma information file data loaded into BoxInfo.")
			else:
				print("[SystemInfo] Enigma information file data loaded, but checksum failed.")
		else:
			print("[SystemInfo] ERROR: %s is not available!  The system is unlikely to boot or operate correctly." % file)
		self.boxInfo = MappingProxyType(boxInfoCollector)

	def processValue(self, value):
		if value and value[0] in ("\"", "'") and value[-1] == value[0]:
			return value[1:-1]
		elif value.upper() == "NONE":
			return None
		elif value.upper() in ("FALSE", "NO", "OFF", "DISABLED"):
			return False
		elif value.upper() in ("TRUE", "YES", "ON", "ENABLED"):
			return True
		else:
			try:
				return eval(value)
			except:
				return value

	def getEnigmaInfoList(self):
		return sorted(self.boxInfo.keys())

	def getEnigmaConfList(self):  # not used by us
		return []

	def getItemsList(self):
		return sorted({**self.boxInfo, **self.boxInfoMutable}.keys())

	def getItem(self, item, default=None):
		if item in self.boxInfo:
			return self.boxInfo[item]
		elif item in self.boxInfoMutable:
			return self.boxInfoMutable[item]
		elif item in SystemInfo:
			return SystemInfo[item]
		return default

	def setItem(self, item, value, immutable=False, forceOverride=False):
		print('*', item, value, immutable, forceOverride)
		if item in self.boxInfo and not forceOverride:
			print("[BoxInfo] Error: Item '%s' is immutable and can not be %s!" % (item, "changed" if item in self.boxInfo else "added"))
			return False
		if immutable:
			boxInfoCollector = dict(self.boxInfo)
			boxInfoCollector[item] = value
			self.boxInfo = MappingProxyType(boxInfoCollector)
		else:
			self.boxInfoMutable[item] = value
		return True

	def deleteItem(self, item, forceOverride=False):
		if item in self.boxInfo:
			if forceOverride:
				boxInfoCollector = dict(self.boxInfo)
				del boxInfoCollector[item]
				self.boxInfo = MappingProxyType(boxInfoCollector)
				return True
			else:
				print("[BoxInfo] Error: Item '%s' is immutable and can not be deleted!" % item)
		if item in self.boxInfoMutable:
			del self.boxInfoMutable[item]
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


SystemInfo["NumVideoDecoders"] = getNumVideoDecoders()
SystemInfo["PIPAvailable"] = SystemInfo["NumVideoDecoders"] > 1
SystemInfo["CanMeasureFrontendInputPower"] = eDVBResourceManager.getInstance().canMeasureFrontendInputPower()


def countFrontpanelLEDs():
	leds = 0
	if fileExists("/proc/stb/fp/led_set_pattern"):
		leds += 1

	while fileExists("/proc/stb/fp/led%d_pattern" % leds):
		leds += 1

	return leds


model = getBoxType()
#SystemInfo["canMode12"] = "_4.boxmode" % model in cmdline and cmdline["_4.boxmode" % model] in ("1", "12") and "192M"
#SystemInfo["canMode12"] = fileHas("/proc/cmdline", "_4.boxmode=1 ") and '192M' or fileHas("/proc/cmdline", "_4.boxmode=12") and '192M'
SystemInfo["canMode12"] = getMachineBuild() in ("hd51", "vs1500", "h7") and ("brcm_cma=440M@328M brcm_cma=192M@768M", "brcm_cma=520M@248M brcm_cma=200M@768M")
SystemInfo["12V_Output"] = Misc_Options.getInstance().detected_12V_output()
SystemInfo["ZapMode"] = fileCheck("/proc/stb/video/zapmode") or fileCheck("/proc/stb/video/zapping_mode")
SystemInfo["NumFrontpanelLEDs"] = countFrontpanelLEDs()
SystemInfo["FrontpanelDisplay"] = fileExists("/dev/dbox/oled0") or fileExists("/dev/dbox/lcd0")
SystemInfo["OledDisplay"] = fileExists("/dev/dbox/oled0") or fileExists(resolveFilename(SCOPE_SKIN, 'display/lcd_skin/skin_display.xml')) or fileExists(resolveFilename(SCOPE_SKIN, 'vfd_skin/skin_display_no_picon.xml')) or getBoxType() in ('osminiplus')
SystemInfo["LcdDisplay"] = fileExists("/dev/dbox/lcd0")
SystemInfo["DeepstandbySupport"] = HardwareInfo().has_deepstandby()
SystemInfo["Fan"] = fileExists("/proc/stb/fp/fan")
SystemInfo["FanPWM"] = SystemInfo["Fan"] and fileExists("/proc/stb/fp/fan_pwm")
SystemInfo["PowerLed"] = fileExists("/proc/stb/power/powerled")
SystemInfo["PowerLed2"] = fileExists("/proc/stb/power/powerled2")
SystemInfo["StandbyLED"] = fileExists("/proc/stb/power/standbyled")
SystemInfo["StandbyPowerLed"] = fileExists("/proc/stb/power/standbyled")
SystemInfo["SuspendPowerLed"] = fileExists("/proc/stb/power/suspendled")
SystemInfo["LedPowerColor"] = fileExists("/proc/stb/fp/ledpowercolor")
SystemInfo["LedStandbyColor"] = fileExists("/proc/stb/fp/ledstandbycolor")
SystemInfo["LedSuspendColor"] = fileExists("/proc/stb/fp/ledsuspendledcolor")
SystemInfo["Power4x7On"] = fileExists("/proc/stb/fp/power4x7on")
SystemInfo["Power4x7Standby"] = fileExists("/proc/stb/fp/power4x7standby")
SystemInfo["Power4x7Suspend"] = fileExists("/proc/stb/fp/power4x7suspend")
SystemInfo["FBLCDDisplay"] = fileCheck("/proc/stb/fb/sd_detach")
SystemInfo["lxbuttons"] = getBrandOEM() == "ini"
SystemInfo["homebutton"] = getBoxType().startswith('ixuss')
SystemInfo["endbutton"] = getBoxType().startswith('ixuss')
SystemInfo["3FunctionButtons"] = getBoxType() == "et8000" or getBoxType() == "et6x00" or getBoxType() == "et10000" or getBoxType().startswith('gb')
SystemInfo["4FunctionButtons"] = getBoxType().startswith('gb')
SystemInfo["WakeOnLAN"] = fileCheck("/proc/stb/fp/wol") or fileCheck("/proc/stb/power/wol")
SystemInfo["HDMICEC"] = (fileExists("/dev/hdmi_cec") or fileExists("/dev/misc/hdmi_cec0")) and isPluginInstalled("HdmiCEC")
SystemInfo["SABSetup"] = isPluginInstalled("SABnzbd")
SystemInfo["SeekStatePlay"] = False
SystemInfo["StatePlayPause"] = False
SystemInfo["StandbyState"] = False
SystemInfo["GraphicLCD"] = getBoxType() in ('vuultimo', 'xpeedlx3', 'et10000', 'mutant2400', 'quadbox2400', 'sezammarvel', 'atemionemesis', 'mbultra', 'beyonwizt4')
SystemInfo["Blindscan"] = isPluginInstalled("Blindscan")
SystemInfo["Satfinder"] = isPluginInstalled("Satfinder")
SystemInfo["HasExternalPIP"] = getMachineBuild() not in ('et9x00', 'et6x00', 'et5x00') and fileCheck("/proc/stb/vmpeg/1/external")
SystemInfo["hasPIPVisibleProc"] = fileCheck("/proc/stb/vmpeg/1/visible")
SystemInfo["VideoDestinationConfigurable"] = fileExists("/proc/stb/vmpeg/0/dst_left")
SystemInfo["GBWOL"] = fileExists("/usr/bin/gigablue_wol")
SystemInfo["LCDSKINSetup"] = os_path.exists("/usr/share/enigma2/display")
SystemInfo["7segment"] = getDisplayType() in ('7segment')
SystemInfo["CIHelper"] = fileExists("/usr/bin/cihelper")
SystemInfo["3DMode"] = fileCheck("/proc/stb/fb/3dmode") or fileCheck("/proc/stb/fb/primary/3d")
SystemInfo["3DZNorm"] = fileCheck("/proc/stb/fb/znorm") or fileCheck("/proc/stb/fb/primary/zoffset")
SystemInfo["RcTypeChangable"] = not (getBoxType().startswith("et8500") or getBoxType().startswith("et7")) and pathExists("/proc/stb/ir/rc/type")
SystemInfo["CanUse3DModeChoices"] = fileExists('/proc/stb/fb/3dmode_choices') and True or False
SystemInfo["need_dsw"] = getBoxType() not in ('osminiplus', 'osmega')
SystemInfo["HaveCISSL"] = fileCheck("/etc/ssl/certs/customer.pem") and fileCheck("/etc/ssl/certs/device.pem")
SystemInfo["HasMultichannelPCM"] = fileCheck("/proc/stb/audio/multichannel_pcm")
SystemInfo["HaveTouchSensor"] = getBoxType() in ('dm520', 'dm525', 'dm900')
SystemInfo["DefaultDisplayBrightness"] = getBoxType() == 'dm900' and 8 or 5
SystemInfo["LCDMiniTV"] = fileExists("/proc/stb/lcd/mode")
SystemInfo["LcdLiveTV"] = fileCheck("/proc/stb/fb/sd_detach")
SystemInfo["MiniTV"] = fileCheck("/proc/stb/fb/sd_detach") or fileCheck("/proc/stb/lcd/live_enable")
SystemInfo["FastChannelChange"] = False
SystemInfo["LCDMiniTVPiP"] = SystemInfo["LCDMiniTV"] and getBoxType() not in ('gb800ueplus', 'gbquad4k', 'gbue4k')
SystemInfo["LCDsymbol_circle"] = fileCheck("/proc/stb/lcd/symbol_circle")
SystemInfo["ForceLNBPowerChanged"] = fileCheck("/proc/stb/frontend/fbc/force_lnbon")
SystemInfo["ForceToneBurstChanged"] = fileCheck("/proc/stb/frontend/fbc/force_toneburst")
SystemInfo["USETunersetup"] = SystemInfo["ForceLNBPowerChanged"] or SystemInfo["ForceToneBurstChanged"]
SystemInfo["HDMIin"] = getHaveHDMIinHD() or getHaveHDMIinFHD()
SystemInfo["HDMIinFHD"] = getHaveHDMIinFHD()
SystemInfo["HaveRCA"] = getHaveRCA()
SystemInfo["HaveDVI"] = getHaveDVI()
SystemInfo["HaveAVJACK"] = getHaveAVJACK()
SystemInfo["HaveSCART"] = getHaveSCART()
SystemInfo["HaveSCARTYUV"] = getHaveSCARTYUV()
SystemInfo["HaveYUV"] = getHaveYUV()
SystemInfo["HaveHDMI"] = getHaveHDMI()
SystemInfo["HaveMiniTV"] = getHaveMiniTV()
SystemInfo["HaveWOL"] = getHaveWOL()
SystemInfo["HaveWWOL"] = getHaveWWOL()
SystemInfo["HaveTranscoding2"] = getHaveTranscoding2()
SystemInfo["HaveCI"] = getHaveCI()
SystemInfo["HaveMultiBoot"] = (fileCheck("/boot/STARTUP") or fileCheck("/boot/cmdline.txt"))
SystemInfo["HaveMultiBootHD"] = fileCheck("/boot/STARTUP") and getMachineBuild() in ('hd51', 'vs1500', 'h7', 'ceryon7252')
SystemInfo["HaveMultiBootXC"] = fileCheck("/boot/cmdline.txt")
SystemInfo["HaveMultiBootGB"] = fileCheck("/boot/STARTUP") and getMachineBuild() in ('gb7252')
SystemInfo["HaveMultiBootCY"] = fileCheck("/boot/STARTUP") and getMachineBuild() in ('8100s')
SystemInfo["HaveMultiBootOS"] = fileCheck("/boot/STARTUP") and getMachineBuild() in ('osmio4k', 'osmio4kplus', 'osmini4k')
SystemInfo["HaveMultiBootDS"] = fileCheck("/boot/STARTUP") and getMachineBuild() in ('cc1', 'sf8008', 'sf8008s', 'sf8008t', 'ustym4kpro', 'viper4k') and fileCheck("/dev/sda")
SystemInfo["HasMMC"] = fileHas("/proc/cmdline", "root=/dev/mmcblk") or "mmcblk" in getMachineMtdRoot()
SystemInfo["CanProc"] = SystemInfo["HasMMC"] and getBrandOEM() != "vuplus"
SystemInfo["HasHiSi"] = pathExists("/proc/hisi")
SystemInfo["MBbootdevice"] = getMBbootdevice()
SystemInfo["canMultiBoot"] = getMultibootslots()
SystemInfo["HAScmdline"] = fileCheck("/boot/cmdline.txt")
SystemInfo["HasMMC"] = fileHas("/proc/cmdline", "root=/dev/mmcblk") or SystemInfo["canMultiBoot"] and fileHas("/proc/cmdline", "root=/dev/sda")
SystemInfo["HasSDmmc"] = SystemInfo["canMultiBoot"] and "sd" in SystemInfo["canMultiBoot"][2] and "mmcblk" in getMachineMtdRoot()
SystemInfo["HasSDswap"] = getMachineBuild() in ("h9", "i55plus") and pathExists("/dev/mmcblk0p1")
SystemInfo["HasFullHDSkinSupport"] = getBoxType() not in ("et4000", "et5000", "sh1", "hd500c", "hd1100", "xp1000", "lc")
SystemInfo["CanProc"] = SystemInfo["HasMMC"] and getBrandOEM() != "vuplus"
SystemInfo["canRecovery"] = getMachineBuild() in ("hd51", "vs1500", "h7", "8100s") and ("disk.img", "mmcblk0p1") or getMachineBuild() in ("xc7439", "osmio4k", "osmio4kplus", "osmini4k") and ("emmc.img", "mmcblk1p1") or getMachineBuild() in ("gbmv200", "cc1", "sf8008", "sf8008m", "sx988", "ip8", "ustym4kpro", "beyonwizv2", "viper4k", "sx88v2") and ("usb_update.bin", "none")
