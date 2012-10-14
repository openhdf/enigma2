from Plugins.Plugin import PluginDescriptor
from Components.PluginComponent import plugins
from Components.Label import Label
from Components.Pixmap import Pixmap
from enigma import ePicLoad, eTimer
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.InfoBarGenerics import InfoBarPlugins
from Tools.Directories import pathExists, resolveFilename
from Components.ActionMap import ActionMap
from Components.Sources.StaticText import StaticText
from Components.AVSwitch import AVSwitch
from Tools.Directories import fileExists, pathExists
from Components.ConfigList import ConfigListScreen
from Components.config import config, ConfigSubsection, ConfigBoolean, getConfigListEntry, ConfigYesNo
import keymapparser
import os
import os.path 

SHARED_DIR_PATH = '/usr/lib/enigma2/python/Plugins/Extensions/EtPortal/'

IMAGE_SIZE = 128
IMAGE_SIZE_S = 128
IMAGE_SIZE_XS = 128
IMAGE_SIZE_XXS = 128
IMAGE_SPACE = 30
BORDER_OFFSET_SIZE = 100
NUMBER_OF_PICTURES = 7

baseInfoBarPlugins__init__ = None
global_index = 0

config.plugins.EtPortal= ConfigSubsection()
config.plugins.EtPortal.finalexit = ConfigBoolean(default = False)
config.plugins.EtPortal.rememberposition = ConfigBoolean(default = True)
config.plugins.EtPortal.showtimericon = ConfigBoolean(default = True)
config.plugins.EtPortal.enablemarkbutton = ConfigYesNo(default = True)
config.plugins.EtPortal.adult = ConfigYesNo(default = False)
config.plugins.EtPortal.emc = ConfigYesNo(default = False)
config.plugins.EtPortal.dvd = ConfigYesNo(default = False)
config.plugins.EtPortal.lola = ConfigYesNo(default = True)
config.plugins.EtPortal.media = ConfigYesNo(default = True)
config.plugins.EtPortal.picture = ConfigYesNo(default = True)
config.plugins.EtPortal.mytube = ConfigYesNo(default = True)
config.plugins.EtPortal.etstreams = ConfigYesNo(default = True)
config.plugins.EtPortal.cinestream = ConfigYesNo(default = False)
config.plugins.EtPortal.burning = ConfigYesNo(default = False)
config.plugins.EtPortal.kinokiste = ConfigYesNo(default = False)
config.plugins.EtPortal.webmedia = ConfigYesNo(default = True)
config.plugins.EtPortal.moviestream = ConfigYesNo(default = False)
config.plugins.EtPortal.musicstream = ConfigYesNo(default = False)
config.plugins.EtPortal.loads7 = ConfigYesNo(default = False)
config.plugins.EtPortal.webbrowser = ConfigYesNo(default = True)
config.plugins.EtPortal.weather = ConfigYesNo(default = True)
config.plugins.EtPortal.weblinks = ConfigYesNo(default = True)
config.plugins.EtPortal.merlinmusic = ConfigYesNo(default = True)
config.plugins.EtPortal.foreca = ConfigYesNo(default = True)
config.plugins.EtPortal.onechannel = ConfigYesNo(default = False)
#config.plugins.EtPortal.extensions = ConfigYesNo(default = False)
#config.plugins.EtPortal.pluginbrowser = ConfigYesNo(default = False)
#config.plugins.EtPortal.shutdown = ConfigYesNo(default = False)

def writeToVFD(txt):
	oled = "/dev/dbox/oled0"
	if fileExists(oled):
		tmp = open(oled, "w")
		tmp.write(txt[:124])
		tmp.close()

