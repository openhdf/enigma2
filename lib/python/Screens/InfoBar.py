from Tools.Profile import profile
from Tools.BoundFunction import boundFunction

# workaround for required config entry dependencies.
import Screens.MovieSelection
from Components.PluginComponent import plugins
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.Label import Label
from Components.Pixmap import MultiPixmap
from Tools.Directories import fileExists

profile("LOAD:enigma")
import enigma
import os
from boxbranding import getBoxType, getMachineBrand,getBrandOEM

boxtype = getBoxType()

profile("LOAD:InfoBarGenerics")
from Screens.InfoBarGenerics import InfoBarShowHide, \
	InfoBarNumberZap, InfoBarChannelSelection, InfoBarMenu, InfoBarRdsDecoder, InfoBarRedButton, InfoBarTimerButton, InfoBarVmodeButton, \
	InfoBarEPG, InfoBarSeek, InfoBarInstantRecord, InfoBarResolutionSelection, InfoBarAspectSelection, \
	InfoBarAudioSelection, InfoBarAdditionalInfo, InfoBarNotifications, InfoBarDish, InfoBarUnhandledKey, InfoBarLongKeyDetection, \
	InfoBarSubserviceSelection, InfoBarShowMovies, \
	InfoBarServiceNotifications, InfoBarPVRState, InfoBarCueSheetSupport, InfoBarSimpleEventView, InfoBarBuffer, \
	InfoBarSummarySupport, InfoBarMoviePlayerSummarySupport, InfoBarTimeshiftState, InfoBarTeletextPlugin, InfoBarExtensions, InfoBarSleepTimer, \
	InfoBarSubtitleSupport, InfoBarPiP, InfoBarPlugins, InfoBarServiceErrorPopupSupport, InfoBarJobman, InfoBarQuickMenu, InfoBarZoom, InfoBarHdmi, \
	setResumePoint, delResumePoint
from Screens.Hotkey import InfoBarHotkey

profile("LOAD:InitBar_Components")
from Components.ActionMap import HelpableActionMap
from Components.Timeshift import InfoBarTimeshift
from Components.config import config
from Components.ServiceEventTracker import ServiceEventTracker, InfoBarBase

profile("LOAD:HelpableScreen")
from Screens.HelpMenu import HelpableScreen

