from Screens.Screen import Screen
from Components.ConfigList import ConfigListScreen
from Components.config import config, ConfigSubsection, ConfigInteger, ConfigSelection, ConfigSlider, getConfigListEntry, ConfigYesNo
from Screens.MessageBox import MessageBox
from enigma import eActionMap
from Components.Sources.StaticText import StaticText
from Components.ServiceEventTracker import ServiceEventTracker
from enigma import iPlayableService, iServiceInformation, eServiceCenter, eServiceReference, eTimer
from ServiceReference import ServiceReference
from Plugins.Plugin import PluginDescriptor
from Components.PluginComponent import plugins
from Tools.Directories import resolveFilename, SCOPE_PLUGINS

from os import path
if path.exists("/proc/stb/fb/3dmode"):
	val_sidebyside = "sidebyside"
	val_topandbottom = "topandbottom"
	val_auto = "auto"
	val_off = "off"

	path_mode = "/proc/stb/fb/3dmode"
	path_znorm = "/proc/stb/fb/znorm"

	modelist = {val_off: _("Off"), val_auto: _("Auto"), val_sidebyside: _("Side by Side"), val_topandbottom: _("Top and Bottom")}
	menulist = {"none": _("None"), "menu": _("Main menu"), "ext": _("Extensions list"), "menuext": _("Menu & Extensions list")}
	togglelist = {val_sidebyside: _("Side by Side - Auto"), val_topandbottom: _("Top and Bottom - Auto")}
else:
	val_sidebyside = "sbs"
	val_topandbottom = "tab"
	val_auto = "off"
	val_off = "off"

	path_mode = "/proc/stb/fb/primary/3d"
	path_znorm = "/proc/stb/fb/primary/zoffset"

	modelist = {val_off: _("Off"), val_sidebyside: _("Side by Side"), val_topandbottom: _("Top and Bottom")}
	menulist = {"none": _("None"), "menu": _("Main menu"), "ext": _("Extensions list"), "menuext": _("Menu & Extensions list")}
	togglelist = {val_sidebyside: _("Side by Side - Off"), val_topandbottom: _("Top and Bottom - Off")}
	
config.plugins.OSD3DSetup = ConfigSubsection()
config.plugins.OSD3DSetup.mode = ConfigSelection(choices = modelist, default = val_auto)
config.plugins.OSD3DSetup.znorm = ConfigInteger(default = 0)
config.plugins.OSD3DSetup.menuext = ConfigSelection(choices = menulist, default = "none")
config.plugins.OSD3DSetup.auto = ConfigYesNo(default = False)
config.plugins.OSD3DSetup.toggle = ConfigSelection(choices = togglelist, default = val_sidebyside)
config.plugins.OSD3DSetup.prompt = ConfigInteger(default = 10)

# Flags
FLAG_MAKE = 0
FLAG_BREAK = 1
FLAG_REPEAT = 2
FLAG_LONG = 3
FLAG_ASCII = 4

#Device Types
TYPE_STANDARD = "dreambox remote control (native)"
TYPE_ADVANCED = "dreambox advanced remote control (native)"
TYPE_KEYBOARD = "dreambox ir keyboard"

EXTENSIONS = {
		"ts": "movie",
		"m2ts": "movie",
		"avi": "movie",
		"divx": "movie",
		"mpg": "movie",
		"mpeg": "movie",
		"mkv": "movie",
		"mp4": "movie",
		"mov": "movie",
		"vob": "movie",
		"ifo": "movie",
		"iso": "movie",
		"flv": "movie",
		"3gp": "movie",
		"mod": "movie"
	}
	
confirmed3D = False	