class EtPortalScreen(Screen):
	def __init__(self, session):

		self.session = session
		self.textcolor = "#FFFFFF"
		self.color = "#30000000"

		skincontent = ""

		piclist = []
		piclist.append(('information.png', 'System information'))
		if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/DVDPlayer/keymap.xml") and config.plugins.EtPortal.dvd.value:
                        piclist.append(('dvd_player.png', 'DVD Player'))
                if fileExists("/usr/lib/enigma2/python/Screens/DVD.pyo") and config.plugins.EtPortal.dvd.value:
                        piclist.append(('dvd_player.png', 'DVD Player'))
                if config.plugins.EtPortal.media.value:
                        piclist.append(('media_player.png', 'Media Player'))
		if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/EnhancedMovieCenter/plugin.pyo") and config.plugins.EtPortal.emc.value:
		        piclist.append(('emc.png', 'EnhancedMovieCenter'))
                if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/PicturePlayer/ui.pyo") and config.plugins.EtPortal.picture.value:
                        piclist.append(('picture_player.png', 'Picture Player'))
                if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/MyTube/plugin.pyo") and config.plugins.EtPortal.mytube.value:
                        piclist.append(('mytube.png', 'My TubePlayer'))
                if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/EtStreams/plugin.pyo") and config.plugins.EtPortal.etstreams.value:
                        piclist.append(('etstreams.png', 'ET-Streams'))
                if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/cinestreamer/plugin.pyo") and config.plugins.EtPortal.cinestream.value:
                        piclist.append(('cinestream.png', 'CineStream'))
                if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/laola1tvlive/plugin.pyo") and config.plugins.EtPortal.lola.value:
                        piclist.append(('laolatv.png', 'laola1.tv'))
                if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/kinokiste/plugin.pyo") and config.plugins.EtPortal.kinokiste.value:
                        piclist.append(('kinokiste.png', 'KinoKiste'))
                if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/WebMedia/") and config.plugins.EtPortal.webmedia.value:
                        piclist.append(('webmedia.png', 'WebMedia'))
                if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/burnseries/plugin.pyo") and config.plugins.EtPortal.burning.value:
                        piclist.append(('burnseries.png', 'Burning-Series'))
                if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/moviestream/plugin.pyo") and config.plugins.EtPortal.moviestream.value:
                        piclist.append(('moviestream.png', 'MovieStream'))
                if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/musicstream/plugin.pyo") and config.plugins.EtPortal.musicstream.value:
                        piclist.append(('musicstream.png', 'MusicStream'))
                if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/loads7/plugin.pyo") and config.plugins.EtPortal.loads7.value:
                        piclist.append(('loads7.png', 'Loads7'))
                if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/WebBrowser/plugin.pyo") and config.plugins.EtPortal.webbrowser.value:
                        piclist.append(('opera.png', 'Web browser'))
		if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/msnWetter/plugin.pyo") and config.plugins.EtPortal.weather.value:
                        piclist.append(('wetter.png', 'msn Wetter'))
                if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/WebBrowser/weblinks.pyo") and config.plugins.EtPortal.weblinks.value:
                        piclist.append(('weblinks.png', 'Weblinks plugin'))
		if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/pornkiste/plugin.pyo") and config.plugins.EtPortal.adult.value:
			piclist.append(('pornkiste.png', 'PornKiste 18+'))
		if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/ePorner/plugin.pyo") and config.plugins.EtPortal.adult.value:
			piclist.append(('eporner.png', 'ePorner 18+'))
		if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/MerlinMusicPlayer/plugin.pyo") and config.plugins.EtPortal.merlinmusic.value:
			piclist.append(('merlinmusic.png', 'Merlin Music Player'))
		if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/Foreca/plugin.pyo") and config.plugins.EtPortal.foreca.value:
			piclist.append(('foreca.png', 'Foreca Weather'))
		if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/onechannel/plugin.pyo") and config.plugins.EtPortal.onechannel.value:
			piclist.append(('1channel.png', '1channel'))
                if config.plugins.EtPortal.showtimericon.value:
                        piclist.append(('timer.png', 'Timers for recordings'))
#                if config.plugins.EtPortal.movie.value:
                piclist.append(('movie_player.png', 'Movie Player'))
#		if config.plugins.EtPortal.extensions.value:
                piclist.append(('extensions_plugins.png', 'Extension Plugins and applications'))
#                if config.plugins.EtPortal.pluginbrowser.value:
                piclist.append(('plugins.png', 'Plugin Browser')) 