class InfoBar(InfoBarBase, InfoBarShowHide,
	InfoBarNumberZap, InfoBarChannelSelection, InfoBarMenu, InfoBarEPG, InfoBarRdsDecoder,
	InfoBarInstantRecord, InfoBarAudioSelection, InfoBarRedButton, InfoBarTimerButton, InfoBarResolutionSelection, InfoBarAspectSelection, InfoBarVmodeButton,
	HelpableScreen, InfoBarAdditionalInfo, InfoBarNotifications, InfoBarDish, InfoBarUnhandledKey, InfoBarLongKeyDetection,
	InfoBarSubserviceSelection, InfoBarTimeshift, InfoBarSeek, InfoBarCueSheetSupport, InfoBarSleepTimer,
	InfoBarSummarySupport, InfoBarTimeshiftState, InfoBarTeletextPlugin, InfoBarExtensions, InfoBarBuffer,
	InfoBarPiP, InfoBarPlugins, InfoBarSubtitleSupport, InfoBarServiceErrorPopupSupport, InfoBarJobman, InfoBarQuickMenu, InfoBarZoom, InfoBarHdmi,
	Screen, InfoBarHotkey):

	ALLOW_SUSPEND = True
	instance = None

	def __init__(self, session):
		Screen.__init__(self, session)
		self["actions"] = HelpableActionMap(self, "InfobarActions",
			{
				"showMovies": (self.showMovies, _("Play recorded movies...")),
				"showRadio": (self.showRadio, _("Show the radio player...")),
				"showTv": (self.TvRadioToggle, _("Show the tv player...")),
				"showMediaPlayer": (self.showMediaPlayer, _("Show the media player...")),
				"openBouquetList": (self.openBouquetList, _("open bouquetlist")),
				"openSleepTimer": (self.openPowerTimerList, _("Show the Sleep Timer...")),
				"showEMC": (self.showEMC, _("Show the media center...")),
				"showETPORTAL": (self.showETPORTAL, _("Open EtPortal...")),
				"showMEDIAPORTAL": (self.showMEDIAPORTAL, _("Open MediaPortal...")),
				"showWWW": (self.showWWW, _("Open WWW Plugin...")),
				"showPluginBrowser": (self.showPluginBrowser, _("Show the plugins...")),
				"showBoxPortal": (self.showBoxPortal, _("Show Box Portal...")),
			}, prio=2)

		self["key_red"] = Label()
		self["key_yellow"] = Label()
		self["key_blue"] = Label()
		self["key_green"] = Label()

		self.allowPiP = True
		self.radioTV = 0

		for x in HelpableScreen, \
				InfoBarBase, InfoBarShowHide, \
				InfoBarNumberZap, InfoBarChannelSelection, InfoBarMenu, InfoBarEPG, InfoBarRdsDecoder, \
				InfoBarInstantRecord, InfoBarAudioSelection, InfoBarRedButton, InfoBarTimerButton, InfoBarUnhandledKey, InfoBarLongKeyDetection, InfoBarResolutionSelection, InfoBarVmodeButton, \
				InfoBarAdditionalInfo, InfoBarNotifications, InfoBarDish, InfoBarSubserviceSelection, InfoBarAspectSelection, InfoBarBuffer, \
				InfoBarTimeshift, InfoBarSeek, InfoBarCueSheetSupport, InfoBarSummarySupport, InfoBarTimeshiftState, InfoBarSleepTimer, \
				InfoBarTeletextPlugin, InfoBarExtensions, InfoBarPiP, InfoBarSubtitleSupport, InfoBarJobman, InfoBarQuickMenu, InfoBarZoom, InfoBarHdmi, \
				InfoBarPlugins, InfoBarServiceErrorPopupSupport, InfoBarHotkey:
			x.__init__(self)

		self.helpList.append((self["actions"], "InfobarActions", [("showMovies", _("Watch recordings..."))]))
		self.helpList.append((self["actions"], "InfobarActions", [("showRadio", _("Listen to the radio..."))]))

		self.__event_tracker = ServiceEventTracker(screen=self, eventmap=
			{
				enigma.iPlayableService.evUpdatedEventInfo: self.__eventInfoChanged
			})

		self.current_begin_time=0
		assert InfoBar.instance is None, "class InfoBar is a singleton class and just one instance of this class is allowed!"
		InfoBar.instance = self
		self.zoomrate = 0
		self.zoomin = 1

		if config.misc.initialchannelselection.value:
			self.onShown.append(self.showMenu)

		self.onShow.append(self.doButtonsCheck)

	def showMenu(self):
		self.onShown.remove(self.showMenu)
		config.misc.initialchannelselection.value = False
		config.misc.initialchannelselection.save()
		self.mainMenu()

	def doButtonsCheck(self):
		if config.plisettings.ColouredButtons.value:
			self["key_yellow"].setText(_("Search"))

			if config.usage.defaultEPGType.value == "Graphical EPG..." or config.usage.defaultEPGType.value == "None":
				self["key_red"].setText(_("Single EPG"))
			else:
				self["key_red"].setText(_("ViX EPG"))

			if not config.plisettings.Subservice.value:
				self["key_green"].setText(_("Timers"))
			else:
				self["key_green"].setText(_("Subservices"))
		self["key_blue"].setText(_("Extensions"))

	def __onClose(self):
		InfoBar.instance = None

	def __eventInfoChanged(self):
		if self.execing:
			service = self.session.nav.getCurrentService()
			old_begin_time = self.current_begin_time
			info = service and service.info()
			ptr = info and info.getEvent(0)
			self.current_begin_time = ptr and ptr.getBeginTime() or 0
			if config.usage.show_infobar_on_event_change.value:
				if old_begin_time and old_begin_time != self.current_begin_time:
					self.doShow()

	def __checkServiceStarted(self):
		self.__serviceStarted(True)
		self.onExecBegin.remove(self.__checkServiceStarted)

	def serviceStarted(self):  #override from InfoBarShowHide
		new = self.servicelist.newServicePlayed()
		if self.execing:
			InfoBarShowHide.serviceStarted(self)
			self.current_begin_time=0
		elif not self.__checkServiceStarted in self.onShown and new:
			self.onShown.append(self.__checkServiceStarted)

	def __checkServiceStarted(self):
		self.serviceStarted()
		self.onShown.remove(self.__checkServiceStarted)

	def openBouquetList(self):
		if config.usage.tvradiobutton_mode.value == "MovieList":
			self.showTvChannelList(True)
			self.showMovies()
		elif config.usage.tvradiobutton_mode.value == "ChannelList":
			self.showTvChannelList(True)
		elif config.usage.tvradiobutton_mode.value == "BouquetList":
			self.showTvChannelList(True)
			self.servicelist.showFavourites()

	def showMediaPlayer(self):
		try:
			from Plugins.Extensions.MediaPlayer.plugin import MediaPlayer
			self.session.open(MediaPlayer)
			no_plugin = False
		except Exception, e:
			self.session.open(MessageBox, _("The MediaPlayer plugin is not installed!\nPlease install it."), type = MessageBox.TYPE_INFO,timeout = 10 )
			
	def showEMC(self):
		try:
			from Plugins.Extensions.EnhancedMovieCenter.plugin import *
			from Components.PluginComponent import plugins
			showMoviesNew()
		except Exception, e:
			self.session.open(MessageBox, _("The Enhanced Movie Center plugin is not installed!\nPlease install it."), type = MessageBox.TYPE_INFO,timeout = 10 )

	def showETPORTAL(self):
		try:
			from Plugins.Extensions.EtPortal.plugin import *
			from Components.PluginComponent import plugins
			self.session.open(EtPortalScreen)
		except Exception, e:
			self.session.open(MessageBox, _("The EtPortal plugin is not installed!\nPlease install it."), type = MessageBox.TYPE_INFO,timeout = 10 )

	def showMEDIAPORTAL(self):
		try:
			if config.mediaportal.ansicht.value == 'liste':
				from Plugins.Extensions.MediaPortal.plugin import MPList
				self.session.open(MPList)
			elif config.mediaportal.ansicht.value == 'wall':
				from Plugins.Extensions.MediaPortal.plugin import MPWall
				self.session.open(MPWall, config.mediaportal.filter.value)
			elif config.mediaportal.ansicht.value == 'wall2':
				from Plugins.Extensions.MediaPortal.plugin import MPWall2
				self.session.open(MPWall2, config.mediaportal.filter.value)
			else:
				from Plugins.Extensions.MediaPortal.plugin import MPList
				self.session.open(MPList)
			no_plugin = False
		except Exception, e:
			self.session.open(MessageBox, _("The MediaPortal plugin is not installed!\nPlease install it."), type = MessageBox.TYPE_INFO,timeout = 10 )

	def showWWW(self):
		try:
			from Plugins.Extensions.EtPortal.plugin import *
			from Components.PluginComponent import plugins
			self.session.open(EtPortalScreen)
		except Exception, e:
			self.session.open(MessageBox, _("The EtPortal plugin is not installed!\nPlease install it."), type = MessageBox.TYPE_INFO,timeout = 10 )

	def BackZap(self):
		if config.OpenWebif.enabled.value:
			try:
				os.system("wget -q -O /tmp/.message.txt 'http://127.0.0.1/web/remotecontrol?command=11' &  > /dev/null 2>&1")
			except Exception, e:
				self.session.open(MessageBox, _("The OpenWebinterface plugin is not installed or activated!\nPlease install or activate it."), type = MessageBox.TYPE_INFO,timeout = 10 )
		else:
			self.session.open(MessageBox, _("The OpenWebinterface plugin is not installed or activated!\nPlease install or activate it."), type = MessageBox.TYPE_INFO,timeout = 10 )

	def openSleepTimer(self):
		from Screens.SleepTimerEdit import SleepTimerEdit
		self.session.open(SleepTimerEdit)

	def openPowerTimerList(self):
		from Screens.PowerTimerEdit import PowerTimerEditList
		self.session.open(PowerTimerEditList)

	def showPluginBrowser(self):
		from Screens.PluginBrowser import PluginBrowser
		self.session.open(PluginBrowser)
		
	def showBoxPortal(self):
		if getMachineBrand() == 'GI' or boxtype.startswith('azbox') or boxtype.startswith('ini') or boxtype.startswith('venton'):
			try:
				from Plugins.Extensions.EtPortal.plugin import *
				from Components.PluginComponent import plugins
				self.session.open(EtPortalScreen)
			except Exception, e:
				self.session.open(MessageBox, _("The EtPortal plugin is not installed!\nPlease install it."), type = MessageBox.TYPE_INFO,timeout = 10 )
		else:
			self.showMovies()

	def TvRadioToggle(self):
		if getBoxType().startswith('gb') or boxtype == 'odinm7':
			self.toogleTvRadio()
		else:
			self.showTv()

	def toogleTvRadio(self):
		if self.radioTV == 1:
			self.radioTV = 0
			self.showTv()
		else:
			self.radioTV = 1
			self.showRadio()

	def showTv(self):
		if config.usage.tvradiobutton_mode.value == "MovieList":
			self.showTvChannelList(True)
			self.showMovies()
		elif config.usage.tvradiobutton_mode.value == "BouquetList":
			self.showTvChannelList(True)
			if config.usage.show_servicelist.value:
				self.servicelist.showFavourites()
		else:
			self.showTvChannelList(True)

	def showRadio(self):
		if config.usage.e1like_radio_mode.value:
			if config.usage.tvradiobutton_mode.value == "BouquetList":
				self.showRadioChannelList(True)
				if config.usage.show_servicelist.value:
					self.servicelist.showFavourites()
			else:
				self.showRadioChannelList(True)
		else:
			self.rds_display.hide() # in InfoBarRdsDecoder
			from Screens.ChannelSelection import ChannelSelectionRadio
			self.session.openWithCallback(self.ChannelSelectionRadioClosed, ChannelSelectionRadio, self)

	def ChannelSelectionRadioClosed(self, *arg):
		self.rds_display.show()  # in InfoBarRdsDecoder
		self.radioTV = 0
		self.doShow()

	def showMovies(self, defaultRef=None):
		self.lastservice = self.session.nav.getCurrentlyPlayingServiceOrGroup()
		if self.lastservice and ':0:/' in self.lastservice.toString():
			self.lastservice = enigma.eServiceReference(config.movielist.curentlyplayingservice.value)
		self.session.openWithCallback(self.movieSelected, Screens.MovieSelection.MovieSelection, defaultRef, timeshiftEnabled = self.timeshiftEnabled())

	def movieSelected(self, service):
		ref = self.lastservice
		del self.lastservice
		if service is None:
			if ref and not self.session.nav.getCurrentlyPlayingServiceOrGroup():
				self.session.nav.playService(ref)
		else:
			self.session.open(MoviePlayer, service, slist = self.servicelist, lastservice = ref)

	def showBoxPortal(self):
		if getMachineBrand() == 'GI' or boxtype.startswith('azbox') or boxtype.startswith('ini') or boxtype.startswith('venton'):
			from Screens.BoxPortal import BoxPortal
			self.session.open(BoxPortal)
		else:
			self.showMovies()

