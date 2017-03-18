from enigma import eDVBVolumecontrol, eTimer
from Tools.Profile import profile
from Screens.Volume import Volume
from Screens.Mute import Mute
from GlobalActions import globalActionMap
from config import config, ConfigSubsection, ConfigInteger

profile("VolumeControl")
class VolumeControl:
	instance = None
	"""Volume control, handles volUp, volDown, volMute actions and display a corresponding dialog"""
	def __init__(self, session):
		global globalActionMap
		globalActionMap.actions["volumeUp"]=self.volUp
		globalActionMap.actions["volumeDown"]=self.volDown
		globalActionMap.actions["volumeMute"]=self.volMute

		assert not VolumeControl.instance, "only one VolumeControl instance is allowed!"
		VolumeControl.instance = self

		config.audio = ConfigSubsection()
		config.audio.volume = ConfigInteger(default = 50, limits = (0, 100))

		self.volumeDialog = session.instantiateDialog(Volume)
		self.volumeDialog.setAnimationMode(0)
		self.muteDialog = session.instantiateDialog(Mute)
		self.muteDialog.setAnimationMode(0)

		self.hideVolTimer = eTimer()
		self.hideVolTimer.callback.append(self.volHide)

		self.stepVolTimer = eTimer()
		self.repeat = 500
		self.delay = 3000

		vol = config.audio.volume.value
		self.volumeDialog.setValue(vol)
		self.volctrl = eDVBVolumecontrol.getInstance()
		self.volctrl.setVolume(vol, vol)

	def volSave(self):
		if self.volctrl.isMuted():
			config.audio.volume.setValue(0)
		else:
			config.audio.volume.setValue(self.volctrl.getVolume())
		config.audio.volume.save()

	def volUp(self):
		vol = self.volctrl.getVolume()
		step = self.stepVolume()
		if vol < 3:
			step = 1
		elif vol < 9:
			if step > 2: step = 2
		elif vol < 18:
			if step > 3: step = 3
		elif vol < 30:
			if step > 4: step = 4
		self.setVolume(vol+step)

	def volDown(self):
		vol = self.volctrl.getVolume()
		step = self.stepVolume()
		if vol <= 3:
			step = 1
		elif vol <= 9:
			if step > 2: step = 2
		elif vol <= 18:
			if step > 3: step = 3
		elif vol <= 30:
			if step > 4: step = 4
		self.setVolume(vol-step)

	def stepVolume(self):
		if self.stepVolTimer.isActive():
			step = config.usage.volume_step_fast.value
		else:
			self.getInputConfig()
			step = config.usage.volume_step_slow.value
		self.stepVolTimer.start(self.repeat,True)
		return step

	def getInputConfig(self):
		if self.hideVolTimer.isActive():
			return
		try:
			inputconfig = config.inputDevices.getSavedValue()
		except KeyError:
			return

		delay = 0
		repeat = 0

		for device in inputconfig.itervalues():
			if "enabled" in device and bool(device["enabled"]):
				if "delay" in device:
					val = int(device["delay"])
					if val > delay:
						delay = val
				if "repeat" in device:
					val = int(device["repeat"])
					if val > repeat:
						repeat = val

		if repeat + 100 > self.repeat:
			self.repeat = repeat + 100
		if delay + 100 > self.delay:
			self.delay = delay + 100

	def setVolume(self, newvol):
		self.volctrl.setVolume(newvol, newvol)
		is_muted = self.volctrl.isMuted()
		vol = self.volctrl.getVolume()
		self.volumeDialog.show()
		if is_muted:
			self.volMute() # unmute
		elif not vol:
			self.volMute(False, True) # mute but dont show mute symbol
		if self.volctrl.isMuted():
			self.volumeDialog.setValue(0)
		else:
			self.volumeDialog.setValue(self.volctrl.getVolume())
		self.volSave()
		self.hideVolTimer.start(self.delay, True)

	def volHide(self):
		self.volumeDialog.hide()

	def volMute(self, showMuteSymbol=True, force=False):
		vol = self.volctrl.getVolume()
		if vol or force:
			self.volctrl.volumeToggleMute()
			if self.volctrl.isMuted():
				if showMuteSymbol:
					self.muteDialog.show()
				self.volumeDialog.setValue(0)
			else:
				self.muteDialog.hide()
				self.volumeDialog.setValue(vol)