#		if config.plugins.EtPortal.shutdown.value:
                piclist.append(('shutdown.png', 'Sleeptimer and power control'))
		
		posX = 0
		hOffset = BORDER_OFFSET_SIZE
		for x in range(NUMBER_OF_PICTURES):
			if posX == 0 or posX == 6:
				tmpVoffset = 30
				tmpSize = IMAGE_SIZE_XXS
			elif posX == 1 or posX == 5:
				tmpVoffset = 20
				tmpSize = IMAGE_SIZE_XS
			elif posX == 2 or posX == 4:
				tmpVoffset = 10
				tmpSize = IMAGE_SIZE_S
			elif posX == 3:
				tmpVoffset = 0
				tmpSize = IMAGE_SIZE
			skincontent += "<widget name=\"thumb" + str(x) + "\" position=\"" + str(hOffset) + "," + str(tmpVoffset) + "\" size=\"" + str(tmpSize) + "," + str(tmpSize) + "\" zPosition=\"2\" transparent=\"1\" alphatest=\"on\" />"
			posX += 1
			if posX == 1:
				hOffset += (IMAGE_SIZE_XXS + IMAGE_SPACE)
			elif posX == 2 or posX == 6:
				hOffset += (IMAGE_SIZE_XS + IMAGE_SPACE)
			elif posX == 3 or posX == 5:
				hOffset += (IMAGE_SIZE_S + IMAGE_SPACE)
			elif posX == 4:
				hOffset += (IMAGE_SIZE + IMAGE_SPACE)

		self.skin = "<screen position=\"0,e-200\" size=\"e-0,200\" flags=\"wfNoBorder\" backgroundColor=\"transparent\" >"
		posX = 0