class OSD3DSetupScreen(Screen, ConfigListScreen):
	#class for configure 3D default settings
	skin = """
	<screen position="c-200,c-100" size="400,200" title="OSD 3D setup">
		<widget name="config" position="c-175,c-75" size="350,150" />
		<ePixmap pixmap="buttons/green.png" position="c-145,e-45" zPosition="0" size="140,40" alphatest="on" />
		<ePixmap pixmap="buttons/red.png" position="c+5,e-45" zPosition="0" size="140,40" alphatest="on" />
		<widget name="ok" position="c-145,e-45" size="140,40" valign="center" halign="center" zPosition="1" font="Regular;20" transparent="1" backgroundColor="green" />
		<widget name="cancel" position="c+5,e-45" size="140,40" valign="center" halign="center" zPosition="1" font="Regular;20" transparent="1" backgroundColor="red" />
	</screen>"""

	def __init__(self, session):
		self.skin = OSD3DSetupScreen.skin
		Screen.__init__(self, session)

		from Components.ActionMap import ActionMap
		from Components.Button import Button

		self["ok"] = Button(_("OK"))
		self["cancel"] = Button(_("Cancel"))
		self["help"] = StaticText()
		
		self["actions"] = ActionMap(["SetupActions", "ColorActions"],
		{
			"ok": self.keyGo,
			"save": self.keyGo,
			"cancel": self.keyCancel,
			"green": self.keyGo,
			"red": self.keyCancel,
			"0": self.keyZero,
		}, -2)

		# preparing setting items 
		mode = config.plugins.OSD3DSetup.mode.value
		znorm = config.plugins.OSD3DSetup.znorm.value
		menuext = config.plugins.OSD3DSetup.menuext.value
		auto = config.plugins.OSD3DSetup.auto.value
		toggle = config.plugins.OSD3DSetup.toggle.value
		prompt = config.plugins.OSD3DSetup.prompt.value
				
		self.mode = ConfigSelection(choices = modelist, default = nz(mode, val_auto))
		self.znorm = ConfigSlider(default = znorm + 50, increment = 1, limits = (0, 100))
		self.menuext = ConfigSelection(choices = menulist, default = nz(menuext, "none"))
		self.auto = ConfigYesNo(default = nz(auto, False))
		self.toggle = ConfigSelection(choices = togglelist, default = nz(toggle, val_sidebyside))
		self.prompt = ConfigInteger(nz(prompt,10), limits=(0, 30))
		# adding notifiers to immediatelly preview changed 3D settings
		self.mode.addNotifier(self.setPreviewSettings, initial_call = False)
		self.znorm.addNotifier(self.setPreviewSettings, initial_call = False)
				
		self.refresh()
		self.initHelpTexts()
		ConfigListScreen.__init__(self, self.list, session = self.session)
		self["config"].onSelectionChanged.append(self.updateHelp)
	
	def keyLeft(self):
		ConfigListScreen.keyLeft(self)
		self.reloadList()
		
	def keyRight(self):
		ConfigListScreen.keyRight(self)
		self.reloadList()
			
	def keyZero(self):
		cur = self["config"].getCurrent()
		if cur == getConfigListEntry(_("Depth"), self.znorm):
			self.znorm.value = 50
			self.reloadList()
		else:
			ConfigListScreen.keyNumberGlobal(self, 0)
		
	def reloadList(self):
		self.refresh()
		self["config"].setList(self.list)	
	
	def refresh(self):		
		list = []
		list.extend((
			getConfigListEntry(_("3d mode"), self.mode),
			getConfigListEntry(_("Depth"), self.znorm),
			getConfigListEntry(_("Show in menu"), self.menuext),
			getConfigListEntry(_("Turn on automatically"), self.auto)
		))

		# Only allow editing toggle mode when the 3d switch command is supposed to apear in menu or 3d should be turned on automatically
		if self.menuext.value is not "none" or self.auto.value:
			list.append(getConfigListEntry(_("Toggle mode"), self.toggle))
			
		# Only allow editing user prompt when the 3d auto toggle is activated
		if self.auto.value:
			list.append(getConfigListEntry(_("Display 3D confirmation"), self.prompt))	

		self.list = list
	
	def initHelpTexts(self):
		self.helpDict = {
			self.mode: _("Choose 3D mode (Side by Side, Top And Bottom, Auto, Off)."),
			self.znorm: _("Set the depth of 3D effect. Press [0] for standard value."),
			self.menuext: _("Should quick toggle command be present in menu / extensions list?"),
			self.auto: _("Should the plugin turn on 3D mode automatically judging on the playing media title (3D in service or file name)?"),
			self.toggle: _("Define the mode to turn on 3D automatically or by quick toggle menu command [Side By Side] or [Top And Bottom]."),
			self.prompt: _("How long should 3D mode on confirmation be displayed (seconds). 0 for none."),
		}
	
	def updateHelp(self):
		cur = self["config"].getCurrent()
		if cur:
			self["help"].text = self.helpDict.get(cur[1], "")
	#channging mode or znorm is immediatelly previewed
	def setPreviewSettings(self, value):
		applySettings(self.mode.value, int(self.znorm.value) - 50)
	#setting are stored in enigma configuration file
	def keyGo(self):
		config.plugins.OSD3DSetup.mode.value = self.mode.value
		config.plugins.OSD3DSetup.znorm.value = int(self.znorm.value) - 50
		config.plugins.OSD3DSetup.menuext.value = self.menuext.value
		config.plugins.OSD3DSetup.auto.value = self.auto.value
		config.plugins.OSD3DSetup.toggle.value = self.toggle.value
		config.plugins.OSD3DSetup.prompt.value = self.prompt.value
		config.plugins.OSD3DSetup.save()
		#refresh menus to reflect current settings
		plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))		
		self.close()
	#roll-back changes - read settings from configuration
	def keyCancel(self):
		setConfiguredSettings()
		self.close()
	
