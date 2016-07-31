#######################################################################
#
#    Channel Number Renderer for Dreambox/Enigma-2
#    Version: 1.0
#    Coded by Vali (c)2010
#
#######################################################################

from Components.VariableText import VariableText
from enigma import eLabel, eServiceCenter
from Renderer import Renderer
from Screens.InfoBar import InfoBar

MYCHANSEL = InfoBar.instance.servicelist

class valioChannel(Renderer, VariableText):
	def __init__(self):
		Renderer.__init__(self)
		VariableText.__init__(self)
	GUI_WIDGET = eLabel
	
	def changed(self, what):
		#if not self.suspended:
		if True:
			service = self.source.service
			info = service and service.info()
			if info is None:
				self.text = " "
				return
			markersOffset = 0
			myRoot = MYCHANSEL.getRoot()
			mySrv = MYCHANSEL.servicelist.getCurrent()
			chx = MYCHANSEL.servicelist.l.lookupService(mySrv)
			if not MYCHANSEL.inBouquet():
				pass
			else:
				serviceHandler = eServiceCenter.getInstance()
				mySSS = serviceHandler.list(myRoot)
				SRVList = mySSS and mySSS.getContent("SN", True)
				for i in range(len(SRVList)):
					if chx == i:
						break
					testlinet = SRVList[i]
					testline = testlinet[0].split(":")
					if testline[1] == "64":
						markersOffset = markersOffset + 1
			chx = (chx - markersOffset) + 1
			rx = MYCHANSEL.getBouquetNumOffset(myRoot)
			name = info.getName()
			name.replace('\xc2\x86', '').replace('\xc2\x87', '')
			self.text = str(chx + rx)+". "+name

