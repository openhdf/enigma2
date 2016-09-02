from os import path

from enigma import iPlayableService, iServiceInformation, eTimer, eServiceCenter, eServiceReference, eDVBDB

from Screens.Screen import Screen
from Screens.ChannelSelection import FLAG_IS_DEDICATED_3D
from Components.About import about
from Components.SystemInfo import SystemInfo
from Components.ConfigList import ConfigListScreen
from Components.config import config, configfile, getConfigListEntry
from Components.Label import Label
from Components.Sources.StaticText import StaticText
from Components.Pixmap import Pixmap
from Components.Sources.Boolean import Boolean
from Components.ServiceEventTracker import ServiceEventTracker
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
from Tools.HardwareInfo import HardwareInfo
from Components.AVSwitch import iAVSwitch

resolutionlabel = None

def getAutoresPlugin_enabled():
	try:
		return config.plugins.autoresolution.enable.value
	except:
		return False

class VideoSetup(Screen, ConfigListScreen):
	def __init__(self, session):
		Screen.__init__(self, session)
		# for the skin: first try VideoSetup, then Setup, this allows individual skinning
		self.skinName = ["VideoSetup", "Setup" ]
		self.setup_title = _("Video settings")
		self["HelpWindow"] = Pixmap()
		self["HelpWindow"].hide()
		self["VKeyIcon"] = Boolean(False)
		self['footnote'] = Label()

		self.hw = iAVSwitch
		self.onChangedEntry = [ ]

		# handle hotplug by re-creating setup
		self.onShow.append(self.startHotplug)
		self.onHide.append(self.stopHotplug)

		self.list = [ ]
		ConfigListScreen.__init__(self, self.list, session = session, on_change = self.changedEntry)

		from Components.ActionMap import ActionMap
		self["actions"] = ActionMap(["SetupActions", "MenuActions", "ColorActions"],
			{
				"cancel": self.keyCancel,
				"save": self.apply,
				"menu": self.closeRecursive,
			}, -2)

		self["key_red"] = StaticText(_("Cancel"))
		self["key_green"] = StaticText(_("OK"))
		self["description"] = Label("")

		config.av.autores_preview.value = False
		self.createSetup()
		self.grabLastGoodMode()
		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.setTitle(self.setup_title)

	def startHotplug(self):
		self.hw.on_hotplug.append(self.createSetup)

	def stopHotplug(self):
		self.hw.on_hotplug.remove(self.createSetup)

	def createSetup(self):
		level = config.usage.setup_level.index

		self.list = [
			getConfigListEntry(_("Video output"), config.av.videoport, _("Configures which video output connector will be used."))
		]
		if config.av.videoport.value in ('HDMI', 'YPbPr', 'Scart-YPbPr') and not getAutoresPlugin_enabled(): #path.exists(resolveFilename(SCOPE_PLUGINS)+'SystemPlugins/AutoResolution'):
			self.list.append(getConfigListEntry(_("Automatic resolution"), config.av.autores,_("If enabled the output resolution of the box will try to match the resolution of the video contents resolution")))
			if config.av.autores.value in ('all', 'hd'):
				self.list.append(getConfigListEntry(_("Delay time"), config.av.autores_delay,_("Set the time before checking video source for resolution infomation.")))
				self.list.append(getConfigListEntry(_("Force de-interlace"), config.av.autores_deinterlace,_("If enabled the video will always be de-interlaced.")))
				self.list.append(getConfigListEntry(_("Automatic resolution label"), config.av.autores_label_timeout,_("Allows you to adjust the amount of time the resolution infomation display on screen.")))
				if config.av.autores.value in 'hd':
					self.list.append(getConfigListEntry(_("Show SD as"), config.av.autores_sd,_("This option allows you to choose how to display standard defintion video on your TV.")))
				self.list.append(getConfigListEntry(_("Show 480/576p 24fps as"), config.av.autores_480p24,_("This option allows you to choose how to display SD progressive 24Hz on your TV. (as not all TV's support these resolutions)")))
				self.list.append(getConfigListEntry(_("Show 720p 24fps as"), config.av.autores_720p24,_("This option allows you to choose how to display 720p 24Hz on your TV. (as not all TV's support these resolutions)")))
				self.list.append(getConfigListEntry(_("Show 1080p 24fps as"), config.av.autores_1080p24,_("This option allows you to choose how to display 1080p 24Hz on your TV. (as not all TV's support these resolutions)")))
				self.list.append(getConfigListEntry(_("Show 1080p 25fps as"), config.av.autores_1080p25,_("This option allows you to choose how to display 1080p 25Hz on your TV. (as not all TV's support these resolutions)")))
				self.list.append(getConfigListEntry(_("Show 1080p 30fps as"), config.av.autores_1080p30,_("This option allows you to choose how to display 1080p 30Hz on your TV. (as not all TV's support these resolutions)")))
				self.list.append(getConfigListEntry(_('Always use smart1080p mode'), config.av.smart1080p, _("This option allows you to always use e.g. 1080p50 for TV/.ts, and 1080p24/p50/p60 for videos")))
			elif config.av.autores.value == 'simple':
				prev_sd = prev_hd = prev_fhd = prev_uhd = ""
				service = self.session.nav.getCurrentService()
				info = service and service.info()
				if info:
					video_height = int(info.getInfo(iServiceInformation.sVideoHeight))
					if video_height <= 576:
						prev_sd = "* "
					elif video_height <= 720:
						prev_hd = "* "
					elif video_height <= 1080:
						prev_fhd = "* "
					elif video_height <= 2160:
						prev_uhd = "* "
					else:
						config.av.autores_preview.value = False
					self.list.append(getConfigListEntry(_("Enable preview"), config.av.autores_preview, _("Show preview of current mode (*)."), "check"))
				else:
					config.av.autores_preview.value = False
				self.list.append(getConfigListEntry(pgettext(_("Video output mode for SD"), _("%sMode for SD (up to 576p)") %prev_sd), config.av.autores_mode_sd[config.av.videoport.value], _("This option configures the video output mode (or resolution)."), "check"))
				self.list.append(getConfigListEntry(_("%sRefresh rate for SD") %prev_sd, config.av.autores_rate_sd[config.av.autores_mode_sd[config.av.videoport.value].value], _("Configure the refresh rate of the screen."), "check"))
				modelist = iAVSwitch.getModeList(config.av.videoport.value)
				if '720p' in iAVSwitch.modes_available:
					self.list.append(getConfigListEntry(pgettext(_("Video output mode for HD"), _("%sMode for HD (up to 720p)") %prev_hd), config.av.autores_mode_hd[config.av.videoport.value], _("This option configures the video output mode (or resolution)."), "check"))
					self.list.append(getConfigListEntry(_("%sRefresh rate for HD") %prev_hd, config.av.autores_rate_hd[config.av.autores_mode_hd[config.av.videoport.value].value], _("Configure the refresh rate of the screen."), "check"))
				if '1080i' in iAVSwitch.modes_available or '1080p' in iAVSwitch.modes_available:
					self.list.append(getConfigListEntry(pgettext(_("Video output mode for FHD"), _("%sMode for FHD (up to 1080p)") %prev_fhd), config.av.autores_mode_fhd[config.av.videoport.value], _("This option configures the video output mode (or resolution)."), "check"))
					self.list.append(getConfigListEntry(_("%sRefresh rate for FHD") %prev_fhd, config.av.autores_rate_fhd[config.av.autores_mode_fhd[config.av.videoport.value].value], _("Configure the refresh rate of the screen."), "check"))
					if config.av.autores_mode_fhd[config.av.videoport.value].value == '1080p' and ('1080p' in iAVSwitch.modes_available or '1080p50' in iAVSwitch.modes_available):
						self.list.append(getConfigListEntry(_("%sShow 1080i as 1080p") %prev_fhd, config.av.autores_1080i_deinterlace, _("Use Deinterlacing for 1080i Videosignal?"), "check"))
					elif not '1080p' in iAVSwitch.modes_available and not '1080p50' in iAVSwitch.modes_available:
						config.av.autores_1080i_deinterlace.setValue(False)
				if '2160p' in iAVSwitch.modes_available or '2160p30' in iAVSwitch.modes_available:
					self.list.append(getConfigListEntry(pgettext(_("Video output mode for UHD"), _("%sMode for UHD (up to 2160p)") %prev_uhd), config.av.autores_mode_uhd[config.av.videoport.value], _("This option configures the video output mode (or resolution)."), "check"))
					self.list.append(getConfigListEntry(_("%sRefresh rate for UHD") %prev_uhd, config.av.autores_rate_uhd[config.av.autores_mode_uhd[config.av.videoport.value].value], _("Configure the refresh rate of the screen."), "check"))
				self.list.append(getConfigListEntry(_("Delay time"), config.av.autores_delay,_("Set the time before checking video source for resolution infomation.")))
				self.list.append(getConfigListEntry(_("Automatic resolution label"), config.av.autores_label_timeout,_("Allows you to adjust the amount of time the resolution infomation display on screen.")))

		# if we have modes for this port:
		if (config.av.videoport.value in config.av.videomode and config.av.autores.value == 'disabled') or config.av.videoport.value == 'Scart':
			# add mode- and rate-selection:
			self.list.append(getConfigListEntry(pgettext("Video output mode", "Mode"), config.av.videomode[config.av.videoport.value], _("This option configures the video output mode (or resolution).")))
			if config.av.videomode[config.av.videoport.value].value == 'PC':
				self.list.append(getConfigListEntry(_("Resolution"), config.av.videorate[config.av.videomode[config.av.videoport.value].value], _("This option configures the screen resolution in PC output mode.")))
			elif config.av.videoport.value != 'Scart':
				self.list.append(getConfigListEntry(_("Refresh rate"), config.av.videorate[config.av.videomode[config.av.videoport.value].value], _("Configure the refresh rate of the screen.")))

		port = config.av.videoport.value
		if port not in config.av.videomode:
			mode = None
		else:
			mode = config.av.videomode[port].value

		# some modes (720p, 1080i) are always widescreen. Don't let the user select something here, "auto" is not what he wants.
		force_wide = self.hw.isWidescreenMode(port, mode)

		if not force_wide:
		 	self.list.append(getConfigListEntry(_("Aspect ratio"), config.av.aspect, _("Configure the aspect ratio of the screen.")))

		if force_wide or config.av.aspect.value in ("16:9", "16:10"):
			self.list.extend((
				getConfigListEntry(_("Display 4:3 content as"), config.av.policy_43, _("When the content has an aspect ratio of 4:3, choose whether to scale/stretch the picture.")),
				getConfigListEntry(_("Display >16:9 content as"), config.av.policy_169, _("When the content has an aspect ratio of 16:9, choose whether to scale/stretch the picture."))
			))
		elif config.av.aspect.value == "4:3":
			self.list.append(getConfigListEntry(_("Display 16:9 content as"), config.av.policy_169, _("When the content has an aspect ratio of 16:9, choose whether to scale/stretch the picture.")))