class AutoToggle3D(Screen):
	#class for listening for service changing events to set 3D mode automatically
	Instance = None 
	OldServiceName = ""
	
	def __init__(self, session):		
		self.session = session
		Screen.__init__(self, session)
		#associate event tracker with class methods
		self.et = ServiceEventTracker(screen = self, eventmap = {iPlayableService.evUpdatedEventInfo: self.UpdInfo, iPlayableService.evUpdatedInfo: self.UpdInfo})		
		#read and apply settings stored in configuration file - enigma starts...
		setConfiguredSettings()
		#read current mode
		if config.plugins.OSD3DSetup.mode.value:
			self.CurrentMode = config.plugins.OSD3DSetup.mode.value
		else:
			self.CurrentMode = val_auto
		self.Confirming = False
		AutoToggle3D.Instance = self #set instance - only one should be running
	
	def UpdInfo(self):
		#react only when there is a change in service or service event and there are apropriate settings in configuration
		if config.plugins.OSD3DSetup.auto.value and self.session.nav.getCurrentlyPlayingServiceReference(): 
			CurrentService = self.session.nav.getCurrentService()
			Service = self.session.nav.getCurrentlyPlayingServiceReference()
			#check if there is a file being played
			if Service.getPath():
				import os
				ServiceName = os.path.basename(Service.getPath())
				extension = ServiceName.split('.')				
				extension = extension[-1].lower()
				if not EXTENSIONS.has_key(extension):
					ServiceName = ""
			#or a channel...
			else:
				ServiceName = ""
				ServiceName = ServiceReference(CurrentService.info().getInfoString(iServiceInformation.sServiceref)).getServiceName()
				hwnd = eServiceCenter.getInstance()
				ServRef = eServiceReference(CurrentService.info().getInfoString(iServiceInformation.sServiceref))
				info = hwnd.info(ServRef)				
				if info:
					evt = info.getEvent(ServRef)
					if evt: ServiceName = ServiceName + " " + evt.getEventName()			
				
				#self.session.open(MessageBox,_(ServiceName), type = MessageBox.TYPE_INFO, timeout = 5)
			
			if AutoToggle3D.OldServiceName != ServiceName:
				AutoToggle3D.OldServiceName = ServiceName
				#NewMode = self.CurrentMode
				# - if it contains "3D" string, switch 3D mode on				
				if ServiceName.upper().count("3D") > 0:
					if config.plugins.OSD3DSetup.prompt.value > 0:
						NewMode = nz(config.plugins.OSD3DSetup.toggle.value, val_auto)
						if self.CurrentMode != NewMode and self.Confirming == False:
							self.Confirming = True
							self.session.openWithCallback(self.setNewMode, InfoAuto3D, NewMode, self.Confirming)
					else:	
						if config.plugins.OSD3DSetup.toggle.value:
							NewMode = config.plugins.OSD3DSetup.toggle.value
						else:
							NewMode = val_sidebyside
				else:
					NewMode = val_auto
				self.setNewMode([NewMode, self.Confirming])
				
	def setNewMode(self, ret):
		if ret:	
			if ret[1] == False:
				self.Confirming = False
				if self.CurrentMode != ret[0]:
					self.CurrentMode = ret[0]
					setmode(ret[0])

class InfoAuto3D(Screen):
	skin = """
		<screen name="InfoAuto3D" position="c-345,c-320" size="700,100" backgroundColor="transparent" flags="wfNoBorder" title="Activate 3D mode">
		<widget name="infotext" position="c-350,e-100" size="690,40" halign="center" valign="center" font="Regular;20" backgroundColor="transparent" foregroundColor="#C8C8FF" shadowColor="#0000FF" />
	</screen>"""	
	Instance = None 
		
	def __init__(self, session, NewMode, Confirming):		
		self.skin = InfoAuto3D.skin
		Screen.__init__(self, session)		
		from Components.Label import Label
		from Components.ActionMap import ActionMap
		self["infotext"] = Label("Press blue button to activate 3D mode")
		self.blueTimer = eTimer()
		self.blueTimer.callback.append(self.autoclose)
		self["actions"] = ActionMap(["SetupActions", "ColorActions"],
		{
			"blue": self.keyBlue,
			"cancel": self.keyCancel
		}, -2)
		self.blueTimer.start(nz(config.plugins.OSD3DSetup.prompt.value,10) * 1000)
		InfoAuto3D.Instance = self #set instance - only one should be running
		
	def keyBlue(self):
		self.blueTimer.stop()
		self.close([config.plugins.OSD3DSetup.toggle.value, False])
	
	def autoclose(self):
		self.close([config.plugins.OSD3DSetup.mode.value, False])
		
	def keyCancel(self):
		self.blueTimer.stop()
		self.autoclose()
		