#		while posX < 32:
#			self.skin += "<eLabel position=\"0," + str(60 + posX) + "\" zPosition=\"0\" size=\"e-0,e-" + str(60 + posX) + "\" backgroundColor=\"#" +'%x' % (0xffffff - ((posX/2) * 0x111111)) + "\" />"
#			self.skin += "<eLabel position=\"0," + str(60 + posX) + "\" zPosition=\"0\" size=\"e-0,e-" + str(60 + posX) + "\" backgroundColor=\"" + self.color + "\" />"
#                        posX += 2
                self.skin += "<ePixmap pixmap=\"/usr/lib/enigma2/python/Plugins/Extensions/EtPortal/sel.png\" position=\"562,0\" size=\"150,130\" zPosition=\"2\" transparent=\"1\" alphatest=\"blend\" />"
                self.skin += "<eLabel position=\"0,75\" zPosition=\"0\" size=\"e-0,e-90\" backgroundColor=\"" + self.color + "\" />"  + skincontent
		self.skin += "<widget source=\"label\" render=\"Label\" position=\"0,148\" size=\"e-0,40\" halign=\"center\" font=\"Regular;30\" zPosition=\"2\" backgroundColor=\"#00000000\" transparent=\"1\" noWrap=\"1\" foregroundColor=\"" + self.textcolor + "\" />"
		self.skin += "</screen>"

		Screen.__init__(self, session)
		                                                        
		self["actions"] = ActionMap(["OkCancelActions", "DirectionActions", "EtPortalActions", "WizardActions", "EPGSelectActions"],
		{
			"cancel": self.keyExit,
			"ok": self.keyOk,
			"left": self.keyLeft,
			"right": self.keyRight,
			"up": self.keyLeft,
			"menu": self.keyMenu,
			"down": self.keyRight,
			"mark_button": self.keyExit,
		}, -1)

		for x in range(NUMBER_OF_PICTURES):
			self["thumb"+str(x)] = Pixmap()

		self["label"] = StaticText()

		self.Thumbnaillist = []
		self.filelist = []
		self.isWorking = False

		index = 0
		framePos = 0
		Page = 0
		for x in piclist:
			self.filelist.append((index, SHARED_DIR_PATH + x[0], x[1]))
			index += 1
			framePos += 1

		self.maxentry = len(self.filelist)-1

		if config.plugins.EtPortal.rememberposition.value:
			global global_index
			self.index = global_index
		else:
			self.index = 0

		self.picload = ePicLoad()
		self.picload.PictureData.get().append(self.showPic)
		self.onLayoutFinish.append(self.setPicloadConf)
		self.ThumbTimer = eTimer()
		self.ThumbTimer.callback.append(self.showPic)
		self.newPage()

	def setPicloadConf(self):
		sc = AVSwitch().getFramebufferScale()
		self.picload.setPara([IMAGE_SIZE_XXS, IMAGE_SIZE_XXS, sc[0], sc[1], False, 1, self.color])

	def newPage(self):
		self.Thumbnaillist = []
		for x in range(NUMBER_OF_PICTURES):
			self["thumb"+str(x)].hide()
		idx = 0
		offset = 0
		while idx < NUMBER_OF_PICTURES:
			if len(self.filelist) <= self.index + idx:
				self.Thumbnaillist.append([0, idx, self.filelist[offset][1], self.filelist[offset][2]])
				offset += 1
			else:
				self.Thumbnaillist.append([0, idx, self.filelist[offset + self.index][1], self.filelist[offset + self.index][2]])
				offset += 1
				if len(self.filelist) == self.index + offset:
					offset = 0
			idx += 1
		self.isWorking = True
		self.showPic()

	def showPic(self, picInfo=""):
		cnt = 0
		for x in range(NUMBER_OF_PICTURES):
			cnt += 1
			if self.Thumbnaillist[x][0] == 0:
				if self.picload.getThumbnail(self.Thumbnaillist[x][2]) == 1:
					self.ThumbTimer.start(500, True)
				else:
					self.Thumbnaillist[x][0] = 1
				break
			elif self.Thumbnaillist[x][0] == 1:
				self.Thumbnaillist[x][0] = 2
				ptr = self.picload.getData()
				if ptr != None:
					self["thumb" + str(self.Thumbnaillist[x][1])].instance.setPixmap(ptr.__deref__())
					sc = AVSwitch().getFramebufferScale()
					tmp = self.Thumbnaillist[x][1] + 1
					if  tmp == 3:
						self.picload.setPara([IMAGE_SIZE, IMAGE_SIZE, sc[0], sc[1], False, 1, self.color])
						
					elif tmp == 2 or tmp == 4:
						self.picload.setPara([IMAGE_SIZE_S, IMAGE_SIZE_S, sc[0], sc[1], False, 1, self.color])
						
					elif tmp == 1 or tmp == 5:
						self.picload.setPara([IMAGE_SIZE_XS, IMAGE_SIZE_XS, sc[0], sc[1], False, 1, self.color])
						
					else:
						self.picload.setPara([IMAGE_SIZE_XXS, IMAGE_SIZE_XXS, sc[0], sc[1], False, 1, self.color])
						
					self["thumb" + str(self.Thumbnaillist[x][1])].show()

			elif self.Thumbnaillist[x][0] == 2:
				if cnt == 6:
					self["label"].setText(self.Thumbnaillist[3][3])
					writeToVFD(self.Thumbnaillist[3][3])
					self.isWorking = False

	def keyLeft(self):
		if self.isWorking:
			return
		self.index -= 1
		if self.index < 0:
			self.index = self.maxentry
		self.newPage()
	
        def keyMenu(self):
		self.session.open(EtPortalSetupScreen)

	def keyRight(self):
		if self.isWorking:
			return
		self.index += 1
		if self.index > self.maxentry:
			self.index = 0
		self.newPage()

	def keyOk(self):
		if 'timer.png' in self.Thumbnaillist[3][2]:
			from Screens.TimerEdit import TimerEditList
			self.session.open(TimerEditList)
		elif 'shutdown.png' in self.Thumbnaillist[3][2]:
			from Screens.Menu import MainMenu
			import xml.etree.cElementTree
			menu = xml.etree.cElementTree.parse(SHARED_DIR_PATH + 'shutdown.xml').getroot()
			self.session.open(MainMenu, menu)
		elif 'information.png' in self.Thumbnaillist[3][2]:
			from Screens.Menu import MainMenu
			import xml.etree.cElementTree
			menu = xml.etree.cElementTree.parse(SHARED_DIR_PATH + 'information.xml').getroot()
			self.session.open(MainMenu, menu)
		elif 'movie_player.png' in self.Thumbnaillist[3][2]:
                        from Screens.InfoBar import InfoBar
                        if InfoBar and InfoBar.instance:
                                InfoBar.showMovies(InfoBar.instance)
		elif 'media_player.png' in self.Thumbnaillist[3][2]:
			if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/MediaPlayer/plugin.pyo"):
                                from Plugins.Extensions.MediaPlayer.plugin import MediaPlayer
                                self.session.open(MediaPlayer)
		elif 'wetter.png' in self.Thumbnaillist[3][2]:
			if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/msnWetter/plugin.pyo"):
                                from Plugins.Extensions.msnWetter.plugin import msnWetterMain
                                self.session.open(msnWetterMain)
		elif 'dvd_player.png' in self.Thumbnaillist[3][2]:
			if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/DVDPlayer/keymap.xml"):
				from Plugins.Extensions.DVDPlayer.plugin import DVDPlayer
				self.session.open(DVDPlayer)
                        if not fileExists("/usr/lib/enigma2/python/Plugins/Extensions/DVDPlayer/keymap.xml") and fileExists("/usr/lib/enigma2/python/Screens/DVD.pyo"):
                                from Screens import DVD
                                self.session.open(DVD.DVDPlayer)
	        elif 'webmedia.png' in self.Thumbnaillist[3][2]:    
	                if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/WebMedia/"):
                                from Plugins.Extensions.WebMedia.plugin import *
                                from Components.PluginComponent import plugins
                                plugin = _("WebMedia")
	                        for p in plugins.getPlugins(where = [PluginDescriptor.WHERE_EXTENSIONSMENU, PluginDescriptor.WHERE_PLUGINMENU]):
	                                if "WebMedia" == str(p.name):
	                                        plugin = p
	                        if plugin is not None:
                                        plugin(session=self.session)     
		elif 'emc.png' in self.Thumbnaillist[3][2]:       
                        if config.plugins.EtPortal.emc.value:
                                from Plugins.Extensions.EnhancedMovieCenter.plugin import *
	                        from Components.PluginComponent import plugins
                        	showMoviesNew()                                                                                  
                elif 'picture_player.png' in self.Thumbnaillist[3][2]:
                        if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/PicturePlayer/ui.pyo"):        
                                from Plugins.Extensions.PicturePlayer.ui import picshow
	                        self.session.open(picshow)
                elif 'mytube.png' in self.Thumbnaillist[3][2]:
                        if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/MyTube/plugin.pyo"):        
                                from Plugins.Extensions.MyTube.plugin import *
	                        l2key = True
                                self.session.open(MyTubePlayerMainScreen,l2key)
                elif 'etstreams.png' in self.Thumbnaillist[3][2]:
                        if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/EtStreams/plugin.pyo"):        
                                from Plugins.Extensions.EtStreams.plugin import *
                                self.session.open(EtStreams)
                elif 'cinestream.png' in self.Thumbnaillist[3][2]:
                        if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/cinestreamer/plugin.pyo"):        
                                from Plugins.Extensions.cinestreamer.plugin import *
	                        self.session.open(csmain, plugin_path)               
                elif 'laolatv.png' in self.Thumbnaillist[3][2]:
                        if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/laola1tvlive/plugin.pyo"):        
                                from Plugins.Extensions.laola1tvlive.plugin import *
	                        self.session.open(lola, plugin_path)
                elif 'kinokiste.png' in self.Thumbnaillist[3][2]:
                        if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/kinokiste/plugin.pyo"):        
                                from Plugins.Extensions.kinokiste.plugin import *
	                        self.session.open(kinokiste, plugin_path)                
                elif 'burnseries.png' in self.Thumbnaillist[3][2]:
                        if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/burnseries/plugin.pyo"):        
                                from Plugins.Extensions.burnseries.plugin import *
	                        self.session.open(burns, plugin_path)
                elif 'moviestream.png' in self.Thumbnaillist[3][2]:
                        if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/moviestream/plugin.pyo"):        
                                from Plugins.Extensions.moviestream.plugin import *
	                        self.session.open(moviestream, plugin_path)
                elif 'musicstream.png' in self.Thumbnaillist[3][2]:
                        if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/musicstream/plugin.pyo"):        
                                from Plugins.Extensions.musicstream.plugin import *
	                        self.session.open(ms, plugin_path)
                elif 'loads7.png' in self.Thumbnaillist[3][2]:
                        if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/loads7/plugin.pyo"):        
                                from Plugins.Extensions.loads7.plugin import *
	                        self.session.open(sieben_loads, plugin_path)
                elif 'merlinmusic.png' in self.Thumbnaillist[3][2]:
                        if config.plugins.EtPortal.merlinmusic.value:        
                                from Plugins.Extensions.MerlinMusicPlayer.plugin import *
                                servicelist = None
                                self.session.open(MerlinMusicPlayerFileList, servicelist)
                elif 'foreca.png' in self.Thumbnaillist[3][2]:
                        if config.plugins.EtPortal.foreca.value:        
                                from Plugins.Extensions.Foreca.plugin import *
	                        self.session.open(ForecaPreview)
                elif '1channel.png' in self.Thumbnaillist[3][2]:
                        if config.plugins.EtPortal.onechannel.value:        
                                from Plugins.Extensions.onechannel.plugin import * 
	                        action = "start"
                                value = 0 
                                self.session.open(MyMenux, action, value)
                elif 'pornkiste.png' in self.Thumbnaillist[3][2]:
                        if config.plugins.EtPortal.adult.value:        
                                from Plugins.Extensions.pornkiste.plugin import *
	                        self.session.open(pornkiste, plugin_path)
                elif 'eporner.png' in self.Thumbnaillist[3][2]:
                        if config.plugins.EtPortal.adult.value:        
                                from Plugins.Extensions.ePorner.plugin import *
	                        self.session.open(eporner, plugin_path)
                elif 'opera.png' in self.Thumbnaillist[3][2]:
			if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/WebBrowser/plugin.pyo"):
				from Plugins.Extensions.WebBrowser.plugin import BrowserRemoteControl
                        if config.plugins.WebBrowser.hasstartpage.value:
                                self.session.open(BrowserRemoteControl, config.plugins.WebBrowser.startpage.value, config.plugins.WebBrowser.startpagemode.value, config.plugins.WebBrowser.startpageagent.value, False)
	                else:
		                self.session.open(BrowserRemoteControl, '', False, False, True)
        	elif 'weblinks.png' in self.Thumbnaillist[3][2]:
			if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/WebBrowser/weblinks.pyo"):
				from Plugins.Extensions.WebBrowser.weblinks import WebLinksSelectMenu
				self.session.open(WebLinksSelectMenu)
		elif 'extensions_plugins.png' in self.Thumbnaillist[3][2]:
                        from Screens.InfoBar import InfoBar
                        if InfoBar and InfoBar.instance:
                                InfoBar.showExtensionSelection(InfoBar.instance)
                elif 'plugins.png' in self.Thumbnaillist[3][2]:
			from Screens.PluginBrowser import PluginBrowser
			self.session.open(PluginBrowser)
		if config.plugins.EtPortal.finalexit.value:
			self.close()

	def keyExit(self):                                                                         
		if config.plugins.EtPortal.rememberposition.value:
			global global_index
			global_index = self.index
		self.close()