#		if config.av.videoport.value == "HDMI":
#			self.list.append(getConfigListEntry(_("Allow unsupported modes"), config.av.edid_override))
		if config.av.videoport.value == "Scart":
			self.list.append(getConfigListEntry(_("Color format"), config.av.colorformat, _("Configure which color format should be used on the SCART output.")))
			if level >= 1:
				self.list.append(getConfigListEntry(_("WSS on 4:3"), config.av.wss, _("When enabled, content with an aspect ratio of 4:3 will be stretched to fit the screen.")))
				if SystemInfo["ScartSwitch"]:
					self.list.append(getConfigListEntry(_("Auto scart switching"), config.av.vcrswitch, _("When enabled, your receiver will detect activity on the VCR SCART input.")))

#		if not isinstance(config.av.scaler_sharpness, ConfigNothing):
#			self.list.append(getConfigListEntry(_("Scaler sharpness"), config.av.scaler_sharpness, _("This option configures the picture sharpness.")))

		if SystemInfo["havecolorspace"]:
			self.list.append(getConfigListEntry(_("HDMI Colorspace"), config.av.hdmicolorspace,_("This option allows you can config the Colorspace from Auto to RGB")))

		if SystemInfo["Canedidchecking"]:
			self.list.append(getConfigListEntry(_("Bypass HDMI EDID Check"), config.av.bypass_edid_checking,_("This option allows you to bypass HDMI EDID check")))

		self["config"].list = self.list
		self["config"].l.setList(self.list)
		if config.usage.sort_settings.value:
			self["config"].list.sort()

	def keyLeft(self):
		ConfigListScreen.keyLeft(self)
		self.createSetup()

	def keyRight(self):
		ConfigListScreen.keyRight(self)
		self.createSetup()

	def confirm(self, confirmed):
		if not confirmed:
			config.av.videoport.setValue(self.last_good[0])
			config.av.videomode[self.last_good[0]].setValue(self.last_good[1])
			config.av.videorate[self.last_good[1]].setValue(self.last_good[2])
			config.av.autores_sd.setValue(self.last_good_extra[0])
			config.av.smart1080p.setValue(self.last_good_extra[1])
			self.hw.setMode(*self.last_good)
		else:
			self.keySave()

	def grabLastGoodMode(self):
		port = config.av.videoport.value
		mode = config.av.videomode[port].value
		rate = config.av.videorate[mode].value
		self.last_good = (port, mode, rate)
		autores_sd = config.av.autores_sd.value
		smart1080p = config.av.smart1080p.value
		self.last_good_extra = (autores_sd, smart1080p)

	def saveAll(self):
		if config.av.videoport.value == 'Scart':
			config.av.autores.setValue('disabled')
		for x in self["config"].list:
			x[1].save()
		configfile.save()

	def apply(self):
		port = config.av.videoport.value
		mode = config.av.videomode[port].value
		rate = config.av.videorate[mode].value
		autores_sd = config.av.autores_sd.value
		smart1080p = config.av.smart1080p.value
		if ((port, mode, rate) != self.last_good) or (autores_sd, smart1080p) != self.last_good_extra:
			if autores_sd.find('1080') >= 0:
				self.hw.setMode(port, '1080p', '50Hz')
			elif (smart1080p == '1080p50') or (smart1080p == 'true'): # for compatibility with old ConfigEnableDisable
				self.hw.setMode(port, '1080p', '50Hz')
			elif smart1080p == '2160p50':
				self.hw.setMode(port, '2160p', '50Hz')
			elif smart1080p == '1080i50':
				self.hw.setMode(port, '1080i', '50Hz')
			elif smart1080p == '720p50':
				self.hw.setMode(port, '720p', '50Hz')
			else:
				self.hw.setMode(port, mode, rate)
			from Screens.MessageBox import MessageBox
			self.session.openWithCallback(self.confirm, MessageBox, _("Is this video mode ok?"), MessageBox.TYPE_YESNO, timeout = 20, default = False)
		else:
			self.keySave()

	# for summary:
	def changedEntry(self):
		for x in self.onChangedEntry:
			x()
		if config.av.autores_preview.value:
			cur = self["config"].getCurrent()
			cur = cur and len(cur) > 3 and cur[3]
			if cur == "check":
				AutoVideoMode(None).VideoChangeDetect()

	def getCurrentEntry(self):
		return self["config"].getCurrent()[0]

	def getCurrentValue(self):
		return str(self["config"].getCurrent()[1].getText())

	def getCurrentDescription(self):
		return self["config"].getCurrent() and len(self["config"].getCurrent()) > 2 and self["config"].getCurrent()[2] or ""

	def createSummary(self):
		from Screens.Setup import SetupSummary
		return SetupSummary

