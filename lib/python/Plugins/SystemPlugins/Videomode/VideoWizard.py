from boxbranding import getBoxType, getMachineName
from Screens.Wizard import WizardSummary
from Screens.WizardLanguage import WizardLanguage
from Screens.Rc import Rc
from Screens.Screen import Screen
from VideoHardware import video_hw

from Components.Pixmap import Pixmap, MovingPixmap, MultiPixmap
from Components.config import config, ConfigBoolean, configfile

from Tools.Directories import resolveFilename, SCOPE_PLUGINS
from Tools.HardwareInfo import HardwareInfo

config.misc.showtestcard = ConfigBoolean(default = False)

try:
	file = open("/proc/stb/info/chipset", "r")
	chipset = file.readline().strip()
	file.close()
except:
	chipset = "unknown"
	
try:
	file = open("/proc/stb/info/boxtype", "r")
	model = file.readline().strip()
	file.close()
except:
	model = "unknown"	

has_rca = False	
hw_type = HardwareInfo().get_device_name()	
if getBoxType() == 'gbquad' or getBoxType() == 'et5x00' or model == 'et6000' or getBoxType() == 'e3hd' or getBoxType() == 'odinm6' or getMachineName() == 'AX-Odin' or getBoxType() == 'ebox7358' or getBoxType() == 'tmnano' or hw_type == 'ultra' or hw_type == "me" or hw_type == "minime" or getBoxType() == 'optimussos1' or getBoxType() == 'optimussos2' or getBoxType() == 'gb800seplus' or getBoxType() == 'gb800ueplus' or model == 'ini-1000ru' or model == 'ini-1000sv':	
	has_rca = True

class VideoWizardSummary(WizardSummary):
	skin = (
	"""<screen name="VideoWizardSummary" position="0,0" size="132,64" id="1">
		<widget name="text" position="6,4" size="120,40" font="Regular;12" transparent="1" />
		<widget source="parent.list" render="Label" position="6,40" size="120,21" font="Regular;14">
			<convert type="StringListSelection" />
		</widget>
		<!--widget name="pic" pixmap="%s" position="6,22" zPosition="10" size="64,64" transparent="1" alphatest="on"/-->
	</screen>""",
	"""<screen name="VideoWizardSummary" position="0,0" size="96,64" id="2">
		<widget name="text" position="0,4" size="96,40" font="Regular;12" transparent="1" />
		<widget source="parent.list" render="Label" position="0,40" size="96,21" font="Regular;14">
			<convert type="StringListSelection" />
		</widget>
		<!--widget name="pic" pixmap="%s" position="0,22" zPosition="10" size="64,64" transparent="1" alphatest="on"/-->
	</screen>""")
	#% (resolveFilename(SCOPE_PLUGINS, "SystemPlugins/Videomode/lcd_Scart.png"))

	def __init__(self, session, parent):
		WizardSummary.__init__(self, session, parent)
		#self["pic"] = Pixmap()

	def setLCDPicCallback(self):
		self.parent.setLCDTextCallback(self.setText)

	def setLCDPic(self, file):
		self["pic"].instance.setPixmapFromFile(file)

