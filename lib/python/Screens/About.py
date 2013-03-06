from Screen import Screen
from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.Sources.StaticText import StaticText
from Components.Harddisk import Harddisk
from Components.NimManager import nimmanager
from Components.About import about
from Components.ScrollLabel import ScrollLabel
from Components.Console import Console
from enigma import eTimer, getBoxType

from Components.Pixmap import MultiPixmap
from Components.Network import iNetwork

from Tools.StbHardware import getFPVersion

from os import path
from re import search

class About(Screen):
	skin = """
        <screen name="About" position="center,center" size="800,470" title="About">
            <widget source="lab1" render="Label" position="29,86" size="369,35" font="Regular;30" transparent="1" zPosition="1" />
			<widget source="lab2" render="Label" position="29,142" size="370,25" font="Regular;19" transparent="1" zPosition="1" />
			<widget source="lab3" render="Label" position="30,187" size="369,25" font="Regular;19" transparent="1" zPosition="1" />
			<eLabel text="OPEN SOURCE" position="410,434" size="353,28" font="Regular;22" transparent="1" zPosition="1" />
			<eLabel text="https://github.com/openhdf" position="410,472" size="352,28" font="Regular;19" transparent="1" zPosition="1" />
			<eLabel text="https://github.com/oe-alliance" position="409,505" size="354,28" font="Regular;19" transparent="1" zPosition="1" />
			<widget name="AboutScrollLabel" position="32,176" size="458,376" font="Regular;20" transparent="1" zPosition="1" scrollbarMode="showOnDemand" />
        </screen>"""
	def __init__(self, session):
		Screen.__init__(self, session)
		self.skinName = "About"
		Screen.setTitle(self, _("Image Information"))
		self.populate()

		self["key_green"] = Button(_("Translations"))

		self["actions"] = ActionMap(["SetupActions", "ColorActions", "TimerEditActions"],
			{
				"cancel": self.close,
				"ok": self.close,
				"log": self.showAboutReleaseNotes,
				"up": self["AboutScrollLabel"].pageUp,
				"down": self["AboutScrollLabel"].pageDown,
				"green": self.showTranslationInfo,
			})

	def populate(self):
		self["lab1"] = StaticText(_("OpenHDF"))
		self["lab2"] = StaticText(_("By HDF Image Team"))
		self["lab3"] = StaticText(_("Support at") + " www.HDFreaks.cc")
		if getBoxType() == 'vuuno':
			self["BoxType"] = StaticText(_("Hardware:") + " Vu+ Uno")
			AboutText = _("Hardware:") + " Vu+ Uno\n"
		elif getBoxType() == 'vuultimo':
			self["BoxType"] = StaticText(_("Hardware:") + " Vu+ Ultimo")
			AboutText = _("Hardware:") + " Vu+ Ultimo\n"
		elif getBoxType() == 'vusolo':
			self["BoxType"] = StaticText(_("Hardware:") + " Vu+ Solo")
			AboutText = _("Hardware:") + " Vu+ Solo\n"
		elif getBoxType() == 'vuduo':
			self["BoxType"] = StaticText(_("Hardware:") + " Vu+ Duo")
			AboutText = _("Hardware:") + " Vu+ Duo\n"
		elif getBoxType() == 'vusolo2':
			self["BoxType"] = StaticText(_("Hardware:") + " Vu+ Solo 2")
			AboutText = _("Hardware:") + " Vu+ Solo 2\n"
		elif getBoxType() == 'vuduo2':
			self["BoxType"] = StaticText(_("Hardware:") + " Vu+ Duo 2")
			AboutText = _("Hardware:") + " Vu+ Duo 2\n"			
		elif getBoxType() == 'et4x00':
			self["BoxType"] = StaticText(_("Hardware:") + " Xtrend ET4x00 Series")
			AboutText = _("Hardware:") + "  Xtrend ET4x00 Series\n"	
		elif getBoxType() == 'et5x00':
			self["BoxType"] = StaticText(_("Hardware:") + " Xtrend ET5x00 Series")
			AboutText = _("Hardware:") + "  Xtrend ET5x00 Series\n"
		elif getBoxType() == 'et6x00':
			self["BoxType"] = StaticText(_("Hardware:") + " Xtrend ET6x00 Series")
			AboutText = _("Hardware:") + "  Xtrend ET6x00 Series\n"
		elif getBoxType() == 'et9x00':
			self["BoxType"] = StaticText(_("Hardware:") + " Xtrend ET9x00 Series")
			AboutText = _("Hardware:") + " Xtrend ET9x00 Series\n"
		elif getBoxType() == 'odinm9':
			self["BoxType"] = StaticText(_("Hardware:") + " Odin M9")
			AboutText = _("Hardware:") + " Odin M9\n"
		elif getBoxType() == 'odinm7':
			self["BoxType"] = StaticText(_("Hardware:") + " Odin M7")
			AboutText = _("Hardware:") + " Odin M7\n"			
		elif getBoxType() == 'gb800solo':
			self["BoxType"] = StaticText(_("Hardware:") + " GigaBlue HD 800SOLO")
			AboutText = _("Hardware:") + " GigaBlue HD 800SOLO\n"
		elif getBoxType() == 'gb800se':
			self["BoxType"] = StaticText(_("Hardware:") + " GigaBlue HD 800SE")
			AboutText = _("Hardware:") + " GigaBlue HD 800SE\n"
		elif getBoxType() == 'gb800ue':
			self["BoxType"] = StaticText(_("Hardware:") + " GigaBlue HD 800UE")
			AboutText = _("Hardware:") + " GigaBlue HD 800UE\n"
		elif getBoxType() == 'gbquad':
			self["BoxType"] = StaticText(_("Hardware:") + " GigaBlue HD QUAD")
			AboutText = _("Hardware:") + " GigaBlue HD Quad\n"
		elif getBoxType() == 'ventonhdx':
			self["BoxType"] = StaticText(_("Hardware:") + " Venton Unibox HDx")
			AboutText = _("Hardware:") + " Venton Unibox HDx\n"
		elif getBoxType() == 'ixussone':
			self["BoxType"] = StaticText(_("Hardware:") + " Ixuss One")
			AboutText = _("Hardware:") + " Ixuss One\n"
		elif getBoxType() == 'ixusszero':
			self["BoxType"] = StaticText(_("Hardware:") + " Ixuss Zero")
			AboutText = _("Hardware:") + " Ixuss Zero\n"
		elif getBoxType() == 'ixussduo':
			self["BoxType"] = StaticText(_("Hardware:") + " Ixuss Duo")
			AboutText = _("Hardware:") + " Ixuss Duo\n"
		elif getBoxType() == 'tmtwin':
			self["BoxType"] = StaticText(_("Hardware:") + " Technomate Twin")
			AboutText = _("Hardware:") + " Technomate Twin\n"
		elif getBoxType() == 'tm2t':
			self["BoxType"] = StaticText(_("Hardware:") + " Technomate 2T")
			AboutText = _("Hardware:") + " Technomate 2T\n"
		elif getBoxType() == 'tmsingle':
			self["BoxType"] = StaticText(_("Hardware:") + " Technomate Single")	
			AboutText = _("Hardware:") + " Technomate Single\n"
		elif getBoxType() == 'xp1000':
			self["BoxType"] = StaticText(_("Hardware:") + " MK Digital XP1000")	
			AboutText = _("Hardware:") + " MK Digital XP1000\n"
		else:
			model = getBoxType()

		if model:
			AboutText += _("Model:\t%s") % model + "\n"

		if path.exists('/proc/stb/info/chipset'):
			AboutText += _("Chipset:\tBCM%s") % about.getChipSetString().lower().replace('\n','').replace('bcm','') + "\n"

		AboutText += _("CPU:\t%s") % about.getCPUString() + "\n"
		AboutText += _("Cores:\t%s") % about.getCpuCoresString() + "\n"

		AboutText += _("Kernel:\t%s") % about.getKernelVersionString() + "\n"
		AboutText += _("Drivers:\t%s") % about.getDriversString() + "\n"
		AboutText += _("Image:\t%s") % about.getImageTypeString() + "\n"
		AboutText += _("Version:\t%s") % about.getImageVersionString() + "\n"
		AboutText += _("Build:\t%s") % about.getBuildVersionString() + "\n"
		AboutText += _("Last update:\t%s") % about.getLastUpdateString() + "\n\n"

		fp_version = getFPVersion()
		if fp_version is None:
			fp_version = ""
		elif fp_version != 0:
			fp_version = _("Frontprocessor version: %d") % fp_version
			AboutText += fp_version + "\n"
		self["FPVersion"] = StaticText(fp_version)

		tempinfo = ""
		if path.exists('/proc/stb/sensors/temp0/value'):
			f = open('/proc/stb/sensors/temp0/value', 'r')
			tempinfo = f.read()
			f.close()
		elif path.exists('/proc/stb/fp/temp_sensor'):
			f = open('/proc/stb/fp/temp_sensor', 'r')
			tempinfo = f.read()
			f.close()
		if tempinfo and int(tempinfo.replace('\n','')) > 0:
			mark = str('\xc2\xb0')
			AboutText += _("System temperature:") + " " + tempinfo.replace('\n','') + mark + "C\n\n"

		self["AboutScrollLabel"] = ScrollLabel(AboutText)

	def showTranslationInfo(self):
		self.session.open(TranslationInfo)

	def showAboutReleaseNotes(self):
		self.session.open(ViewGitLog)

	def createSummary(self):
		return AboutSummary

