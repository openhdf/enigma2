from __future__ import absolute_import
from os import path, listdir
from enigma import eDVBResourceManager, Misc_Options
from Tools.Directories import fileExists, fileCheck, resolveFilename, SCOPE_SKIN, fileHas, pathExists
from Tools.HardwareInfo import HardwareInfo
from boxbranding import getBoxType, getBrandOEM, getDisplayType, getHaveAVJACK, getHaveDVI, getHaveHDMI, getHaveRCA, getHaveSCART, getHaveSCARTYUV, getHaveYUV, getMachineBuild, getMachineMtdRoot, getMachineMtdKernel, getHaveHDMIinHD, getHaveMiniTV, getHaveHDMIinFHD, getHaveWOL, getHaveWWOL, getHaveCI, getHaveTranscoding2, getHaveCI

SystemInfo = {}
SystemInfo["HasRootSubdir"] = False	# This needs to be here so it can be reset by getMultibootslots!
SystemInfo["RecoveryMode"] = False or fileCheck("/proc/stb/fp/boot_mode")	# This needs to be here so it can be reset by getMultibootslots!
from Tools.Multiboot import getMBbootdevice, getMultibootslots  # This import needs to be here to avoid a SystemInfo load loop!

#FIXMEE...
def getNumVideoDecoders():
	idx = 0
	while fileExists("/dev/dvb/adapter0/video%d"% idx, 'f'):
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

SystemInfo["12V_Output"] = Misc_Options.getInstance().detected_12V_output()
SystemInfo["ZapMode"] = fileCheck("/proc/stb/video/zapmode") or fileCheck("/proc/stb/video/zapping_mode")
SystemInfo["NumFrontpanelLEDs"] = countFrontpanelLEDs()
SystemInfo["FrontpanelDisplay"] = fileExists("/dev/dbox/oled0") or fileExists("/dev/dbox/lcd0")
SystemInfo["OledDisplay"] = fileExists("/dev/dbox/oled0") or fileExists(resolveFilename(SCOPE_SKIN, 'display/skin_display_picon.xml')) or fileExists(resolveFilename(SCOPE_SKIN, 'vfd_skin/skin_display_no_picon.xml')) or getBoxType() in ('osminiplus')
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
SystemInfo["HDMICEC"] = (fileExists("/dev/hdmi_cec") or fileExists("/dev/misc/hdmi_cec0")) and fileExists("/usr/lib/enigma2/python/Plugins/SystemPlugins/HdmiCEC/plugin.pyo")
SystemInfo["HasHDMI-CEC"] = (fileExists("/dev/hdmi_cec") or fileExists("/dev/misc/hdmi_cec0")) and fileExists("/usr/lib/enigma2/python/Plugins/SystemPlugins/HdmiCEC/plugin.pyo")
SystemInfo["SABSetup"] = fileExists("/usr/lib/enigma2/python/Plugins/SystemPlugins/SABnzbd/plugin.pyo")
SystemInfo["SeekStatePlay"] = False
SystemInfo["StatePlayPause"] = False
SystemInfo["StandbyState"] = False
SystemInfo["GraphicLCD"] = getBoxType() in ('vuultimo', 'xpeedlx3', 'et10000', 'mutant2400', 'quadbox2400', 'sezammarvel', 'atemionemesis', 'mbultra', 'beyonwizt4')
SystemInfo["Blindscan"] = fileExists("/usr/lib/enigma2/python/Plugins/SystemPlugins/Blindscan/plugin.pyo")
SystemInfo["Satfinder"] = fileExists("/usr/lib/enigma2/python/Plugins/SystemPlugins/Satfinder/plugin.pyo")
SystemInfo["HasExternalPIP"] = getMachineBuild() not in ('et9x00', 'et6x00', 'et5x00') and fileCheck("/proc/stb/vmpeg/1/external")
SystemInfo["hasPIPVisibleProc"] = fileCheck("/proc/stb/vmpeg/1/visible")
SystemInfo["VideoDestinationConfigurable"] = fileExists("/proc/stb/vmpeg/0/dst_left")
SystemInfo["GBWOL"] = fileExists("/usr/bin/gigablue_wol")
SystemInfo["LCDSKINSetup"] = path.exists("/usr/share/enigma2/display")
SystemInfo["7segment"] = getDisplayType() in ('7segment')
SystemInfo["grautec"] = fileExists("/tmp/usbtft")
SystemInfo["isGBIPBOX"] = fileExists("/usr/lib/enigma2/python/gbipbox.so")
SystemInfo["CIHelper"] = fileExists("/usr/bin/cihelper")
SystemInfo["3DMode"] = fileCheck("/proc/stb/fb/3dmode") or fileCheck("/proc/stb/fb/primary/3d")
SystemInfo["3DZNorm"] = fileCheck("/proc/stb/fb/znorm") or fileCheck("/proc/stb/fb/primary/zoffset")
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
SystemInfo["canMode12"] = getMachineBuild() in ("hd51", "vs1500", "h7") and ("brcm_cma=440M@328M brcm_cma=192M@768M", "brcm_cma=520M@248M brcm_cma=200M@768M")
SystemInfo["HAScmdline"] = fileCheck("/boot/cmdline.txt")
SystemInfo["HasMMC"] = fileHas("/proc/cmdline", "root=/dev/mmcblk") or SystemInfo["canMultiBoot"] and fileHas("/proc/cmdline", "root=/dev/sda")
SystemInfo["HasSDmmc"] = SystemInfo["canMultiBoot"] and "sd" in SystemInfo["canMultiBoot"][2] and "mmcblk" in getMachineMtdRoot()
SystemInfo["HasSDswap"] = getMachineBuild() in ("h9", "i55plus") and pathExists("/dev/mmcblk0p1")
SystemInfo["HasFullHDSkinSupport"] = getBoxType() not in ("et4000", "et5000", "sh1", "hd500c", "hd1100", "xp1000", "lc")
SystemInfo["CanProc"] = SystemInfo["HasMMC"] and getBrandOEM() != "vuplus"
SystemInfo["canRecovery"] = getMachineBuild() in ("hd51", "vs1500", "h7", "8100s") and ("disk.img", "mmcblk0p1") or getMachineBuild() in ("xc7439", "osmio4k", "osmio4kplus", "osmini4k") and ("emmc.img", "mmcblk1p1") or getMachineBuild() in ("gbmv200", "cc1", "sf8008", "sf8008m", "ustym4kpro", "beyonwizv2", "viper4k") and ("usb_update.bin", "none")