class AudioSetup(Screen, ConfigListScreen):
	def __init__(self, session):
		Screen.__init__(self, session)
		# for the skin: first try AudioSetup, then Setup, this allows individual skinning
		self.skinName = ["AudioSetup", "Setup" ]
		self.setup_title = _("Audio settings")
		self["HelpWindow"] = Pixmap()
		self["HelpWindow"].hide()
		self["VKeyIcon"] = Boolean(False)
		self['footnote'] = Label()

		self.hw = iAVSwitch
		self.onChangedEntry = [ ]

		# handle hotplug by re-creating setup
		self.onShow.append(self.startHotplug)
		self.onHide.append(self.stopHotplug)

		self.list = [ ]
		ConfigListScreen.__init__(self, self.list, session = session, on_change = self.changedEntry)

		from Components.ActionMap import ActionMap
		self["actions"] = ActionMap(["SetupActions", "MenuActions", "ColorActions"],
			{
				"cancel": self.keyCancel,
				"save": self.apply,
				"menu": self.closeRecursive,
			}, -2)

		self["key_red"] = StaticText(_("Cancel"))
		self["key_green"] = StaticText(_("OK"))
		self["description"] = Label("")

		self.createSetup()
		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.setTitle(self.setup_title)

	def startHotplug(self):
		self.hw.on_hotplug.append(self.createSetup)

	def stopHotplug(self):
		self.hw.on_hotplug.remove(self.createSetup)

	def createSetup(self):
		level = config.usage.setup_level.index

		self.list = [ ]

		if level >= 1:
			if SystemInfo["HasMultichannelPCM"]:
				self.list.append(getConfigListEntry(_("Multichannel as PCM"), config.av.pcm_multichannel, _("Choose whether multi channel sound tracks should be output as PCM.")))
			if SystemInfo["CanDownmixAC3"]:
				self.list.append(getConfigListEntry(_("Dolby Digital / DTS downmix"), config.av.downmix_ac3, _("Choose whether multi channel sound tracks should be downmixed to stereo.")))
			if SystemInfo["CanDownmixAAC"]:
				self.list.append(getConfigListEntry(_("AAC downmix"), config.av.downmix_aac, _("Choose whether multi channel sound tracks should be downmixed to stereo.")))
			if SystemInfo["Canaudiosource"]:
				self.list.append(getConfigListEntry(_("Audio Source"), config.av.audio_source, _("Choose whether multi channel sound tracks should be convert to PCM or SPDIF.")))
			if SystemInfo["CanAACTranscode"]:
				self.list.append(getConfigListEntry(_("AAC transcoding"), config.av.transcodeaac, _("Choose whether AAC sound tracks should be transcoded.")))
			self.list.extend((
				getConfigListEntry(_("General AC3 delay"), config.av.generalAC3delay, _("This option configures the general audio delay of Dolby Digital sound tracks.")),
				getConfigListEntry(_("General PCM delay"), config.av.generalPCMdelay, _("This option configures the general audio delay of stereo sound tracks.")),
				getConfigListEntry(_("Volume adjust slow"), config.usage.volume_step_slow, _("Step value for single press the volume button. Depending on the setting (if greater) and the current volume (if less) will adjusted the step. (30 to 4, 18 to 3, 9 to 2 and 3 to 1)")),
				getConfigListEntry(_("Volume adjust fast"), config.usage.volume_step_fast, _("Step value for fast switching or long press the volume button. Depending on the setting (if greater) and the current volume (if less) will adjusted the step. (30 to 4, 18 to 3, 9 to 2 and 3 to 1)"))
			))

			if SystemInfo["Can3DSurround"]:
				self.list.append(getConfigListEntry(_("3D Surround"), config.av.surround_3d,_("This option allows you to enable 3D Surround Sound for an output.")))

			if SystemInfo["Can3DSpeaker"] and config.av.surround_3d.value != "none":
				self.list.append(getConfigListEntry(_("3D Surround Speaker Position"), config.av.surround_3d_speaker,_("This option allows you to change the virtuell loadspeaker position.")))

			if SystemInfo["CanAutoVolume"]:
				self.list.append(getConfigListEntry(_("Auto Volume Level"), config.av.autovolume,_("This option configures output for Auto Volume Level.")))

		self["config"].list = self.list
		self["config"].l.setList(self.list)
		if config.usage.sort_settings.value:
			self["config"].list.sort()

	def keyLeft(self):
		ConfigListScreen.keyLeft(self)
		self.createSetup()

	def keyRight(self):
		ConfigListScreen.keyRight(self)
		self.createSetup()

	def confirm(self, confirmed):
		self.keySave()

	def apply(self):
		self.keySave()

	# for summary:
	def changedEntry(self):
		for x in self.onChangedEntry:
			x()

	def getCurrentEntry(self):
		return self["config"].getCurrent()[0]

	def getCurrentValue(self):
		return str(self["config"].getCurrent()[1].getText())

	def getCurrentDescription(self):
		return self["config"].getCurrent() and len(self["config"].getCurrent()) > 2 and self["config"].getCurrent()[2] or ""

	def createSummary(self):
		from Screens.Setup import SetupSummary
		return SetupSummary

