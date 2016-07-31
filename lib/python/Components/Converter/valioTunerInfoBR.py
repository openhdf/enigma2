# -*- coding: iso-8859-1 -*-
#
#    SmartInfo-Converter for Dreambox/Enigma-2
#    Version: 1.0
#    Coded by Vali (c)2009-2011
#
#######################################################################



from Components.Converter.Converter import Converter
from Components.Sources.bitratecalc import eBitrateCalculator
from Components.Element import cached
from enigma import eTimer, iServiceInformation
from Screens.InfoBar import InfoBar



class valioTunerInfoBR(Converter, object):
	def __init__(self, type):
		Converter.__init__(self, type)
		self.videoBitrate = None
		self.BRvalue="n/a"
		self.timerBR = eTimer()
		self.timerBR.callback.append(self.starthack)
		InfoBar.instance.onHide.append(self.hideNow)
		InfoBar.instance.onShow.append(self.showNow)



	@cached
	
	def getText(self):
		return "kbit/s: "+self.BRvalue

	text = property(getText)

	def changed(self, what):
		self.videoBitrate = None
		self.BRvalue="0"
		Converter.changed(self, "yes")
		if self.timerBR.isActive():
			self.timerBR.stop()
			self.timerBR.start(1000)
		else:
			self.timerBR.start(1000)

	def starthack(self):
		self.timerBR.stop()
		self.runBR()

	def runBR(self):
		ref = InfoBar.instance.session.nav.getCurrentlyPlayingServiceReference()
		if not ref:
			return
		service = InfoBar.instance.session.nav.getCurrentService()
		if service:
			serviceInfo = service.info()
			vpid = serviceInfo.getInfo(iServiceInformation.sVideoPID)
		if vpid:
			self.videoBitrate = eBitrateCalculator(vpid, ref.toString(), 1000, 1024*1024)
			self.videoBitrate.callback.append(self.updateInfos)

	def updateInfos(self, value, status):
		if status:
			self.BRvalue=str(value)
			Converter.changed(self, "yes")

	def showNow(self):
		self.timerBR.start(1000)

	def hideNow(self):
		if self.timerBR.isActive():
			self.timerBR.stop()
		self.videoBitrate = None
		self.BRvalue="0"
		Converter.changed(self, "yes")