class EtPortalSetupScreen(Screen, ConfigListScreen):
	skin = """
	<screen position="c-300,c-250" size="600,500" title="EtPortal config">
		<widget name="config" position="25,25" scrollbarMode="showOnDemand" size="550,300" />
		<ePixmap pixmap="skin_default/buttons/red.png" position="20,e-45" size="140,40" alphatest="on" />
		<ePixmap pixmap="skin_default/buttons/green.png" position="160,e-45" size="140,40" alphatest="on" />
		<widget source="key_red" render="Label" position="20,e-45" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
		<widget source="key_green" render="Label" position="160,e-45" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
	</screen>"""

	def __init__(self, session):
		self.skin = EtPortalSetupScreen.skin
		Screen.__init__(self, session)

		self["key_red"] = StaticText(_("Cancel"))
		self["key_green"] = StaticText(_("OK"))

		self["actions"] = ActionMap(["SetupActions", "ColorActions"],
		{
			"ok": self.keyGo,
			"save": self.keyGo,
			"cancel": self.keyCancel,
			"green": self.keyGo,
			"red": self.keyCancel,
		}, -2)

		self.list = []
		ConfigListScreen.__init__(self, self.list, session = self.session)
                self.list.append(getConfigListEntry(_("Exit portal after selecting an option"), config.plugins.EtPortal.finalexit))
		self.list.append(getConfigListEntry(_("Remember last menu position"), config.plugins.EtPortal.rememberposition))
		self.list.append(getConfigListEntry(_("Show timer option in menu"), config.plugins.EtPortal.showtimericon))
                self.list.append(getConfigListEntry(_("Enable Timer and Mark/Portal Button"), config.plugins.EtPortal.enablemarkbutton))
                self.list.append(getConfigListEntry(_("Show Adult-Content 18+"), config.plugins.EtPortal.adult))
                self.list.append(getConfigListEntry(_("Show EMC"), config.plugins.EtPortal.emc))
                self.list.append(getConfigListEntry(_("Show DVD-Player"), config.plugins.EtPortal.dvd))
                self.list.append(getConfigListEntry(_("Show Media-Player"), config.plugins.EtPortal.media))
                self.list.append(getConfigListEntry(_("Show Picture-Player"), config.plugins.EtPortal.picture))
                self.list.append(getConfigListEntry(_("Show MyTube"), config.plugins.EtPortal.mytube))
                self.list.append(getConfigListEntry(_("Show EtStreams"), config.plugins.EtPortal.etstreams))
                self.list.append(getConfigListEntry(_("Show CineStream"), config.plugins.EtPortal.cinestream))
                self.list.append(getConfigListEntry(_("Show Burning-Series"), config.plugins.EtPortal.burning))
                self.list.append(getConfigListEntry(_("Show KinoKiste"), config.plugins.EtPortal.kinokiste))
                self.list.append(getConfigListEntry(_("Show WebMedia"), config.plugins.EtPortal.webmedia))
                self.list.append(getConfigListEntry(_("Show Movie-Stream"), config.plugins.EtPortal.moviestream))
                self.list.append(getConfigListEntry(_("Show Music-Stream"), config.plugins.EtPortal.musicstream))
                self.list.append(getConfigListEntry(_("Show Loads7"), config.plugins.EtPortal.loads7))
                self.list.append(getConfigListEntry(_("Show WebBrowser"), config.plugins.EtPortal.webbrowser))
                self.list.append(getConfigListEntry(_("Show msn-Weather"), config.plugins.EtPortal.weather))
                self.list.append(getConfigListEntry(_("Show WebLinks"), config.plugins.EtPortal.weblinks))
                self.list.append(getConfigListEntry(_("Show Merlin-Music Player"), config.plugins.EtPortal.merlinmusic))
                self.list.append(getConfigListEntry(_("Show Foreca"), config.plugins.EtPortal.foreca))
                self.list.append(getConfigListEntry(_("Show 1channel"), config.plugins.EtPortal.onechannel))
                self.list.append(getConfigListEntry(_("Show laola1.tv"), config.plugins.EtPortal.lola))