def setAudioTrack(service):
	try:
		from Tools.ISO639 import LanguageCodes as langC
		tracks = service and service.audioTracks()
		nTracks = tracks and tracks.getNumberOfTracks() or 0
		if not nTracks: return
		idx = 0
		trackList = []
		for i in xrange(nTracks):
			audioInfo = tracks.getTrackInfo(i)
			lang = audioInfo.getLanguage()
			if langC.has_key(lang):
				lang = langC[lang][0]
			desc = audioInfo.getDescription()
			track = idx, lang,  desc
			idx += 1
			trackList += [track]
		seltrack = tracks.getCurrentTrack()
		# we need default selected language from image
		# to set the audiotrack if "config.autolanguage.audio_autoselect...values" are not set
		from Components.Language import language
		syslang = language.getLanguage()[:2]
		syslang = langC[syslang][0]
		if (config.autolanguage.audio_autoselect1.value or config.autolanguage.audio_autoselect2.value or config.autolanguage.audio_autoselect3.value or config.autolanguage.audio_autoselect4.value) != "---":
			audiolang = [config.autolanguage.audio_autoselect1.value, config.autolanguage.audio_autoselect2.value, config.autolanguage.audio_autoselect3.value, config.autolanguage.audio_autoselect4.value]
			caudiolang = True
		else:
			audiolang = syslang
			caudiolang = False
		useAc3 = config.autolanguage.audio_defaultac3.value
		if useAc3:
			matchedAc3 = tryAudioTrack(tracks, audiolang, caudiolang, trackList, seltrack, useAc3)
			if matchedAc3: return
			matchedMpeg = tryAudioTrack(tracks, audiolang, caudiolang, trackList, seltrack, False)
			if matchedMpeg: return
			tracks.selectTrack(0)    # fallback to track 1(0)
			return
		else:
			matchedMpeg = tryAudioTrack(tracks, audiolang, caudiolang, trackList, seltrack, False)
			if matchedMpeg:	return
			matchedAc3 = tryAudioTrack(tracks, audiolang, caudiolang, trackList, seltrack, useAc3)
			if matchedAc3: return
			tracks.selectTrack(0)    # fallback to track 1(0)
	except Exception, e:
		print("[MoviePlayer] audioTrack exception:\n" + str(e))