def nz(value, nullvalue) :
   if value is None: return nullvalue
   else: return value		
		
def applySettings(mode, znorm):
	setmode(mode)
	setznorm(znorm)

def setConfiguredSettings():
	applySettings(config.plugins.OSD3DSetup.mode.value, int(config.plugins.OSD3DSetup.znorm.value))

def getmode():
	file = open(path_mode, "r")
	if file:
		return file.readline().replace('\n','')
		file.close()
	else:
		return val_auto

def getznorm():
	file = open(path_znorm, "r")
	if file:
		return int(file.readline().replace('\n','').replace('%d',''))
		file.close()
	else:
		return val_auto
		
def setmode(val):
	if not val:
		val = val_auto
	try:
		file = open(path_mode, "w")
		file.write(val)
		file.close()
	except:
		return

def setznorm(val):
	if not val:
		val = 0
	try:
		file = open(path_znorm, "w")
		file.write('%d' % val)
		file.close()
	except:
		return		
		
#if there is a command in menu...	
def menu(menuid, **kwargs):
	if menuid == "mainmenu":
		if config.plugins.OSD3DSetup.toggle.value == val_sidebyside: 
			return [(_("3D ON/OFF (Side by Side)"), menutoggle3d, "Toggle 3D mode", 44)]
		else:
			return [(_("3D ON/OFF (Top And Bootom)"), menutoggle3d, "Toggle 3D mode", 44)]
	return []	
#show configuration screen...	
def main(session, **kwargs):
	session.open(OSD3DSetupScreen)

def startup(session, **kwargs):
	AutoToggle3D(session)

def menutoggle3d(session, **kwargs):
	mode = getmode()
	znorm = getznorm()
	toggle = config.plugins.OSD3DSetup.toggle.value
	if toggle is None:
		toggle = val_sidebyside
	if mode != toggle: #val_auto val_off or other not expected...
		setmode(toggle)
	else:
		setmode(val_auto) 
	if znorm < 0 or znorm > 100:
		setznorm(0)
	#if there is a toggle command in menu it would be nice to hide the menu - simulation of menu key pressing - to replace by direct menu hide command	
	try:
		eam = eActionMap.getInstance()
		#press the key with the desired flag
		eam.keyPressed(TYPE_STANDARD, 139, FLAG_MAKE) #menu
		#Release the key		
		eam.keyPressed(TYPE_STANDARD, 139, FLAG_BREAK) #menu
	except Exception, e:
		print "[OSD3D Setup] toggle3d exception:\n" + str(e)	
	return []	
	
#if there is a command in extensions selection...		
def toggleSBS(session, **kwargs):
	toggleext(val_sidebyside)
	return []

def toggleTAB(session, **kwargs):
	toggleext(val_topandbottom)
	return []
	
def toggleext(value):
 	mode = getmode()
	znorm = getznorm()
	if mode is None:
		mode = value
	if mode != value:
		setmode(value)
	else:
		setmode(val_auto) 
	if znorm < 0 or znorm > 100:
		setznorm(0)	
	
def Plugins(**kwargs):
	pluginlist = []
	from os import path
	menuext = config.plugins.OSD3DSetup.menuext.value
	auto = config.plugins.OSD3DSetup.auto.value
	if path.exists(path_mode):		
		if menuext == "menu" or menuext == "menuext":
			pluginlist.append(PluginDescriptor(name = "3D toggle ON/OFF", description = _("3D toggle ON/OFF"), where = PluginDescriptor.WHERE_MENU, needsRestart = False, fnc = menu))
		if menuext == "ext" or menuext == "menuext":
			pluginlist.append(PluginDescriptor(name = "3D ON/OFF (Side by Side)", description = _("3D ON/OFF (Side by Side)"), where = PluginDescriptor.WHERE_EXTENSIONSMENU, needsRestart = False, fnc = toggleSBS))
			pluginlist.append(PluginDescriptor(name = "3D ON/OFF (Top and Bottom)", description = _("3D ON/OFF (Top and Bottom)"), where = PluginDescriptor.WHERE_EXTENSIONSMENU, needsRestart = False, fnc = toggleTAB))
		pluginlist.append(PluginDescriptor(name = "OSD 3D setup", description = _("Adjust 3D settings"), where = PluginDescriptor.WHERE_PLUGINMENU, fnc = main))
		pluginlist.append(PluginDescriptor(name = "OSD 3D setup", description = "", where = PluginDescriptor.WHERE_SESSIONSTART, fnc = startup))
		return pluginlist		
	return pluginlist