class AutoVideoModeLabel(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)

		self["content"] = Label()
		self["restxt"] = Label()

		self.hideTimer = eTimer()
		self.hideTimer.callback.append(self.hide)

		self.onShow.append(self.hide_me)

	def hide_me(self):
		idx = config.av.autores_label_timeout.index
		if idx:
			idx += 4
			self.hideTimer.start(idx*1000, True)

class AutoVideoMode(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)

		if session == None:
			self.firstrun = False
		else:
			self.firstrun = True
			self.__event_tracker = ServiceEventTracker(screen=self, eventmap=
				{
					iPlayableService.evStart: self.__evStart,
					iPlayableService.evVideoSizeChanged: self.VideoChanged,
					iPlayableService.evVideoProgressiveChanged: self.VideoChanged,
					iPlayableService.evVideoFramerateChanged: self.VideoChanged,
					iPlayableService.evBuffering: self.BufferInfo,
					iPlayableService.evStopped: self.BufferInfoStop
				})

		self.delay = False
		self.bufferfull = True
		self.detecttimer = eTimer()
		self.detecttimer.callback.append(self.VideoChangeDetect)

	def checkIfDedicated3D(self):
			service = self.session.nav.getCurrentlyPlayingServiceReference()
			servicepath = service and service.getPath()
			if servicepath and servicepath.startswith("/"):
					if service.toString().startswith("1:"):
						info = eServiceCenter.getInstance().info(service)
						service = info and info.getInfoString(service, iServiceInformation.sServiceref)
						return service and eDVBDB.getInstance().getFlag(eServiceReference(service)) & FLAG_IS_DEDICATED_3D == FLAG_IS_DEDICATED_3D and "sidebyside"
					else:
						return ".3d." in servicepath.lower() and "sidebyside" or ".tab." in servicepath.lower() and "topandbottom"
			service = self.session.nav.getCurrentService()
			info = service and service.info()
			return info and info.getInfo(iServiceInformation.sIsDedicated3D) == 1 and "sidebyside"

	def __evStart(self):
		if config.osd.threeDmode.value == "auto":
			global isDedicated3D
			isDedicated3D = self.checkIfDedicated3D()
			if isDedicated3D:
				applySettings(isDedicated3D)
			else:
				applySettings()

	def BufferInfo(self):
		bufferInfo = self.session.nav.getCurrentService().streamed().getBufferCharge()
		if bufferInfo[0] > 98:
			self.bufferfull = True
			self.VideoChanged()
		else:
			self.bufferfull = False

	def BufferInfoStop(self):
		self.bufferfull = True

	def VideoChanged(self):
		if getAutoresPlugin_enabled():
			print "[VideoMode] autoresolution plugin is enabled - internal autoresolution canceled !"
			return
		if self.session.nav.getCurrentlyPlayingServiceReference() and not self.session.nav.getCurrentlyPlayingServiceReference().toString().startswith('4097:'):
			delay = config.av.autores_delay.value
		else:
			delay = config.av.autores_delay.value * 2
		if not self.detecttimer.isActive() and not self.delay:
			self.delay = True
			self.detecttimer.start(delay)
		else:
			self.delay = True
			self.detecttimer.stop()
			self.detecttimer.start(delay)

	def VideoChangeDetect(self):
		global resolutionlabel
		config_port = config.av.videoport.value
		config_mode = str(config.av.videomode[config_port].value).replace('\n','')
		config_res = str(config.av.videomode[config_port].value[:-1]).replace('\n','')
		config_pol = str(config.av.videomode[config_port].value[-1:]).replace('\n','')
		config_rate = str(config.av.videorate[config_mode].value).replace('Hz','').replace('\n','')

		f = open("/proc/stb/video/videomode")
		current_mode = f.read()[:-1].replace('\n','')
		f.close()
		if current_mode.upper() in ('PAL', 'NTSC'):
			current_mode = current_mode.upper()

		current_pol = ''
		if 'i' in current_mode:
			current_pol = 'i'
		elif 'p' in current_mode:
			current_pol = 'p'
		current_res = current_pol and current_mode.split(current_pol)[0].replace('\n','') or ""
		current_rate = current_pol and current_mode.split(current_pol)[0].replace('\n','') and current_mode.split(current_pol)[1].replace('\n','') or ""

		video_height = None
		video_width = None
		video_pol = None
		video_rate = None
		if path.exists("/proc/stb/vmpeg/0/yres"):
			try:
				f = open("/proc/stb/vmpeg/0/yres", "r")
				video_height = int(f.read(),16)
				f.close()
			except:
				video_height = 0
		if path.exists("/proc/stb/vmpeg/0/xres"):
			try:
				f = open("/proc/stb/vmpeg/0/xres", "r")
				video_width = int(f.read(),16)
				f.close()
			except:
				video_width = 0
		if path.exists("/proc/stb/vmpeg/0/progressive"):
			try:
				f = open("/proc/stb/vmpeg/0/progressive", "r")
				video_pol = "p" if int(f.read(),16) else "i"
				f.close()
			except:
				video_pol = "i"
		if path.exists("/proc/stb/vmpeg/0/framerate"):
			f = open("/proc/stb/vmpeg/0/framerate", "r")
			try:
				video_rate = int(f.read())
			except:
				video_rate = 50
			f.close()

		if not video_height or not video_width or not video_pol or not video_rate:
			service = self.session.nav.getCurrentService()
			if service is not None:
				info = service.info()
			else:
				info = None

			if info:
				video_height = int(info.getInfo(iServiceInformation.sVideoHeight))
				video_width = int(info.getInfo(iServiceInformation.sVideoWidth))
				video_pol = ("i", "p")[info.getInfo(iServiceInformation.sProgressive)]
				video_rate = int(info.getInfo(iServiceInformation.sFrameRate))

		if (video_height and video_width and video_pol and video_rate) or (config.av.smart1080p.value != 'false'):
			resolutionlabel["content"].setText(_("Video content: %ix%i%s %iHz") % (video_width, video_height, video_pol, (video_rate + 500) / 1000))
			if video_height != -1:
				if video_height > 720 or video_width > 1280:
					new_res = "1080"
				elif (576 < video_height <= 720) or video_width > 1024:
					new_res = "720"
				elif (480 < video_height <= 576) or video_width > 720 or video_rate in (25000, 23976, 24000):
					new_res = "576"
				else:
					new_res = "480"
			else:
				new_res = config_res

			if video_rate != -1:
				if video_rate == 25000 and video_pol == 'i':
					new_rate = 50000
				elif video_rate == 59940 or (video_rate == 29970 and video_pol == 'i') or (video_rate == 29970 and video_pol == 'p' and config.av.autores.value == 'disabled'): 
					new_rate = 60000
				elif video_rate == 23976:
					new_rate = 24000
				elif video_rate == 29970:
					new_rate = 30000
				else:
					new_rate = video_rate
				new_rate = str((new_rate + 500) / 1000)
			else:
				new_rate = config_rate

			if video_pol != -1:
				new_pol = str(video_pol)
			else:
				new_pol = config_pol

			write_mode = None
			new_mode = None
			if config_mode in ('PAL', 'NTSC'):
				write_mode = config_mode
			elif config.av.autores.value == 'simple':
				new_rate = (video_rate + 500) / 1000
				if video_height <= 576: #sd
					if config.av.autores_rate_sd[config.av.autores_mode_sd[config.av.videoport.value].value].value == 'multi':
						if video_pol == 'i': new_rate *= 2
					else:
						new_rate = str(config.av.autores_rate_sd[config.av.autores_mode_sd[config.av.videoport.value].value].value).replace('Hz','').replace('\n','')
					new_mode = str(config.av.autores_mode_sd[config_port].value).replace('p30','p').replace('\n','')
				elif video_height <= 720: #hd
					if config.av.autores_rate_hd[config.av.autores_mode_hd[config.av.videoport.value].value].value == 'multi':
						if video_pol == 'i': new_rate *= 2
					else:
						new_rate = str(config.av.autores_rate_hd[config.av.autores_mode_hd[config.av.videoport.value].value].value).replace('Hz','').replace('\n','')
					new_mode = str(config.av.autores_mode_hd[config_port].value).replace('p30','p').replace('\n','')
				elif video_height <= 1080: #fhd
					if config.av.autores_rate_fhd[config.av.autores_mode_fhd[config.av.videoport.value].value].value == 'multi':
						if video_pol == 'i': new_rate *= 2
					else:
						new_rate = str(config.av.autores_rate_fhd[config.av.autores_mode_fhd[config.av.videoport.value].value].value).replace('Hz','').replace('\n','')
					new_mode = str(config.av.autores_mode_fhd[config_port].value).replace('p30','p').replace('\n','')
					if new_mode == '1080p' and not config.av.autores_1080i_deinterlace.value and video_height == 1080 and video_pol == 'i':
						new_mode = '1080i'
				elif video_height <= 2160: #uhd
					if config.av.autores_rate_uhd[config.av.autores_mode_uhd[config.av.videoport.value].value].value == 'multi':
						if video_pol == 'i': new_rate *= 2
					else:
						new_rate = str(config.av.autores_rate_uhd[config.av.autores_mode_uhd[config.av.videoport.value].value].value).replace('Hz','').replace('\n','')
					new_mode = str(config.av.autores_mode_uhd[config_port].value).replace('p30','p').replace('\n','')
				new_rate = str(new_rate)
				new_mode = str(new_mode)
				if new_mode+new_rate in iAVSwitch.modes_available:
					write_mode = new_mode+new_rate
				elif new_mode in iAVSwitch.modes_available:
					write_mode = new_mode
				#print "[VideoMode] simple mode, selecting ", write_mode
			elif config.av.autores.value == 'all' or (config.av.autores.value == 'hd' and int(new_res) >= 720):
				if (config.av.autores_deinterlace.value and HardwareInfo().is_nextgen()) or (config.av.autores_deinterlace.value and not HardwareInfo().is_nextgen() and int(new_res) <= 720):
					new_pol = new_pol.replace('i','p')
				if new_res+new_pol+new_rate in iAVSwitch.modes_available:
					new_mode = new_res+new_pol+new_rate
					if new_mode == '480p24' or new_mode == '576p24':
						new_mode = config.av.autores_480p24.value
					if new_mode == '720p24':
						new_mode = config.av.autores_720p24.value
					if new_mode == '1080p24':
						new_mode = config.av.autores_1080p24.value
					if new_mode == '1080p25':
						new_mode = config.av.autores_1080p25.value
					if new_mode == '1080p30':
						new_mode = config.av.autores_1080p30.value
				elif new_res+new_pol in iAVSwitch.modes_available:
					new_mode = new_res+new_pol
				else:
					new_mode = config_mode+new_rate

				write_mode = new_mode
			elif config.av.autores.value == 'hd' and int(new_res) <= 576:
				if (config.av.autores_deinterlace.value and HardwareInfo().is_nextgen()) or (config.av.autores_deinterlace.value and not HardwareInfo().is_nextgen() and not config.av.autores_sd.value == '1080i'):
					new_mode = config.av.autores_sd.value.replace('i','p')+new_rate
				else:
					if new_pol in 'p':
						new_mode = config.av.autores_sd.value.replace('i','p')+new_rate
					else:
						new_mode = config.av.autores_sd.value+new_rate

				if new_mode == '720p24':
					new_mode = config.av.autores_720p24.value
				if new_mode == '1080p24':
					new_mode = config.av.autores_1080p24.value
				if new_mode == '1080p25':
					new_mode = config.av.autores_1080p25.value
				if new_mode == '1080p30':
					new_mode = config.av.autores_1080p30.value

				write_mode = new_mode
			else:
				if path.exists('/proc/stb/video/videomode_%shz' % new_rate) and config_rate == 'multi':
					f = open("/proc/stb/video/videomode_%shz" % new_rate, "r")
					multi_videomode = f.read().replace('\n','')
					f.close()
					if multi_videomode and (current_mode != multi_videomode):
						write_mode = multi_videomode
					else:
						write_mode = config_mode+new_rate

			# workaround for bug, see http://www.opena.tv/forum/showthread.php?1642-Autoresolution-Plugin&p=38836&viewfull=1#post38836
			# always use a fixed resolution and frame rate   (e.g. 1080p50 if supported) for TV or .ts files
			# always use a fixed resolution and correct rate (e.g. 1080p24/p50/p60 for all other videos
			if config.av.smart1080p.value != 'false' and config.av.autores.value != 'disabled' and config.av.autores.value != 'simple':
				ref = self.session.nav.getCurrentlyPlayingServiceReference()
				if ref is not None:
					try:
						mypath = ref.getPath()
					except:
						mypath = ''
				else:
					mypath = ''
				# no frame rate information available, check if filename (or directory name) contains a hint
				# (allow user to force a frame rate this way):
				if   (mypath.find('p24.') >= 0) or (mypath.find('24p.') >= 0):
					new_rate = '24'
				elif (mypath.find('p25.') >= 0) or (mypath.find('25p.') >= 0):
					new_rate = '25'
				elif (mypath.find('p30.') >= 0) or (mypath.find('30p.') >= 0):
					new_rate = '30'
				elif (mypath.find('p50.') >= 0) or (mypath.find('50p.') >= 0):
					new_rate = '50'
				elif (mypath.find('p60.') >= 0) or (mypath.find('60p.') >= 0):
					new_rate = '60'
				elif new_rate == 'multi':
					new_rate = '' # omit frame rate specifier, e.g. '1080p' instead of '1080p50' if there is no clue
				if mypath != '':
					if mypath.endswith('.ts'):
						print "DEBUG VIDEOMODE/ playing .ts file"
						new_rate = '50' # for .ts files
					else:
						print "DEBUG VIDEOMODE/ playing other (non .ts) file"
						# new_rate from above for all other videos
				else:
					print "DEBUG VIDEOMODE/ no path or no service reference, presumably live TV"
					new_rate = '50' # for TV / or no service reference, then stay at 1080p50
				
				new_rate = new_rate.replace('25', '50')
				new_rate = new_rate.replace('30', '60')
				
				if  (config.av.smart1080p.value == '1080p50') or (config.av.smart1080p.value == 'true'): # for compatibility with old ConfigEnableDisable
					write_mode = '1080p' + new_rate
				elif config.av.smart1080p.value == '2160p50':
					write_mode = '2160p' + new_rate
				elif config.av.smart1080p.value == '1080i50':
					if new_rate == '24':
						write_mode = '1080p24' # instead of 1080i24
					else:
						write_mode = '1080i' + new_rate
				elif config.av.smart1080p.value == '720p50':
					write_mode = '720p' + new_rate
				print "[VideoMode] smart1080p mode, selecting ",write_mode

			if write_mode and current_mode != write_mode and self.bufferfull:
				# first we read now the real available values for every stb,
				# before we try to write the new mode
				self.firstrun = False
				changeResolution = False
				try:
					if path.exists("/proc/stb/video/videomode_choices"):
						vf = open("/proc/stb/video/videomode_choices")
						values = vf.readline().replace("\n", "").split(" ", -1)
						for x in values:
							if x == write_mode:
								try:
									f = open("/proc/stb/video/videomode", "w")
									f.write(write_mode)
									f.close()
									changeResolution = True
								except Exception, e:
									print("[VideoMode] write_mode exception:" + str(e))

						if not changeResolution:
							print "[VideoMode] setMode - port: %s, mode: %s is not available" % (config_port, write_mode)
							resolutionlabel["restxt"].setText(_("Video mode: %s not available") % write_mode)
							# we try to go for not available 1080p24/1080p30/1080p60 to change to 1080p from 60hz_choices if available
							# TODO: can we make it easier, or more important --> smaller ?
							# should we outsourced that way, like two new "def ..."
							# or some other stuff, not like this?
							if (write_mode == "1080p24") or (write_mode == "1080p30") or (write_mode == "1080p60"):
								for x in values:
									if x == "1080p":
										try:
											f = open("/proc/stb/video/videomode", "w")
											f.write(x)
											f.close()
											changeResolution = True
										except Exception, e:
											print("[VideoMode] write_mode exception:" + str(e))
								if not changeResolution:
									print "[VideoMode] setMode - port: %s, mode: 1080p is also not available" % config_port
									resolutionlabel["restxt"].setText(_("Video mode: 1080p also not available"))
								else:
									print "[VideoMode] setMode - port: %s, mode: 1080p" % config_port
									resolutionlabel["restxt"].setText(_("Video mode: 1080p"))
							if (write_mode == "2160p24") or (write_mode == "2160p30") or (write_mode == "2160p60"):
								for x in values:
									if x == "2160p":
										try:
											f = open("/proc/stb/video/videomode", "w")
											f.write(x)
											f.close()
											changeResolution = True
										except Exception, e:
											print("[VideoMode] write_mode exception:" + str(e))
								if not changeResolution:
									print "[VideoMode] setMode - port: %s, mode: 2160p is also not available" % config_port
									resolutionlabel["restxt"].setText(_("Video mode: 2160p also not available"))
								else:
									print "[VideoMode] setMode - port: %s, mode: %s" % (config_port, x)
									resolutionlabel["restxt"].setText(_("Video mode: %s") % x)
						else:
							resolutionlabel["restxt"].setText(_("Video mode: %s") % write_mode)
							print "[VideoMode] setMode - port: %s, mode: %s" % (config_port, write_mode)
						if config.av.autores.value != "disabled" and config.av.autores_label_timeout.value != '0':
							resolutionlabel.show()
						vf.close()
				except Exception, e:
					print("[VideoMode] read videomode_choices exception:" + str(e))
			elif write_mode and current_mode != write_mode:
				print "[VideoMode] not changing from",current_mode,"to",write_mode,"as self.bufferfull is",self.bufferfull

		iAVSwitch.setAspect(config.av.aspect)
		iAVSwitch.setWss(config.av.wss)
		iAVSwitch.setPolicy43(config.av.policy_43)
		iAVSwitch.setPolicy169(config.av.policy_169)

		self.delay = False
		self.detecttimer.stop()

def autostart(session):
	global resolutionlabel
	if not getAutoresPlugin_enabled(): #path.exists(resolveFilename(SCOPE_PLUGINS)+'SystemPlugins/AutoResolution'):
		if resolutionlabel is None:
			resolutionlabel = session.instantiateDialog(AutoVideoModeLabel)
		AutoVideoMode(session)
	else:
		config.av.autores.setValue(False)
		config.av.autores.save()
		configfile.save()