class Devices(Screen):
	skin = """
        <screen name="Devices" position="center,center" size="800,470" title="Devices">
			<widget source="TunerHeader" render="Label" position="31,0" size="458,36" font="Regular;20" transparent="1" zPosition="1" />
			<widget source="nims" render="Label" position="31,34" size="458,108" font="Regular;18" transparent="1" zPosition="1" enableWrapAround="0" />
			<widget source="HDDHeader" render="Label" position="31,146" size="458,36" font="Regular;20" transparent="1" zPosition="1" />
			<widget source="hdd" render="Label" position="31,179" size="458,112" font="Regular;18" transparent="1" zPosition="1" enableWrapAround="0" />
			<widget source="MountsHeader" render="Label" position="31,293" size="458,36" font="Regular;20" transparent="1" zPosition="1" />
			<widget source="mounts" render="Label" position="31,334" size="458,143" font="Regular;18" transparent="1" zPosition="1" enableWrapAround="0" />
        </screen>"""
	def __init__(self, session):
		Screen.__init__(self, session)
		self.skinName = "Devices"
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
			if not search('sd[a-z][1-9]',device):
				continue
			if device in list2:
				continue

			mount = '/dev/' + device
			f = open('/proc/mounts', 'r')
			for line in f.readlines():
				if line.find(device) != -1:
					parts = line.strip().split()
					mount = str(parts[1])
					break
					continue
			f.close()

			if not mount.startswith('/dev/'):
				size = Harddisk(device).diskSize()
				free = Harddisk(device).free()

				if ((float(size) / 1024) / 1024) >= 1:
					sizeline = _("Size: ") + str(round(((float(size) / 1024) / 1024),2)) + _("TB")
				elif (size / 1024) >= 1:
					sizeline = _("Size: ") + str(round((float(size) / 1024),2)) + _("GB")
				elif size >= 1:
					sizeline = _("Size: ") + str(size) + _("MB")
				else:
					sizeline = _("Size: ") + _("unavailable")

				if ((float(free) / 1024) / 1024) >= 1:
					freeline = _("Free: ") + str(round(((float(free) / 1024) / 1024),2)) + _("TB")
				elif (free / 1024) >= 1:
					freeline = _("Free: ") + str(round((float(free) / 1024),2)) + _("GB")
				elif free >= 1:
					freeline = _("Free: ") + str(free) + _("MB")
				else:
					freeline = _("Free: ") + _("full")
				self.list.append(mount +'\t'  + sizeline + ' \t' + freeline)
			else:
				self.list.append(mount +'\t'  + _('Not mounted'))

			list2.append(device)
		self.list = '\n'.join(self.list)
		self["hdd"].setText(self.list)

		self.Console.ePopen("df -mh | grep -v '^Filesystem'", self.Stage1Complete)

	def Stage1Complete(self,result, retval, extra_args = None):
		result = result.replace('\n                        ',' ').split('\n')
		self.mountinfo = ""
		for line in result:
			self.parts = line.split()
			if line and self.parts[0] and (self.parts[0].startswith('192') or self.parts[0].startswith('//192')):
				line = line.split()
				ipaddress = line[0]
				mounttotal = line[1]
				mountfree = line[3]
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
	skin = """
	<screen name="SystemMemoryInfo" position="center,center" size="560,400" >
		<widget name="AboutScrollLabel" position="32,88" size="458,376" font="Regular;20" transparent="1" zPosition="1" scrollbarMode="showOnDemand" />
	</screen>"""
	def __init__(self, session):
		Screen.__init__(self, session)
		Screen.setTitle(self, _("Memory Information"))
		self.skinName = "SystemMemoryInfo"
		self["AboutScrollLabel"] = ScrollLabel()

		self["actions"] = ActionMap(["SetupActions", "ColorActions"],
			{
				"cancel": self.close,
				"ok": self.close,
			})

		out_lines = file("/proc/meminfo").readlines()
		self.AboutText = _("RAM") + '\n\n'
		RamTotal = "-"
		RamFree = "-"
		for lidx in range(len(out_lines)-1):
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

	def Stage1Complete(self,result, retval, extra_args = None):
		flash = str(result).replace('\n','')
		flash = flash.split()
		RamTotal=flash[1]
		RamFree=flash[3]

		self.AboutText += _("FLASH") + '\n\n'
		self.AboutText += _("Total:") + "\t" + RamTotal + "\n"
		self.AboutText += _("Free:") + "\t" + RamFree + "\n\n"

		self["AboutScrollLabel"].setText(self.AboutText)
		self["actions"].setEnabled(True)

	def createSummary(self):
		return AboutSummary