#                self.list.append(getConfigListEntry(_("Show Extension Plugins and applications"), config.plugins.EtPortal.extensions))
#                self.list.append(getConfigListEntry(_("Show Plugin-Browser"), config.plugins.EtPortal.pluginbrowser))
#                self.list.append(getConfigListEntry(_("Show Sleeptimer and power control"), config.plugins.EtPortal.shutdown))
                self["config"].list = self.list
		self["config"].l.setList(self.list)
                
	def keyLeft(self):
		ConfigListScreen.keyLeft(self)

	def keyRight(self):
		ConfigListScreen.keyRight(self)

	def keyGo(self):
		for x in self["config"].list:
			x[1].save()	
                self.close()
                              
	def keyCancel(self):                                                     
		for x in self["config"].list:
			x[1].cancel()
		self.close()

def main(session, **kwargs):
	#session.open(EtPortalSetupScreen)
	session.open(EtPortalScreen)

def markButtonHook(self):
	self.session.open(EtPortalScreen)

def timerButtonHook(self):
	from Screens.TimerEdit import TimerEditList
	self.session.open(TimerEditList)

def InfoBarPlugins__init__(self):
        if config.plugins.EtPortal.enablemarkbutton.value:
		config.plugins.EtPortal.enablemarkbutton.setValue(True)
                self["EtPortalActions"] = ActionMap(["EtPortalActions"],
			{
				"mark_button": self.buttonHookMark,
				"timer_button": self.buttonHookTimer
				}, -1)
                                	
	global baseInfoBarPlugins__init__
	baseInfoBarPlugins__init__(self)

def autostart(reason, **kwargs):
	if "session" in kwargs:
		global baseInfoBarPlugins__init__
		baseInfoBarPlugins__init__ = InfoBarPlugins.__init__
		InfoBarPlugins.__init__ = InfoBarPlugins__init__
		if config.plugins.EtPortal.enablemarkbutton.value:
                       InfoBarPlugins.buttonHookMark = markButtonHook
                       InfoBarPlugins.buttonHookTimer = timerButtonHook
	
def Plugins(**kwargs):
	return [PluginDescriptor(where = PluginDescriptor.WHERE_SESSIONSTART, fnc = autostart), \
			PluginDescriptor(name = "ET-Portal config", description = "Configure your ET-Portal", where = PluginDescriptor.WHERE_PLUGINMENU, icon = "plugin.png",fnc = main),
			PluginDescriptor(name="ET-Portal", description="ET-Portal", where = PluginDescriptor.WHERE_EXTENSIONSMENU, fnc=main)]
