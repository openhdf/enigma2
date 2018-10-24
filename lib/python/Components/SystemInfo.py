from os import path
from enigma import eDVBResourceManager, Misc_Options
from Tools.Directories import fileExists, fileCheck, resolveFilename, SCOPE_SKIN
from Tools.HardwareInfo import HardwareInfo
from boxbranding import getBoxType, getMachineBuild, getBrandOEM, getDisplayType, getHaveRCA, getHaveDVI, getHaveYUV, getHaveSCART, getHaveAVJACK

SystemInfo = { }

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
SystemInfo["StandbyLED"] = fileExists("/proc/stb/power/standbyled")
SystemInfo["StandbyPowerLed"] = fileExists("/proc/stb/power/standbyled")
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
SystemInfo["GraphicLCD"] = getBoxType() in ('vuultimo', 'xpeedlx3', 'et10000', 'mutant2400', 'quadbox2400', 'sezammarvel', 'atemionemesis', 'mbultra', 'beyonwizt4')
SystemInfo["Blindscan"] = fileExists("/usr/lib/enigma2/python/Plugins/SystemPlugins/Blindscan/plugin.pyo")
SystemInfo["Satfinder"] = fileExists("/usr/lib/enigma2/python/Plugins/SystemPlugins/Satfinder/plugin.pyo")
SystemInfo["HasExternalPIP"] = getMachineBuild() not in ('et9x00', 'et6x00', 'et5x00') and fileCheck("/proc/stb/vmpeg/1/external")
SystemInfo["hasPIPVisibleProc"] = fileCheck("/proc/stb/vmpeg/1/visible")
SystemInfo["VideoDestinationConfigurable"] = fileExists("/proc/stb/vmpeg/0/dst_left")
SystemInfo["GBWOL"] = fileExists("/usr/bin/gigablue_wol")
SystemInfo["LCDSKINSetup"] = path.exists("/usr/share/enigma2/display") and getDisplayType() not in ('7segment')
SystemInfo["grautec"] = fileExists("/tmp/usbtft")
SystemInfo["isGBIPBOX"] = fileExists("/usr/lib/enigma2/python/gbipbox.so")
SystemInfo["CIHelper"] = fileExists("/usr/bin/cihelper")
SystemInfo["3DMode"] = fileCheck("/proc/stb/fb/3dmode") or fileCheck("/proc/stb/fb/primary/3d")
SystemInfo["3DZNorm"] = fileCheck("/proc/stb/fb/znorm") or fileCheck("/proc/stb/fb/primary/zoffset")
SystemInfo["CanUse3DModeChoices"] = fileExists('/proc/stb/fb/3dmode_choices') and True or False
SystemInfo["HaveMultiBoot"] = (fileCheck("/boot/STARTUP") or fileCheck("/boot/cmdline.txt"))
SystemInfo["HaveMultiBootHD"] = fileCheck("/boot/STARTUP") and getMachineBuild() in ('hd51','vs1500','h7','ceryon7252')
SystemInfo["HaveMultiBootXC"] = fileCheck("/boot/cmdline.txt")
SystemInfo["HaveMultiBootGB"] = fileCheck("/boot/STARTUP") and getMachineBuild() in ('gb7252')
SystemInfo["HaveMultiBootCY"] = fileCheck("/boot/STARTUP") and getMachineBuild() in ('8100s')
SystemInfo["HaveMultiBootDS"] = fileCheck("/boot/STARTUP") and getMachineBuild() in ('cc1','sf8008') and fileCheck("/dev/sda")
SystemInfo["need_dsw"] = getBoxType() not in ('osminiplus','osmega')
SystemInfo["HaveCISSL"] = fileCheck("/etc/ssl/certs/customer.pem") and fileCheck("/etc/ssl/certs/device.pem")
SystemInfo["HasMultichannelPCM"] = fileCheck("/proc/stb/audio/multichannel_pcm")
SystemInfo["HaveTouchSensor"] = getBoxType() in ('dm520', 'dm525', 'dm900')
SystemInfo["DefaultDisplayBrightness"] = getBoxType() == 'dm900' and 8 or 5
SystemInfo["RecoveryMode"] = fileCheck("/proc/stb/fp/boot_mode")
SystemInfo["LCDMiniTV"] = fileExists("/proc/stb/lcd/mode")
SystemInfo["LcdLiveTV"] = fileCheck("/proc/stb/fb/sd_detach")
SystemInfo["MiniTV"] = fileCheck("/proc/stb/fb/sd_detach") or fileCheck("/proc/stb/lcd/live_enable")
SystemInfo["FastChannelChange"] = False
SystemInfo["LCDMiniTVPiP"] = SystemInfo["LCDMiniTV"] and getBoxType() not in ('gb800ueplus','gbquad4k','gbue4k')
SystemInfo["LCDsymbol_circle"] = fileCheck("/proc/stb/lcd/symbol_circle")
SystemInfo["ForceLNBPowerChanged"] = fileCheck("/proc/stb/frontend/fbc/force_lnbon")
SystemInfo["ForceToneBurstChanged"] = fileCheck("/proc/stb/frontend/fbc/force_toneburst")
SystemInfo["USETunersetup"] = SystemInfo["ForceLNBPowerChanged"] or SystemInfo["ForceToneBurstChanged"]
SystemInfo["HDMIin"] = getMachineBuild() in ('inihdp', 'hd2400', 'et10000', 'dm7080', 'dm820', 'dm900', 'gb7252', 'vuultimo4k', 'gbquad4k')
SystemInfo["HaveRCA"] = getHaveRCA() in ('True')
SystemInfo["HaveDVI"] = getHaveDVI() in ('True')
SystemInfo["HaveAVJACK"] = getHaveAVJACK() in ('True')
SystemInfo["HAVE_SCART"] = getHaveSCART() in ('True')