class VideoWizard(WizardLanguage, Rc):
	skin = """
		<screen position="fill" title="Welcome..." flags="wfNoBorder" >
			<panel name="WizardMarginsTemplate"/>
			<panel name="WizardPictureLangTemplate"/>
			<panel name="RemoteControlTemplate"/>
			<panel position="left" size="10,*" />
			<panel position="right" size="10,*" />
			<panel position="fill">
				<widget name="text" position="top" size="*,270" font="Regular;23" valign="center" />
				<panel position="fill">
					<panel position="left" size="150,*">
						<widget name="portpic" position="top" zPosition="10" size="150,150" transparent="1" alphatest="on"/>
					</panel>
					<panel position="fill" layout="stack">
						<widget source="list" render="Listbox" position="fill" scrollbarMode="showOnDemand" >
							<convert type="StringList" />
						</widget>
						<!--<widget name="config" position="fill" zPosition="1" scrollbarMode="showOnDemand" />-->
					</panel>
				</panel>
			</panel>
		</screen>"""

	def __init__(self, session):
		# FIXME anyone knows how to use relative paths from the plugin's directory?
		self.xmlfile = resolveFilename(SCOPE_PLUGINS, "SystemPlugins/Videomode/videowizard.xml")
		self.hw = video_hw

		WizardLanguage.__init__(self, session, showSteps = False, showStepSlider = False)
		Rc.__init__(self)
		self["wizard"] = Pixmap()
		self["portpic"] = Pixmap()
		Screen.setTitle(self, _("Welcome..."))

		self.port = None
		self.mode = None
		self.rate = None


	def createSummary(self):
		print "++++++++++++***++**** VideoWizard-createSummary"
		from Screens.Wizard import WizardSummary
		return VideoWizardSummary

	def markDone(self):
		self.hw.saveMode(self.port, self.mode, self.rate)
		config.misc.videowizardenabled.setValue(0)
		config.misc.videowizardenabled.save()
		configfile.save()

	def listInputChannels(self):
		hw_type = HardwareInfo().get_device_name()
		has_hdmi = HardwareInfo().has_hdmi()

		list = []

		for port in self.hw.getPortList():
			if self.hw.isPortUsed(port):
				descr = port
				if descr == 'DVI' and has_hdmi:
					descr = 'HDMI'
				if descr == 'Scart' and has_rca:
					descr = 'RCA'					
				if port != "DVI-PC":
					list.append((descr,port))
		list.sort(key = lambda x: x[0])
		print "listInputChannels:", list
		return list

	def inputSelectionMade(self, index):
		print "inputSelectionMade:", index
		self.port = index
		self.inputSelect(index)

	def inputSelectionMoved(self):
		hw_type = HardwareInfo().get_device_name()
		has_hdmi = HardwareInfo().has_hdmi()
		print "input selection moved:", self.selection
		self.inputSelect(self.selection)
		if self["portpic"].instance is not None:
			picname = self.selection
			if picname == 'DVI' and has_hdmi:
				picname = "HDMI"
			if picname == 'Scart' and has_rca:
				picname = "RCA"	
			self["portpic"].instance.setPixmapFromFile(resolveFilename(SCOPE_PLUGINS, "SystemPlugins/Videomode/" + picname + ".png"))

	def inputSelect(self, port):
		print "inputSelect:", port
		modeList = self.hw.getModeList(self.selection)
		print "modeList:", modeList
		self.port = port
		if (len(modeList) > 0):
			ratesList = self.listRates(modeList[0][0])
			self.hw.setMode(port = port, mode = modeList[0][0], rate = ratesList[0][0])

	def listModes(self):
		list = []
		print "modes for port", self.port
		for mode in self.hw.getModeList(self.port):
			#if mode[0] != "PC":
				list.append((mode[0], mode[0]))
		print "modeslist:", list
		return list

	def modeSelectionMade(self, index):
		print "modeSelectionMade:", index
		self.mode = index
		self.modeSelect(index)

	def modeSelectionMoved(self):
		print "mode selection moved:", self.selection
		self.modeSelect(self.selection)

	def modeSelect(self, mode):
		ratesList = self.listRates(mode)
		print "ratesList:", ratesList
		if self.port == "DVI" and mode in ("720p", "1080i", "1080p") and (chipset.find('7358') != -1 or chipset.find('7356') != -1):
			self.rate = "multi"
			self.hw.setMode(port = self.port, mode = mode, rate = "multi")
		elif self.port == "DVI" and mode in ("720p", "1080i"):
			self.rate = "multi"
			self.hw.setMode(port = self.port, mode = mode, rate = "multi")
		else:
			self.hw.setMode(port = self.port, mode = mode, rate = ratesList[0][0])

	def listRates(self, querymode = None):
		if querymode is None:
			querymode = self.mode
		list = []
		print "modes for port", self.port, "and mode", querymode
		for mode in self.hw.getModeList(self.port):
			print mode
			if mode[0] == querymode:
				for rate in mode[1]:
					if self.port == "DVI-PC":
						print "rate:", rate
						if rate == "640x480":
							list.insert(0, (rate, rate))
							continue
					list.append((rate, rate))
		return list

	def rateSelectionMade(self, index):
		print "rateSelectionMade:", index
		self.rate = index
		self.rateSelect(index)

	def rateSelectionMoved(self):
		print "rate selection moved:", self.selection
		self.rateSelect(self.selection)

	def rateSelect(self, rate):
		self.hw.setMode(port = self.port, mode = self.mode, rate = rate)

	def showTestCard(self, selection = None):
		if selection is None:
			selection = self.selection
		print "set config.misc.showtestcard to", {'yes': True, 'no': False}[selection]
		if selection == "yes":
			config.misc.showtestcard.setValue(True)
		else:
			config.misc.showtestcard.setValue(False)

	def keyNumberGlobal(self, number):
		if number in (1,2,3):
			if number == 1:
				self.hw.saveMode("DVI", "720p", "multi")
			elif number == 2:
				self.hw.saveMode("DVI", "1080i", "multi")
			elif number == 3:
				self.hw.saveMode("Scart", "Multi", "multi")
			self.hw.setConfiguredMode()
			self.close()

		WizardLanguage.keyNumberGlobal(self, number)