def tryAudioTrack(tracks, audiolang, caudiolang, trackList, seltrack, useAc3):
	for entry in audiolang:
		if caudiolang:
			# we need here more replacing for other language, or new configs with another list !!!
			# choice gives only the value, never the description
			# so we can also make some changes in "config.py" to get the description too, then we dont need replacing here !
			entry = entry.replace('eng qaa Englisch', 'English').replace('deu ger', 'German')
		for x in trackList:
			if entry == x[1] and seltrack == x[0]:
				if useAc3:
					if x[2].startswith('AC'):
						print("[MoviePlayer] audio track is current selected track: " + str(x))
						return True
				else:
					print("[MoviePlayer] audio track is current selected track: " + str(x))
					return True
			elif entry == x[1] and seltrack != x[0]:
				if useAc3:
					if x[2].startswith('AC'):
						print("[MoviePlayer] audio track match: " + str(x))
						tracks.selectTrack(x[0])
						return True
				else:
					print("[MoviePlayer] audio track match: " + str(x))
					tracks.selectTrack(x[0])
					return True
	return False

class MoviePlayer(InfoBarBase, InfoBarShowHide, InfoBarLongKeyDetection, InfoBarMenu, InfoBarEPG, \
		InfoBarSeek, InfoBarShowMovies, InfoBarInstantRecord, InfoBarAudioSelection, HelpableScreen, InfoBarNotifications,
		InfoBarServiceNotifications, InfoBarPVRState, InfoBarCueSheetSupport, InfoBarSimpleEventView,
		InfoBarMoviePlayerSummarySupport, InfoBarSubtitleSupport, Screen, InfoBarTeletextPlugin, InfoBarAspectSelection,
		InfoBarServiceErrorPopupSupport, InfoBarExtensions, InfoBarPlugins, InfoBarPiP, InfoBarResolutionSelection, InfoBarZoom, InfoBarHotkey):

	ENABLE_RESUME_SUPPORT = True
	ALLOW_SUSPEND = True

	instance = None

	def __init__(self, session, service, slist = None, lastservice = None):
		Screen.__init__(self, session)
		InfoBarAspectSelection.__init__(self)
		InfoBarAudioSelection.__init__(self)
		InfoBarSimpleEventView.__init__(self)
		self.pts_pvrStateDialog = ""

		self["key_yellow"] = Label()
		self["key_blue"] = Label()
		self["key_green"] = Label()

		self["eventname"] = Label()
		self["state"] = Label()
		self["speed"] = Label()
		self["statusicon"] = MultiPixmap()

		self["actions"] = HelpableActionMap(self, "MoviePlayerActions",
			{
				"leavePlayer": (self.leavePlayer, _("leave movie player...")),
				"leavePlayerOnExit": (self.leavePlayerOnExit, _("leave movie player..."))
			})

		self.allowPiP = True

		for x in HelpableScreen, InfoBarShowHide, InfoBarLongKeyDetection, InfoBarMenu, InfoBarEPG, \
				InfoBarBase, InfoBarSeek, InfoBarShowMovies, InfoBarInstantRecord, \
				InfoBarAudioSelection, InfoBarNotifications, InfoBarSimpleEventView, \
				InfoBarServiceNotifications, InfoBarPVRState, InfoBarCueSheetSupport, \
				InfoBarMoviePlayerSummarySupport, InfoBarSubtitleSupport, \
				InfoBarTeletextPlugin, InfoBarServiceErrorPopupSupport, InfoBarExtensions, \
				InfoBarPlugins, InfoBarPiP, InfoBarZoom, InfoBarHotkey:
			x.__init__(self)

		self.onChangedEntry = [ ]
		self.servicelist = slist
		self.lastservice = lastservice or session.nav.getCurrentlyPlayingServiceOrGroup()
		session.nav.playService(service)
		self.cur_service = service
		self.returning = False
		self.onClose.append(self.__onClose)
		self.onShow.append(self.doButtonsCheck)

		self.__event_tracker = ServiceEventTracker(screen=self, eventmap=
			{
				enigma.iPlayableService.evStart: self.__evStart
			})

		assert MoviePlayer.instance is None, "class InfoBar is a singleton class and just one instance of this class is allowed!"
		MoviePlayer.instance = self

		# is needed for every first call of MoviePlayer
		self.__evStart()

	def __evStart(self):
		self.switchAudioTimer = enigma.eTimer()
		self.switchAudioTimer.callback.append(self.switchAudio)
		self.switchAudioTimer.start(750, True)    # 750 is a safe-value

	def switchAudio(self):
		service = self.session.nav.getCurrentlyPlayingServiceOrGroup()
		if service:
			# we go this way for other extensions as own records(they switch over pmt)
			path = service.getPath()
			import os
			ext = os.path.splitext(path)[1].lower()
			exts = [".mkv", ".avi", ".divx", ".mp4"]      # we need more extensions here ?
			if ext.lower() in exts:
				service = self.session.nav.getCurrentService()
				if service:
					setAudioTrack(service)

	def doButtonsCheck(self):
		if config.plisettings.ColouredButtons.value:
			self["key_yellow"].setText(_("Search"))
			self["key_green"].setText(_("Timers"))
		self["key_blue"].setText(_("Extensions"))

	def __onClose(self):
		MoviePlayer.instance = None
		from Screens.MovieSelection import playlist
		del playlist[:]
		Screens.InfoBar.InfoBar.instance.callServiceStarted()
		self.session.nav.playService(self.lastservice)
		config.usage.last_movie_played.value = self.cur_service.toString()
		config.usage.last_movie_played.save()

	def handleLeave(self, how):
		self.is_closing = True
		if how == "ask":
			if config.usage.setup_level.index < 2: # -expert
				list = (
					(_("Yes"), "quit"),
					(_("No"), "continue")
				)
			else:
				list = (
					(_("Yes"), "quit"),
					(_("Yes, returning to movie list"), "movielist"),
					(_("Yes, and delete this movie"), "quitanddelete"),
					(_("Yes, delete this movie and return to movie list"), "deleteandmovielist"),
					(_("No"), "continue"),
					(_("No, but restart from begin"), "restart")
				)

			from Screens.ChoiceBox import ChoiceBox
			self.session.openWithCallback(self.leavePlayerConfirmed, ChoiceBox, title=_("Stop playing this movie?"), list = list)
		else:
			self.leavePlayerConfirmed([True, how])

	def leavePlayer(self):
		setResumePoint(self.session)
		self.handleLeave(config.usage.on_movie_stop.value)

	def leavePlayerOnExit(self):
		if self.shown:
			self.hide()
		elif self.session.pipshown and "popup" in config.usage.pip_hideOnExit.value:
			if config.usage.pip_hideOnExit.value == "popup":
				self.session.openWithCallback(self.hidePipOnExitCallback, MessageBox, _("Disable Picture in Picture"), simple=True)
			else:
				self.hidePipOnExitCallback(True)
		elif config.usage.leave_movieplayer_onExit.value == "popup":
			self.session.openWithCallback(self.leavePlayerOnExitCallback, MessageBox, _("Exit movie player?"), simple=True)
		elif config.usage.leave_movieplayer_onExit.value == "without popup":
			self.leavePlayerOnExitCallback(True)
		elif config.usage.leave_movieplayer_onExit.value == "stop":
			self.leavePlayer()

	def leavePlayerOnExitCallback(self, answer):
		if answer:
			setResumePoint(self.session)
			self.handleLeave("quit")

	def hidePipOnExitCallback(self, answer):
		if answer:
			self.showPiP()

	def deleteConfirmed(self, answer):
		if answer:
			self.leavePlayerConfirmed((True, "quitanddeleteconfirmed"))

	def deleteAndMovielistConfirmed(self, answer):
		if answer:
			self.leavePlayerConfirmed((True, "deleteandmovielistconfirmed"))

	def movielistAgain(self):
		from Screens.MovieSelection import playlist
		del playlist[:]
		self.session.nav.playService(self.lastservice)
		self.leavePlayerConfirmed((True, "movielist"))

	def leavePlayerConfirmed(self, answer):
		answer = answer and answer[1]
		if answer is None:
			return
		if answer in ("quitanddelete", "quitanddeleteconfirmed", "deleteandmovielist", "deleteandmovielistconfirmed"):
			ref = self.session.nav.getCurrentlyPlayingServiceOrGroup()
			serviceHandler = enigma.eServiceCenter.getInstance()
			if answer in ("quitanddelete", "deleteandmovielist"):
				msg = ''
				if config.usage.movielist_trashcan.value:
					import Tools.Trashcan
					try:
						trash = Tools.Trashcan.createTrashFolder(ref.getPath())
						Screens.MovieSelection.moveServiceFiles(ref, trash)
						# Moved to trash, okay
						if answer == "quitanddelete":
							self.close()
						else:
							self.movielistAgain()
						return
					except Exception, e:
						print "[InfoBar] Failed to move to .Trash folder:", e
						msg = _("Cannot move to trash can") + "\n" + str(e) + "\n"
				info = serviceHandler.info(ref)
				name = info and info.getName(ref) or _("this recording")
				msg += _("Do you really want to delete %s?") % name
				if answer == "quitanddelete":
					self.session.openWithCallback(self.deleteConfirmed, MessageBox, msg)
				elif answer == "deleteandmovielist":
					self.session.openWithCallback(self.deleteAndMovielistConfirmed, MessageBox, msg)
				return

			elif answer in ("quitanddeleteconfirmed", "deleteandmovielistconfirmed"):
				offline = serviceHandler.offlineOperations(ref)
				if offline.deleteFromDisk(0):
					self.session.openWithCallback(self.close, MessageBox, _("You cannot delete this!"), MessageBox.TYPE_ERROR)
					if answer == "deleteandmovielistconfirmed":
						self.movielistAgain()
					return

		if answer in ("quit", "quitanddeleteconfirmed"):
			self.close()
		elif answer in ("movielist", "deleteandmovielistconfirmed"):
			if config.movielist.stop_service.value:
				ref = self.session.nav.getCurrentlyPlayingServiceOrGroup()
			else:
				ref = self.lastservice
			self.returning = True
			self.session.openWithCallback(self.movieSelected, Screens.MovieSelection.MovieSelection, ref)
			self.session.nav.stopService()
			if not config.movielist.stop_service.value:
				self.session.nav.playService(self.lastservice)
		elif answer == "restart":
			self.doSeek(0)
			self.setSeekState(self.SEEK_STATE_PLAY)
		elif answer in ("playlist","playlistquit","loop"):
			( next_service, item , length ) = self.getPlaylistServiceInfo(self.cur_service)
			if next_service is not None:
				if config.usage.next_movie_msg.value:
					self.displayPlayedName(next_service, item, length)
				self.session.nav.playService(next_service)
				self.cur_service = next_service
			else:
				if answer == "playlist":
					self.leavePlayerConfirmed([True,"movielist"])
				elif answer == "loop" and length > 0:
					self.leavePlayerConfirmed([True,"loop"])
				else:
					self.leavePlayerConfirmed([True,"quit"])
		elif answer in "repeatcurrent":
			if config.usage.next_movie_msg.value:
				(item, length) = self.getPlaylistServiceInfo(self.cur_service)
				self.displayPlayedName(self.cur_service, item, length)
			self.session.nav.stopService()
			self.session.nav.playService(self.cur_service)

	def doEofInternal(self, playing):
		if not self.execing:
			return
		if not playing :
			return
		ref = self.session.nav.getCurrentlyPlayingServiceOrGroup()
		if ref:
			delResumePoint(ref)
		self.handleLeave(config.usage.on_movie_eof.value)

	def up(self):
		slist = self.servicelist
		if slist and slist.dopipzap:
			if "keep" not in config.usage.servicelist_cursor_behavior.value:
				slist.moveUp()
			self.session.execDialog(slist)
		else:
			self.showMovies()

	def down(self):
		slist = self.servicelist
		if slist and slist.dopipzap:
			if "keep" not in config.usage.servicelist_cursor_behavior.value:
				slist.moveDown()
			self.session.execDialog(slist)
		else:
			self.showMovies()

	def right(self):
		# XXX: gross hack, we do not really seek if changing channel in pip :-)
		slist = self.servicelist
		if slist and slist.dopipzap:
			# XXX: We replicate InfoBarChannelSelection.zapDown here - we shouldn't do that
			if slist.inBouquet():
				prev = slist.getCurrentSelection()
				if prev:
					prev = prev.toString()
					while True:
						if config.usage.quickzap_bouquet_change.value and slist.atEnd():
							slist.nextBouquet()
						else:
							slist.moveDown()
						cur = slist.getCurrentSelection()
						if not cur or (not (cur.flags & 64)) or cur.toString() == prev:
							break
			else:
				slist.moveDown()
			slist.zap(enable_pipzap = True)
		else:
			InfoBarSeek.seekFwd(self)

	def left(self):
		slist = self.servicelist
		if slist and slist.dopipzap:
			# XXX: We replicate InfoBarChannelSelection.zapUp here - we shouldn't do that
			if slist.inBouquet():
				prev = slist.getCurrentSelection()
				if prev:
					prev = prev.toString()
					while True:
						if config.usage.quickzap_bouquet_change.value:
							if slist.atBegin():
								slist.prevBouquet()
						slist.moveUp()
						cur = slist.getCurrentSelection()
						if not cur or (not (cur.flags & 64)) or cur.toString() == prev:
							break
			else:
				slist.moveUp()
			slist.zap(enable_pipzap = True)
		else:
			InfoBarSeek.seekBack(self)

	def showPiP(self):
		slist = self.servicelist
		if self.session.pipshown:
			if slist and slist.dopipzap:
				slist.togglePipzap()
			if self.session.pipshown:
				del self.session.pip
				self.session.pipshown = False
		else:
			service = self.session.nav.getCurrentService()
			info = service and service.info()
			xres = str(info.getInfo(enigma.iServiceInformation.sVideoWidth))
			if int(xres) <= 720 or not getMachineBuild() == 'blackbox7405':  
				from Screens.PictureInPicture import PictureInPicture
				self.session.pip = self.session.instantiateDialog(PictureInPicture)
				self.session.pip.show()
				if self.session.pip.playService(slist.getCurrentSelection()):
					self.session.pipshown = True
					self.session.pip.servicePath = slist.getCurrentServicePath()
				else:
					self.session.pipshown = False
					del self.session.pip
			else:
				self.session.open(MessageBox, _("Your %s %s does not support PiP HD") % (getMachineBrand(), getMachineName()), type = MessageBox.TYPE_INFO,timeout = 5 )
				
	def movePiP(self):
		if self.session.pipshown:
			InfoBarPiP.movePiP(self)

	def swapPiP(self):
		pass

	def showMovies(self):
		ref = self.session.nav.getCurrentlyPlayingServiceOrGroup()
		if ref and ':0:/' not in ref.toString():
			self.playingservice = ref # movie list may change the currently playing
		else:
			self.playingservice = enigma.eServiceReference(config.movielist.curentlyplayingservice.value)
		self.session.openWithCallback(self.movieSelected, Screens.MovieSelection.MovieSelection, ref)

	def movieSelected(self, service):
		if service is not None:
			self.cur_service = service
			self.is_closing = False
			self.session.nav.playService(service)
			self.returning = False
		elif self.returning:
			self.close()
		else:
			self.is_closing = False
			try:
				ref = self.playingservice
				del self.playingservice
				# no selection? Continue where we left off
				if ref and not self.session.nav.getCurrentlyPlayingServiceOrGroup():
					self.session.nav.playService(ref)
			except:
				pass		

	def getPlaylistServiceInfo(self, service):
		from MovieSelection import playlist
		for i, item in enumerate(playlist):
			if item == service:
				if config.usage.on_movie_eof.value == "repeatcurrent":
					return i+1, len(playlist)
				i += 1
				if i < len(playlist):
					return playlist[i], i+1, len(playlist)
				elif config.usage.on_movie_eof.value == "loop":
					return playlist[0], 1, len(playlist)
		return None, 0, 0

	def displayPlayedName(self, ref, index, n):
		from Tools import Notifications
		Notifications.AddPopup(text = _("%s/%s: %s") % (index, n, self.ref2HumanName(ref)), type = MessageBox.TYPE_INFO, timeout = 5)

	def ref2HumanName(self, ref):
		return enigma.eServiceCenter.getInstance().info(ref).getName(ref)