class SystemNetworkInfo(Screen):
	skin = """
		<screen name="SystemNetworkInfo" position="center,center" size="560,400" >
			<widget name="AboutScrollLabel" position="29,82" size="458,376" font="Regular;20" transparent="1" zPosition="1" scrollbarMode="showOnDemand" />
			<widget source="LabelBSSID" render="Label" position="28,292" size="200,25" valign="left" font="Regular;20" transparent="1" />
			<widget source="LabelESSID" render="Label" position="29,329" size="200,25" valign="center" font="Regular;20" transparent="1" />
			<widget source="LabelQuality" render="Label" position="29,367" size="200,25" valign="center" font="Regular;20" transparent="1" />
			<widget source="LabelSignal" render="Label" position="29,405" size="200,25" valign="center" font="Regular;20" transparent="1" />
			<widget source="LabelBitrate" render="Label" position="30,440" size="200,25" valign="center" font="Regular;20" transparent="1" />
			<widget source="LabelEnc" render="Label" position="29,475" size="200,25" valign="center" font="Regular;20" transparent="1" />
			<widget source="BSSID" render="Label" position="204,292" size="310,25" valign="center" font="Regular;20" transparent="1" />
			<widget source="ESSID" render="Label" position="204,330" size="310,25" valign="center" font="Regular;20" transparent="1" />
			<widget source="quality" render="Label" position="204,367" size="310,25" valign="center" font="Regular;20" transparent="1" />
			<widget source="signal" render="Label" position="203,405" size="310,25" valign="center" font="Regular;20" transparent="1" />
			<widget source="bitrate" render="Label" position="203,440" size="310,25" valign="center" font="Regular;20" transparent="1" />
			<widget source="enc" render="Label" position="203,474" size="310,25" valign="center" font="Regular;20" transparent="1" />
			<widget source="IFtext" render="Label" position="31,509" size="120,21" zPosition="10" font="Regular;20" halign="left" transparent="1" />
			<widget source="IF" render="Label" position="139,508" size="375,21" zPosition="10" font="Regular;20" halign="left" transparent="1" />
			<widget source="Statustext" render="Label" position="31,537" size="115,21" zPosition="10" font="Regular;20" halign="left" transparent="1" />
			<widget name="statuspic" pixmaps="skin_default/buttons/button_green.png,skin_default/buttons/button_green_off.png" position="149,539" zPosition="10" size="15,16" transparent="0" alphatest="on" />
		</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		Screen.setTitle(self, _("Network Information"))
		self.skinName = "SystemNetworkInfo"
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
		self.AboutText = ""
		self.iface = "eth0"
		eth0 = about.getIfConfig('eth0')
		if eth0.has_key('addr'):
			self.AboutText += _("IP:") + "\t" + eth0['addr'] + "\n"
			if eth0.has_key('netmask'):
				self.AboutText += _("Netmask:") + "\t" + eth0['netmask'] + "\n"
			if eth0.has_key('hwaddr'):
				self.AboutText += _("MAC:") + "\t" + eth0['hwaddr'] + "\n"
			self.iface = 'eth0'

		wlan0 = about.getIfConfig('wlan0')
		if wlan0.has_key('addr'):
			self.AboutText += _("IP:") + "\t" + wlan0['addr'] + "\n"
			if wlan0.has_key('netmask'):
				self.AboutText += _("Netmask:") + "\t" + wlan0['netmask'] + "\n"
			if wlan0.has_key('hwaddr'):
				self.AboutText += _("MAC:") + "\t" + wlan0['hwaddr'] + "\n"
			self.iface = 'wlan0'

		rx_bytes, tx_bytes = about.getIfTransferredData(self.iface)
		self.AboutText += "\n" + _("Bytes received:") + "\t" + rx_bytes + "\n"
		self.AboutText += _("Bytes sent:") + "\t" + tx_bytes + "\n"

		hostname = file('/proc/sys/kernel/hostname').read()
		self.AboutText += "\n" + _("Hostname:") + "\t" + hostname + "\n"
		self["AboutScrollLabel"] = ScrollLabel(self.AboutText)

	def cleanup(self):
		if self.iStatus:
			self.iStatus.stopWlanConsole()

	def resetList(self):
		if self.iStatus:
			self.iStatus.getDataForInterface(self.iface,self.getInfoCB)

	def getInfoCB(self,data,status):
		self.LinkState = None
		if data is not None:
			if data is True:
				if status is not None:
					if self.iface == 'wlan0':
						if status[self.iface]["essid"] == "off":
							essid = _("No Connection")
						else:
							essid = status[self.iface]["essid"]
						if status[self.iface]["accesspoint"] == "Not-Associated":
							accesspoint = _("Not-Associated")
							essid = _("No Connection")
						else:
							accesspoint = status[self.iface]["accesspoint"]
						if self.has_key("BSSID"):
							self.AboutText += _('Accesspoint:') + '\t' + accesspoint + '\n'
						if self.has_key("ESSID"):
							self.AboutText += _('SSID:') + '\t' + essid + '\n'

						quality = status[self.iface]["quality"]
						if self.has_key("quality"):
							self.AboutText += _('Link Quality:') + '\t' + quality + '\n'

						if status[self.iface]["bitrate"] == '0':
							bitrate = _("Unsupported")
						else:
							bitrate = str(status[self.iface]["bitrate"]) + " Mb/s"
						if self.has_key("bitrate"):
							self.AboutText += _('Bitrate:') + '\t' + bitrate + '\n'

						signal = status[self.iface]["signal"]
						if self.has_key("signal"):
							self.AboutText += _('Signal Strength:') + '\t' + signal + '\n'

						if status[self.iface]["encryption"] == "off":
							if accesspoint == "Not-Associated":
								encryption = _("Disabled")
							else:
								encryption = _("Unsupported")
						else:
							encryption = _("Enabled")
						if self.has_key("enc"):
							self.AboutText += _('Encryption:') + '\t' + encryption + '\n'

						if status[self.iface]["essid"] == "off" or status[self.iface]["accesspoint"] == "Not-Associated" or status[self.iface]["accesspoint"] == False:
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
				self.iStatus.getDataForInterface(self.iface,self.getInfoCB)
			except:
				self["statuspic"].setPixmapNum(1)
				self["statuspic"].show()
		else:
			iNetwork.getLinkState(self.iface,self.dataAvail)

	def dataAvail(self,data):
		self.LinkState = None
		for line in data.splitlines():
			line = line.strip()
			if 'Link detected:' in line:
				if "yes" in line:
					self.LinkState = True
				else:
					self.LinkState = False
		if self.LinkState == True:
			iNetwork.checkNetworkState(self.checkNetworkCB)
		else:
			self["statuspic"].setPixmapNum(1)
			self["statuspic"].show()

	def checkNetworkCB(self,data):
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
		self.skinName = "AboutSummary"
		if about.getImageTypeString() == 'Release':
			self["selected"] = StaticText("HDF:" + about.getImageVersionString() + ' (R)')
		elif about.getImageTypeString() == 'Experimental':
			self["selected"] = StaticText("HDF:" + about.getImageVersionString() + ' (B)')
		if getBoxType() == 'vuuno':
			self["BoxType"] = StaticText(_("Hardware:") + " Vu+ Uno")
		elif getBoxType() == 'vuultimo':
			self["BoxType"] = StaticText(_("Hardware:") + " Vu+ Ultimo")
		elif getBoxType() == 'vusolo':
			self["BoxType"] = StaticText(_("Hardware:") + " Vu+ Solo")
		elif getBoxType() == 'vuduo':
			self["BoxType"] = StaticText(_("Hardware:") + " Vu+ Duo")
		elif getBoxType() == 'vusolo2':
			self["BoxType"] = StaticText(_("Hardware:") + " Vu+ Solo 2")
		elif getBoxType() == 'vuduo2':
			self["BoxType"] = StaticText(_("Hardware:") + " Vu+ Duo 2")			
		elif getBoxType() == 'et4x00':
			self["BoxType"] = StaticText(_("Hardware:") + " Xtrend ET4x00 Series")	
		elif getBoxType() == 'et5x00':
			self["BoxType"] = StaticText(_("Hardware:") + " Xtrend ET5x00 Series")
		elif getBoxType() == 'et6x00':
			self["BoxType"] = StaticText(_("Hardware:") + " Xtrend ET6x00 Series")
		elif getBoxType() == 'et9x00':
			self["BoxType"] = StaticText(_("Hardware:") + " Xtrend ET9x00 Series")
		elif getBoxType() == 'odinm9':
			self["BoxType"] = StaticText(_("Hardware:") + " Odin M9")
		elif getBoxType() == 'odinm7':
			self["BoxType"] = StaticText(_("Hardware:") + " Odin M7")			
		elif getBoxType() == 'gb800solo':
			self["BoxType"] = StaticText(_("Hardware:") + " GigaBlue HD 800SOLO")
		elif getBoxType() == 'gb800se':
			self["BoxType"] = StaticText(_("Hardware:") + " GigaBlue HD 800SE")
		elif getBoxType() == 'gb800ue':
			self["BoxType"] = StaticText(_("Hardware:") + " GigaBlue HD 800UE")
		elif getBoxType() == 'gbquad':
			self["BoxType"] = StaticText(_("Hardware:") + " GigaBlue HD QUAD")
		elif getBoxType() == 'ventonhdx':
			self["BoxType"] = StaticText(_("Hardware:") + " Venton Unibox HDx")
		elif getBoxType() == 'ixussone':
			self["BoxType"] = StaticText(_("Hardware:") + " Ixuss One")
		else:
			self["BoxType"] = StaticText(_("Hardware:") + " " + getBoxType())
		self["KernelVersion"] = StaticText(_("Kernel:") + " " + about.getKernelVersionString())
		self["ImageType"] = StaticText(_("Image:") + " " + about.getImageTypeString())
		self["ImageVersion"] = StaticText(_("Version:") + " " + about.getImageVersionString() + "   " + _("Build:") + " " + about.getBuildVersionString())
		self["EnigmaVersion"] = StaticText(_("Last Update:") + " " + about.getLastUpdateString())

class ViewGitLog(Screen):
	def __init__(self, session, args = None):
		Screen.__init__(self, session)
		self.skinName = "SoftwareUpdateChanges"
		self.setTitle(_("OE Changes"))
		self.logtype = 'oe'
		self["text"] = ScrollLabel()
		self['title_summary'] = StaticText()
		self['text_summary'] = StaticText()
		self["key_red"] = Button(_("Close"))
		self["key_green"] = Button(_("OK"))
		self["key_yellow"] = Button(_("Show E2 Log"))
		self["myactions"] = ActionMap(['ColorActions', 'OkCancelActions', 'DirectionActions'],
		{
			'cancel': self.closeRecursive,
			'green': self.closeRecursive,
			"red": self.closeRecursive,
			"yellow": self.changelogtype,
			"left": self.pageUp,
			"right": self.pageDown,
			"down": self.pageDown,
			"up": self.pageUp
		},-1)
		self.onLayoutFinish.append(self.getlog)

	def changelogtype(self):
		if self.logtype == 'e2':
			self["key_yellow"].setText(_("Show E2 Log"))
			self.setTitle(_("OE Changes"))
			self.logtype = 'oe'
		else:
			self["key_yellow"].setText(_("Show OE Log"))
			self.setTitle(_("Enigma2 Changes"))
			self.logtype = 'e2'
		self.getlog()

	def pageUp(self):
		self["text"].pageUp()

	def pageDown(self):
		self["text"].pageDown()

	def getlog(self):
		fd = open('/etc/' + self.logtype + '-git.log', 'r')
		releasenotes = fd.read()
		fd.close()
		releasenotes = releasenotes.replace('\nopenvix: build',"\n\nopenvix: build")
		self["text"].setText(releasenotes)
		summarytext = releasenotes
		try:
			self['title_summary'].setText(summarytext[0]+':')
			self['text_summary'].setText(summarytext[1])
		except:
			self['title_summary'].setText("")
			self['text_summary'].setText("")

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
		print infomap

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
