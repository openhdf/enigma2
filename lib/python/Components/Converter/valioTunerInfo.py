# -*- coding: iso-8859-1 -*-
#
#    SmartInfo-Converter for Dreambox/Enigma-2
#    Version: 1.0
#    Coded by Vali (c)2009-2011
#
#######################################################################



from enigma import iServiceInformation
from Components.Converter.Converter import Converter
from Components.Element import cached



class valioTunerInfo(Converter, object):
	def __init__(self, type):
		Converter.__init__(self, type)
		self.ar_fec = ["Auto", "1/2", "2/3", "3/4", "5/6", "7/8", "8/9", "3/5", "4/5", "9/10","None","None","None","None","None"]
		self.ar_pol = ["H", "V", "CL", "CR", "na", "na", "na", "na", "na", "na", "na", "na"]



	@cached
	
	def getText(self):
		service = self.source.service
		info = service and service.info()
		if not info:
			return ""	
		Ret_Text = ""
		if True:
			feinfo = (service and service.frontendInfo())
			if (feinfo is not None):
				frontendData = (feinfo and feinfo.getAll(True))
				if (frontendData is not None):
					if ((frontendData.get("tuner_type") == "DVB-S") or (frontendData.get("tuner_type") == "DVB-C")):
						frequency = str(int(frontendData.get("frequency") / 1000))
						symbolrate = str(int(frontendData.get("symbol_rate")) / 1000)
						try:
							if (frontendData.get("tuner_type") == "DVB-S"):
								polarisation_i = frontendData.get("polarization")
							else:
								polarisation_i = 0
							fec_i = frontendData.get("fec_inner")
							Ret_Text = frequency + "  " + self.ar_pol[polarisation_i] + "  " + self.ar_fec[fec_i] + "  " + symbolrate
						except:
							Ret_Text = "FQ:" + frequency + "  SR:" + symbolrate 
					elif (frontendData.get("tuner_type") == "DVB-T"):
						frequency = str((frontendData.get("frequency") / 1000)) + " MHz"
						Ret_Text = "Freq: " + frequency
			return Ret_Text
		return "n/a"
		

	text = property(getText)

	def changed(self, what):
		Converter.changed(self, what)